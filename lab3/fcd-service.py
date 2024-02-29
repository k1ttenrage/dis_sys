# fcd-service.py

from flask import Flask, request, abort, jsonify
from random import choice
from uuid import uuid4
import requests
import socket

app = Flask(__name__)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg_service = "http://127.0.0.1:8001/messages"
ports = [8002, 8003, 8004]
closed_ports = []

def isOpen(port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect(('127.0.0.1', port))
      s.shutdown(2)
      return True
   except:
      return False

@app.route("/", methods=["POST", "GET"])
def handle_request():
    port = choice(ports)
    while not isOpen(port):
        if port not in closed_ports: closed_ports.append(port)
        port = choice(list(filter(lambda x: x not in closed_ports, ports)))
    if port in closed_ports: closed_ports.remove(port)
    log_service = f"http://127.0.0.1:{port}/logging"
    if request.method == "POST":
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid4())
        data = {"id": _id, "msg": _msg}
        response = requests.post(log_service, data=data)
        return jsonify(data), 200
    elif request.method == "GET":
        log_response = requests.get(log_service)
        msg_response = requests.get(msg_service)
        return [log_response.text, msg_response.text], 200
    else:
        abort(400)

if __name__ == "__main__":
    app.run(port=8000)