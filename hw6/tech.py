import sys
import pika
from time import sleep
from pika.channel import Channel
import pickle 
E_SEND = "exchange2"
E_RECV = "exchange1"
exams = ["knee", "hip", "elbow"]

def recieve(channel: Channel, method, properites, body):
    body = pickle.loads(body)
    print("Recieved: "+body[0]+" "+body[1]+" From: "+body[2])
    sleep(5)
    channel.basic_publish(exchange=E_SEND, routing_key=body[2], body=bytes(body[1]+" "+body[0]+" done","utf-8"))
    print("Sent results: "+body[1]+" "+body[0]+" done To: "+body[2])
    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Exctly 2 must be specified")
        exit(1)
    if sys.argv[1] not in exams or sys.argv[2] not in exams or sys.argv[1] == sys.argv[2]:
        print("Wrong configuration")
        exit(1)
    keys = sys.argv[1:]
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()
    
    channel.exchange_declare(exchange=E_SEND, exchange_type="direct")
    
    channel.exchange_declare(exchange=E_RECV, exchange_type="direct")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    for k in keys:
        channel.queue_bind(exchange=E_RECV, queue=queue_name, routing_key= k)
    channel.basic_consume(queue=queue_name, on_message_callback=recieve, auto_ack=False)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        pass
    connection.close()