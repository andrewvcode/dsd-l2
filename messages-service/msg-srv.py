from flask import Flask,request
import pika
import sys
from threading import Thread
from time import sleep
import sys
import consul  
app = Flask(__name__)
messages_list = []
def main():
    _,data = c.kv.get('rmqlogin')
    rmqlogin = data['Value'].decode()
    _,data = c.kv.get('rmqpass')
    rmqpass = data['Value'].decode()
    _,data = c.kv.get('rmqqueue')
    rmqqueue = data['Value'].decode()
    print(rmqqueue)
    credentials = pika.PlainCredentials(rmqlogin, rmqpass)
    conn_params = pika.ConnectionParameters('localhost',5672,'/',credentials)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()

    channel.queue_declare(queue=rmqqueue)
    
    def callback(ch, method, properties, body):    
        print(" [x] Received %r" % body.decode())
        messages_list.append(body.decode())
        print(messages_list)
    channel.basic_consume(queue=rmqqueue, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

@app.route('/')
def msg():
    
    if request.method == 'GET':
        print(messages_list)
        return '</br>'.join(messages_list)

if __name__ == '__main__':
    service_name = "messages" 
    service_id = "messages1"
    service_addr = "192.168.88.1"
    c = consul.Consul()
    k = 2
    while True:
        if service_id in c.agent.services():
            service_id=service_id[:8] + str(k)
            k+=1
        else:
            break    
    port = 5001 + k        
    c.agent.service.register(service_id=service_id,name=service_name, address=service_addr, port=port)
    Thread(target=main, daemon=True).start()
    app.run(port=port, debug=True, use_reloader=False)
