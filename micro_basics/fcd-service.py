from flask import Flask, request, abort, jsonify
import requests
import uuid

app = Flask(__name__)

log_service = "http://127.0.0.1:8001/logging"
msg_service = "http://127.0.0.1:8002/messages"

@app.route("/", methods=["POST", "GET"])
def handle_request():
    if request.method == "POST":
        _msg = request.form.get("msg")
        if not _msg:
            return "Message not provided", 400
        _id = str(uuid.uuid4())
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