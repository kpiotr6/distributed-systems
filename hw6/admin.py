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

class RecieveThread(Thread):
    def __init__(self, queue, channel):
        super().__init__()
        self.channel: BlockingChannel = channel
        self.queue = queue
        self.stopped = False
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
        self.channel.cancel()    
        
class AdminShell(cmd.Cmd):
    prompt = "Admin >>> "
    def __init__(self, channel: Channel):
        super().__init__()
        self.channel: Channel  = channel
    
    def do_info(self, arg: str):
        splitted = arg.split(" ", 1)
        if len(splitted) != 2:
            print("Wrong arguments")
            return
        name, message = splitted
        info_other(name, message, self.channel)
    def do_exit(self, arg):
        self.close()

def info_other(name: str, mess: str, channel: Channel):
    channel.basic_publish(exchange=FROM_ADMIN, routing_key=name, body=bytes(mess, encoding="utf-8"))

if __name__ == "__main__":

    
    connection_send = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel_send = connection_send.channel()
    
    channel_send.exchange_declare(exchange=FROM_ADMIN, exchange_type="direct")
    
    connection_recv = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel_recv = connection_recv.channel()
    result = channel_recv.queue_declare(queue=TO_ADMIN, exclusive=True)
    queue_name = result.method.queue
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
