import uuid
import requests
from flask import Flask, request, redirect
import random
import pika
app = Flask(__name__)


@app.route('/')
def redirect_root():
    return redirect("/fascad_service", code=302)

@app.route('/fascad_service', methods=['GET', 'POST'])
def fascade():
    micro_msg_ports = [5003,5004]
    micro_logs_ports = [5005,5006,5007]
    ml_port = random.choice(micro_logs_ports)
    credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    conn_params = pika.ConnectionParameters('localhost',5672,'/',credentials)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue='lab6')

    if request.method == 'POST':
        if request.json.get('msg'):
            content = {str(uuid.uuid4()): request.json.get('msg')}
            requests.post(f'http://localhost:{ml_port}/log', json=content)
            channel.basic_publish(exchange='', routing_key='lab6', body=str(request.json.get('msg')))
            return 'Request accepted'
        else:
            return 'Bad Request', 400
    else:  
        getlogs = requests.get(f'http://localhost:{ml_port}/log')
        getmessages = ''
        for p in micro_msg_ports:
            getmessages += requests.get(f'http://localhost:{p}/').content.decode("utf-8") + '</br>'
        answer = '<div>' + '<h3>Logs:</h3>' + getlogs.content.decode("utf-8") + '</div>' + '<div>' + '<h3>Messages:</h3>' + getmessages + '</div>'
        return answer, 200   

if __name__ == '__main__':
    app.run(port=5001, debug=True)
