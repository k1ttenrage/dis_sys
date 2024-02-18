from flask import Flask

app = Flask(__name__)

@app.route('/messages', methods=['GET'])
def get_messages():
    return "Endpoint for retrieving messages"

if __name__ == '__main__':
    app.run(port=8002)
