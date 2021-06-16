from flask import Flask,request
import pika
import sys
from threading import Thread
from time import sleep
import sys

app = Flask(__name__)
messages_list = []
def main():
    credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    conn_params = pika.ConnectionParameters('localhost',5672,'/',credentials)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()

    channel.queue_declare(queue='lab6')
    
    def callback(ch, method, properties, body):    
        print(" [x] Received %r" % body.decode())
        messages_list.append(body.decode())
        print(messages_list)
    channel.basic_consume(queue='lab6', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

@app.route('/')
def msg():
    
    if request.method == 'GET':
        print(messages_list)
        return '</br>'.join(messages_list)

if __name__ == '__main__':
    Thread(target=main, daemon=True).start()
    app.run(port=int(sys.argv[1]), debug=True, use_reloader=False)
