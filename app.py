import os
from flask import Flask, request
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Twilio setup
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
my_number = os.getenv("MY_PHONE")
client = Client(account_sid, auth_token)

@app.route("/request", methods=["GET"])
def send_whatsapp_request():
    message = client.messages.create(
        body="⚠️ New Inference Request.\nReply with 'yes' to approve.",
        from_=twilio_number,
        to=my_number
    )
    return "Request sent via WhatsApp ✅"

@app.route("/webhook", methods=["POST"])
def receive_whatsapp_response():
    incoming_msg = request.form.get("Body", "").strip().lower()
    if incoming_msg == "yes":
        print("✅ Approved")
    else:
        print("❌ Not approved or ignored")
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
