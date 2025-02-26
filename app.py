from flask import Flask, request, jsonify
import os
import requests
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Load Google Sheets credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Google Sheets info
SHEET_ID = "1aE6ZDZ8W1qozc985MDMJLilLFGYDEHRyAhZnBeA_gWM"
cars_sheet = client.open_by_key(SHEET_ID).worksheet("cars")  # Open "cars" sheet

# WhatsApp API Details
WHATSAPP_PHONE_NUMBER_ID = "525298894008965"
WHATSAPP_ACCESS_TOKEN = "EAASmeEcmWYcBO3nQ4Wt2AW7yjZBbyMuQ6UYVlEFzDALBj4UoUOMkJT3gtc1dtEA1LyYU8XxZAgxq1hnDi0TrOSXNiHGsxqW4vnVEMNWSCIabt6ZCutbja7p1yA9ZCdywFD6FffVWXZBM9ZCFM3uf9Vt3O1xttuoWFXeXxNY48S2C2PT4YMA8WrqZCvmrq8e88jo7U2YE6ovHTbMELzXPTIAJQXbZAMv9Sue8MGZCGG4NrwchPl8spbY4S"
VERIFY_TOKEN = "my_custom_token"

# Track user input state
user_state = {}

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

    if "entry" in data and len(data["entry"]) > 0:
        changes = data["entry"][0].get("changes", [])
        if len(changes) > 0 and "value" in changes[0]:
            value = changes[0]["value"]

            if "messages" in value:
                msg = value["messages"][0]
                sender = msg["from"]

                # If user selected a menu option
                if "interactive" in msg:
                    selection = msg["interactive"]["list_reply"]["id"]
                    
                    if selection == "get_car_code":
                        send_message(sender, "אנא הזן מספר רכב")  # Ask for car number
                        user_state[sender] = "waiting_for_car_number"

                # If user is in input state, get car code from Google Sheets
                elif sender in user_state and user_state[sender] == "waiting_for_car_number":
                    car_number = msg.get("text", {}).get("body", "").strip()
                    car_code = get_car_code(car_number)  # Fetch car code from Google Sheets
                    send_message(sender, f"הקוד הוא {car_code}")
                    del user_state[sender]  # Remove user from tracking after response

                else:
                    send_menu(sender)  # Default: Show menu

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
            "body": {"text": "נא לבחור אפשרות:"},
            "action": {
                "button": "בחר אפשרות",
                "sections": [
                    {
                        "title": "אפשרויות",
                        "rows": [
                            {"id": "get_car_code", "title": "קוד לרכב", "description": "הזן מספר רכב לקבלת קוד"},
                            {"id": "option_2", "title": "Option 2", "description": "Select this for Option 2"}
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Menu Sent:", response.json())  # Debugging log

def get_car_code(car_number):
    """Fetches car code from Google Sheets based on the provided car number"""
    records = cars_sheet.get_all_records()  # Fetch all rows

    for row in records:
        if str(row.get("D", "")).strip() == car_number:
            return row.get("G", "לא נמצא קוד לרכב זה")  # Return column G value
    
    return "לא נמצא קוד לרכב זה"  # Return if not found

def send_message(recipient, text):
    """Sends a WhatsApp text message"""
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
    print("Message Sent:", response.json())  # Debugging log

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Ensure it matches Render's assigned port
    app.run(host="0.0.0.0", port=port)