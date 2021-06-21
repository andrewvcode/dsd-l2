from flask import Flask, request, redirect
import hazelcast
import sys
import consul
app = Flask(__name__)


@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        getlogs = request.json
        print(getlogs)
        key = next(iter(getlogs.keys()))
        distributed_map.set(key,getlogs[key])
        return ''
    else:
        alllogs = '</br>'.join(distributed_map.get_all(distributed_map.key_set().result()).result().values())
        return alllogs

if __name__ == '__main__':
    service_name = "logging1" 
    service_addr = "192.168.88.1"
    c = consul.Consul()
    k = 2
    while True:
        if service_name in c.agent.services():
            service_name=service_name[:7] + str(k)
            k+=1
        else:
            break    
    port = 5003 + k  

    c.agent.service.register(name=service_name, address=service_addr, port=port)
    _,data = c.kv.get('hzcname')
    hzcname = data['Value'].decode()
    _,data = c.kv.get('hzdm')
    hzdm = data['Value'].decode()
    client = hazelcast.HazelcastClient(
    cluster_name=hzcname ,
    cluster_members=[
        "172.17.0.2:5701",
        "172.17.0.3:5701",
        "172.17.0.4:5701",
    ],
    lifecycle_listeners=[
        lambda state: print("Lifecycle event >>>", state),
    ]
    )
    distributed_map = client.get_map(hzdm)
    app.run(port=port, debug=True,use_reloader=False)
