import uuid
import requests
from flask import Flask, request, redirect
import random
import pika
import consul 
app = Flask(__name__)


@app.route('/')
def redirect_root():
    return redirect("/facade_service", code=302)

@app.route('/facade_service', methods=['GET', 'POST'])
def fascade():
    micro_msg_ports = []
    micro_logs_ports = []
    for instance in c.catalog.service("logging")[1]:
        micro_logs_ports.append(instance["ServicePort"])

    for instance in c.catalog.service("messages")[1]:
        micro_msg_ports.append(instance["ServicePort"])  

    _,data = c.kv.get('rmqlogin')
    rmqlogin = data['Value'].decode()
    _,data = c.kv.get('rmqpass')
    rmqpass = data['Value'].decode()
    _,data = c.kv.get('rmqqueue')
    rmqqueue = data['Value'].decode()
    ml_port = random.choice(micro_logs_ports)
    credentials = pika.PlainCredentials(rmqlogin, rmqpass)
    conn_params = pika.ConnectionParameters('localhost',5672,'/',credentials)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue=rmqqueue)

    if request.method == 'POST':
        if request.json.get('msg'):
            content = {str(uuid.uuid4()): request.json.get('msg')}
            requests.post(f'http://localhost:{ml_port}/log', json=content)
            channel.basic_publish(exchange='', routing_key=rmqqueue, body=str(request.json.get('msg')))
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
    service_name = "facade"
    service_addr = "192.168.88.1"
    port = 5001
    c = consul.Consul()
    c.agent.service.register(name=service_name, address=service_addr, port=port)
    app.run(host="0.0.0.0",port=port, debug=True,use_reloader=False)
