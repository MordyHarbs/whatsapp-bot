from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Replace with your actual WhatsApp API details
WHATSAPP_PHONE_NUMBER_ID = "525298894008965"  # Your WhatsApp phone number ID
WHATSAPP_ACCESS_TOKEN = "EAASmeEcmWYcBOZBw5Hm87YMwZCVhZCFS1I7rDAtbyfb6rz52BUwG3C44Fubxibgel2KmhZBsnah4ap6ymcIBKvfFnJg6aIr2ZBQlWsXFSkxJ7XGrMlZAt0UNUS3od5Pcg1vLtPsGEKCZC0RGBPHwk8xyzVk05T6ght3SrU7nhlL4DwMcmTgPGXMgSTLYhdMMPd6Nj5hDfdonkwUPW9iXrycnAMZBtMffUGzl6cmAoc3Xbehyr8FUshIZD"
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

    if "messages" in data["entry"][0]["changes"][0]["value"]:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = msg["from"]
        message_text = msg["text"]["body"] if "text" in msg else ""

        # Log the incoming message
        print(f"Message from {sender}: {message_text}")

        # Auto-reply
        send_reply(sender, "Hello! This is an auto-reply from my bot.")

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
        "text": {"body": text}
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("Reply Sent:", response.json())  # Debugging log

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Ensure it matches Render's assigned port
    app.run(host="0.0.0.0", port=port)