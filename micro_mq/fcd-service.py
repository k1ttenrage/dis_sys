# fcd-service.py

from flask import Flask, request, abort, jsonify
from random import choice
from uuid import uuid4
import hazelcast
import requests
import socket
import json

hz = hazelcast.HazelcastClient(cluster_name="lab4")
queue = hz.get_queue("queue").blocking()

app = Flask(__name__)
log_ports = [8003, 8004, 8005]
msg_ports = [8001, 8002]
closed_ports = []
msgs = {}
msgs['messages_from_msg'] = []

def isOpen(port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect(('127.0.0.1', port))
      s.shutdown(2)
      return True
   except:
      return False

def get_open_port(ports):
    port = choice(ports)
    while not isOpen(port):
        if port not in closed_ports: closed_ports.append(port)
        port = choice(list(filter(lambda x: x not in closed_ports, ports)))
    if port in closed_ports: closed_ports.remove(port)
    return port

@app.route("/", methods=["POST", "GET"])
def handle_request():

    log_service = f"http://127.0.0.1:{get_open_port(log_ports)}/logging"

    msg_service = f"http://127.0.0.1:{get_open_port(msg_ports)}/messages"

    if request.method == "POST":
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid4())
        data = {"id": _id, "msg": _msg}
        response = requests.post(log_service, data=data)
        queue.offer(json.dumps(_msg))
        return jsonify(data), 200
    
    elif request.method == "GET":
        log_response = requests.get(log_service)
        msg_response = requests.get(msg_service).json()
        print(msg_response['messages_from_msg'])
        for i in msg_response['messages_from_msg']: 
            if i not in msgs['messages_from_msg']:
                msgs['messages_from_msg'].append(i)
        return [log_response.text, msgs], 200
    
    else:
        abort(400)

if __name__ == "__main__":
    app.run(port=8000)