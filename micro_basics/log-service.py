# log-service.py

from flask import Flask, request, abort, jsonify

app = Flask(__name__)

messages = {}

@app.route("/logging", methods=["POST", "GET"])
def log_request():
    if request.method == "POST":
        _id = request.form.get('id')
        _msg = request.form.get('msg')
        if not (_id or _msg):
            abort(400, "Missing 'id' or 'msg' field in the request")
        messages[_id] = _msg
        print("Received message:", _msg)
        return "Message logged successfully", 201
    elif request.method == "GET":
        # return jsonify(messages)
        return jsonify(list(messages.values()))
    else:
        abort(405)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": error.description}), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "This method is not allowed for the requested URL"}), 405

if __name__ == '__main__':
    app.run(port=8001)