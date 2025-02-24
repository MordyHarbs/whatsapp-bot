from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Replace with your actual WhatsApp API details
WHATSAPP_PHONE_NUMBER_ID = "525298894008965"  # Your WhatsApp phone number ID
WHATSAPP_ACCESS_TOKEN = "EAASmeEcmWYcBO6MVDPMR2UZB7539tEe1kTffBCm9FnnQ06xNrn5cNHorwUgXW2nSmzuvKSRSmiFDqOpYTZAoArWR8INs1t9m6zVKlOPUSE3nwB2Ya1zihs4UzXF5NPFPkImSnuQVjcHEYn0ZCEq0QgIRX1Y3rVYrI2ZCzuxk2fEAaFO93hHmHxO9fZCZBJ2w8yLNLsxjJRXdAvp6ZAQ12NXUkY0ONJwUEdavMOZBimeA9VkGryTVBQcZD"
VERIFY_TOKEN = "my_custom_token"  # The token you set in Meta's webhook settings

@app.route('/webhook', methods=['GET'])
def verify():
    """Webhook verification for WhatsApp API."""
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    """Handles incoming messages from WhatsApp."""
    data = request.json
    print("Received:", data)  # Debugging log

    # Ensure the request contains the required structure
    if "entry" in data and len(data["entry"]) > 0:
        changes = data["entry"][0].get("changes", [])
        if len(changes) > 0 and "value" in changes[0]:
            value = changes[0]["value"]

            # Check if the incoming webhook contains a message
            if "messages" in value:
                msg = value["messages"][0]  # Get the first message
                sender = msg["from"]
                message_text = msg["text"]["body"] if "text" in msg else ""

                # Log the received message
                print(f"Message from {sender}: {message_text}")

                # Auto-reply with a response
                send_reply(sender, f"Hello! You said: {message_text}")

    return jsonify({"status": "received"}), 200

def send_reply(recipient, text):
    """Sends a WhatsApp message via Cloud API."""
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text}
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("Reply Sent:", response.json())  # Debugging log

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Ensure it matches Render's assigned port
    app.run(host="0.0.0.0", port=port)