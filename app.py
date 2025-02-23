from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['GET'])
def verify():
    verify_token = "my_custom_token"
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if token == verify_token:
        return challenge
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    print("Received:", data)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)