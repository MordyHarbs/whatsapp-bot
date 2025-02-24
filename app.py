from flask import Flask, request, jsonify
import os

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
    print("Received:", data)  # Debugging log
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Ensures Render uses the right port
    app.run(host="0.0.0.0", port=port)