import cmd, sys
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel 
from threading import Thread
import pickle

E_SEND = "exchange1"
E_RECV = "exchange2"
FROM_ADMIN = "exchange3"
TO_ADMIN = "exchange4"

doctor_name = ""

class RecieveThread(Thread):
    def __init__(self, queue, channel):
        super().__init__()
        self.channel: BlockingChannel = channel
        self.stopped = False
        self.queue = queue
    def stop(self):
        self.stopped = True
        
    def run(self):
        for msg in self.channel.consume(self.queue, inactivity_timeout=1, auto_ack=True):
            if self.stopped:
                break
            if msg == (None,None,None):
                continue
            print()
            print(msg[2].decode("utf-8"))
            self.channel.basic_publish(exchange="", routing_key=TO_ADMIN, body=bytes("From doctor "+doctor_name+": "+msg[2].decode("utf-8"), encoding="utf-8"))
        self.channel.cancel()    
        
class DoctShell(cmd.Cmd):
    prompt = "Doctor >>> "
    def __init__(self, channel: Channel, doctor_name: str):
        super().__init__()
        self.channel: Channel  = channel
        self.doctor_name: str = doctor_name
    
    def do_knee(self, arg):
        sent_to_tech(self.doctor_name, 'knee', arg, self.channel)
    
    def do_hip(self, arg):
        sent_to_tech(self.doctor_name, 'hip', arg, self.channel)
    
    def do_elbow(self, arg):
        sent_to_tech(self.doctor_name, 'elbow', arg, self.channel)
    
    def do_exit(self, arg):
        self.close()

def sent_to_tech(doctor: str, exam: str, surname: str, channel: Channel):
    channel.basic_publish(exchange=E_SEND, routing_key=exam, body=pickle.dumps((exam, surname, doctor)))
    channel.basic_publish(exchange="", routing_key=TO_ADMIN, body=bytes("From doctor "+doctor_name+": "+str((exam, surname, doctor)), encoding="utf-8"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Name not specified")
        exit(1)
    doctor_name = sys.argv[1]
    
    connection_send = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel_send = connection_send.channel()
    
    channel_send.exchange_declare(exchange=E_SEND, exchange_type="direct")
    
    connection_recv = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel_recv = connection_recv.channel()
    channel_recv.exchange_declare(exchange=E_RECV, exchange_type="direct")
    from_tech = channel_recv.queue_declare(queue="", exclusive=True)
    queue_tech = from_tech.method.queue
    channel_recv.queue_bind(exchange=E_RECV, queue=queue_tech, routing_key=doctor_name)
    
    connection_recv2 = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel_recv2 = connection_recv2.channel()
    channel_recv2.exchange_declare(exchange=FROM_ADMIN, exchange_type="direct")
    from_admin = channel_recv2.queue_declare(queue="", exclusive=True)
    queue_admin = from_admin.method.queue
    channel_recv2.queue_bind(exchange=FROM_ADMIN, queue=queue_admin, routing_key="d"+doctor_name)
    
    tid1 = RecieveThread(queue_tech,channel_recv)
    tid1.start()
    tid2 = RecieveThread(queue_admin,channel_recv2)
    tid2.start()
    
    try: 
        DoctShell(channel_send, doctor_name).cmdloop()
    except KeyboardInterrupt:
        tid1.stop()
        tid2.stop()
        tid1.join()
        tid2.join()
        connection_send.close()
        connection_recv.close()
        pass
    