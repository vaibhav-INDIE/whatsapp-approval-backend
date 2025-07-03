from flask import Flask, request
from twilio.rest import Client
import os

app = Flask(__name__)

# Load environment variables
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_PHONE = os.getenv("MY_PHONE")

# Setup Twilio client
client = Client(TWILIO_SID, TWILIO_TOKEN)

# ✅ Route to send WhatsApp message
@app.route('/request', methods=['GET'])
def request_inference():
    try:
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            to=MY_PHONE,
            body="⚠️ New inference request received. Reply with 'yes' to approve."
        )
        return f"✅ Message sent successfully. SID: {message.sid}"
    except Exception as e:
        return f"❌ Failed to send message: {str(e)}", 500

# ✅ Route to receive WhatsApp replies
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body', '').strip().lower()
    print(f"📨 Received WhatsApp message: {incoming_msg}")

    if incoming_msg == 'yes':
        print("✅ Approved!")
        # You can trigger Azure VM start here later
    else:
        print("❌ Not approved or unrecognized message.")

    return "OK", 200

# ✅ Start app with proper host/port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
