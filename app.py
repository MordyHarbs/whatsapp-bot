from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Replace with your actual WhatsApp API details
WHATSAPP_PHONE_NUMBER_ID = "525298894008965"  # Your WhatsApp phone number ID
WHATSAPP_ACCESS_TOKEN = "EAASmeEcmWYcBO80QUrUzfqj7BlCfNuJiRjyXLbpRlVLIL94xxEb4F9GbZBHkFIw7ZAg6kOrBDJ5ZBRlXBeoTYiHtPpgIZBKdSUSZB8zcfobzvYR4s3HOxu8OXZAVZAfXgksOQ7qL0qUlrgpPTqxcAzV6CqgIWoaZCS1xSQhPH8z8SKgUP4fZBjI7p9HKwvOMLE6eONl4YSPljVVAkzPLDxQyQfCJr22kkjlWdRmYIRJKMq3hWFWZB5WbcZD"
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

                # Send the menu to the sender
                send_menu(sender)

    return jsonify({"status": "received"}), 200

def send_menu(recipient):
    """Sends a menu with two options."""
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "Please choose an option:"},
            "action": {
                "button": "Select an option",
                "sections": [
                    {
                        "title": "Options",
                        "rows": [
                            {"id": "option_1", "title": "Option 1", "description": "Select this for Option 1"},
                            {"id": "option_2", "title": "Option 2", "description": "Select this for Option 2"}
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Menu Sent:", response.json())  # Debugging log

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Ensure it matches Render's assigned port
    app.run(host="0.0.0.0", port=port)