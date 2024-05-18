import sys
import pika
from time import sleep
from pika.channel import Channel
import pickle 
E_SEND = "exchange2"
E_RECV = "exchange1"
FROM_ADMIN = "exchange3"
TO_ADMIN_QUEUE = "admin"

exams = ["knee", "hip", "elbow"]
keys = []
technician_name = ""

def recieve(channel: Channel, method, properites, body):
    body = pickle.loads(body)
    pr = "Recieved: "+body[0]+" "+body[1]+" From: "+body[2]
    print(pr)
    # log
    channel.basic_publish(exchange="", routing_key=TO_ADMIN_QUEUE, body=bytes("From technician "+technician_name+": "+pr, encoding="utf-8"))
    res = body[1]+" "+body[0]+" done"
    sleep(5)
    channel.basic_publish(exchange=E_SEND, routing_key=body[2], body=bytes(res, encoding="utf-8"))
    # log
    channel.basic_publish(exchange="", routing_key=TO_ADMIN_QUEUE, body=bytes("From technician "+technician_name+": "+res, encoding="utf-8"))
    
    print("Sent results: "+body[1]+" "+body[0]+" done To: "+body[2])
    channel.basic_ack(delivery_tag=method.delivery_tag)
    
def recieve_admin(channel: Channel, method, properites, body):
    body = body.decode("utf-8")
    print("From Admin: "+body)
    channel.basic_publish(exchange="", routing_key=TO_ADMIN_QUEUE, body=bytes("From technician "+technician_name+": "+body, encoding="utf-8"))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Exctly 4 cmd arguments must be specified")
        exit(1)
    if sys.argv[1] not in exams or sys.argv[2] not in exams or sys.argv[1] == sys.argv[2]:
        print("Wrong configuration")
        exit(1)
    technician_name = sys.argv[3]
    keys = sys.argv[1:]
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=1000)
    )
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    
    channel.exchange_declare(exchange=E_SEND, exchange_type="direct")
    for k in keys:    
        result = channel.queue_declare(queue=k)
        channel.basic_consume(queue=k, on_message_callback=recieve, auto_ack=False)
        channel.queue_bind(exchange=E_RECV, queue=k, routing_key=k)
    
    channel.exchange_declare(exchange=FROM_ADMIN, exchange_type="direct")
    from_admin = channel.queue_declare(queue="", exclusive=True)
    queue_admin = from_admin.method.queue
    channel.basic_consume(queue=queue_admin, on_message_callback=recieve_admin, auto_ack=True)
    channel.queue_bind(exchange=FROM_ADMIN, queue=queue_admin, routing_key="t"+technician_name)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        pass
    connection.close()