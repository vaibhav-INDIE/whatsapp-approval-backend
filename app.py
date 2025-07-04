from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from twilio.rest import Client
import os

app = Flask(__name__)

# Configure CORS with more specific settings
cors = CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "https://www.cuttu.in", "https://cuttu.in"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Load environment variables
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_PHONE = os.getenv("MY_PHONE")

# Setup Twilio client
client = Client(TWILIO_SID, TWILIO_TOKEN)

# Route to send WhatsApp message (for inference requests)
@app.route('/request', methods=['GET'])
def request_inference():
    try:
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_NUMBER}', # Recommended to add whatsapp: prefix
            to=f'whatsapp:{MY_PHONE}',         # Recommended to add whatsapp: prefix
            body="⚠️ New inference request received. Reply with 'yes' to approve."
        )
        return f"✅ Message sent successfully. SID: {message.sid}"
    except Exception as e:
        return f"❌ Failed to send message: {str(e)}", 500

# ✨ NEW ROUTE: To handle contact form submissions
@app.route('/contact', methods=['POST'])
def handle_contact():
    try:
        data = request.get_json()
        print("📩 Incoming request body:", data)

        name = data.get('name')
        email = data.get('email')
        message_body = data.get('message')

        print(f"📌 Name: {name}, Email: {email}, Message: {message_body}")

        if not all([name, email, message_body]):
            return jsonify({"error": "Missing required fields: name, email, or message"}), 400

        whatsapp_message = (
            f"📬 *New Contact Form Submission*\n\n"
            f"*From:* {name}\n"
            f"*Email:* {email}\n\n"
            f"*Message:*\n{message_body}"
        )

        message = client.messages.create(
            from_=TWILIO_NUMBER,
            to=MY_PHONE,
            body=whatsapp_message
        )

        print("✅ WhatsApp message sent")
        return jsonify({"message": "Your message has been sent successfully!"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Route to receive WhatsApp replies
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

# Add a root route to handle OPTIONS requests
@app.route('/', methods=['GET', 'OPTIONS'])
@cross_origin()
def handle_root():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    return jsonify({"status": "Server is running"}), 200

# Start app with proper host/port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port, threaded=True)