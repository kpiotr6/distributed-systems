import cmd, sys
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel 
from threading import Thread
import pickle

E_SEND = "exchange1"
E_RECV = "exchange2"

class RecieveThread(Thread):
    def __init__(self, queue, channel):
        super().__init__()
        self.channel: BlockingChannel = channel
        self.queue = queue
        self.stopped = False
    def stop(self):
        self.stopped = True
        
    def run(self):
        for msg in self.channel.consume(self.queue, inactivity_timeout=1):
            if self.stopped:
                break
            if msg == (None,None,None):
                continue
            print()
            print(msg[2].decode("utf-8"))
        self.channel.cancel()    
        
class AdminShell(cmd.Cmd):
    prompt = "Doctor >>> "
    def __init__(self, channel: Channel):
        super().__init__()
        self.channel: Channel  = channel
    
    def do_info(self, arg):
        sent_to_tech(self.doctor_name, 'knee', arg, self.channel)
        
    def do_exit(self, arg):
        self.close()

def sent_to_tech(doctor: str, exam: str, surname: str, channel: Channel):
    channel.basic_publish(exchange=E_SEND, routing_key=exam, body=pickle.dumps((exam, surname, doctor)))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Name not specified")
        exit(1)
    doctor_name = sys.argv[1]
    
    connection_send = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel_send = connection_send.channel()
    
    channel_send.exchange_declare(exchange=E_SEND, exchange_type="direct")
    
    connection_recv = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel_recv = connection_recv.channel()
    channel_recv.exchange_declare(exchange=E_RECV, exchange_type="direct")
    result = channel_recv.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel_recv.queue_bind(exchange=E_RECV, queue=queue_name, routing_key=doctor_name)
    tid = RecieveThread(queue_name, channel_recv)
    tid.start()
    
    try: 
        AdminShell(channel_send).cmdloop()
    except KeyboardInterrupt:
        tid.stop()
        tid.join()
        connection_send.close()
        connection_recv.close()
        pass
