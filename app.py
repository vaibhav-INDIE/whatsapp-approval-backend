from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from twilio.rest import Client
import os

app = Flask(__name__)

# ✅ Enable CORS for all routes, allowing your frontend to connect.
# For production, you might want to restrict this to your frontend's domain:
# CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})
CORS(app)

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
        name = data.get('name')
        email = data.get('email')
        message_body = data.get('message')

        if not all([name, email, message_body]):
            return jsonify({"error": "Missing required fields: name, email, or message"}), 400

        # Format the message for WhatsApp
        whatsapp_message = (
            f"📬 *New Contact Form Submission*\n\n"
            f"*From:* {name}\n"
            f"*Email:* {email}\n\n"
            f"*Message:*\n{message_body}"
        )

        # Send the message using Twilio
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_NUMBER}',
            to=f'whatsapp:{MY_PHONE}',
            body=whatsapp_message
        )
        
        print(f"✅ Contact form message sent successfully. SID: {message.sid}")
        return jsonify({"message": "Your message has been sent successfully!"}), 200

    except Exception as e:
        print(f"❌ Failed to handle contact form: {str(e)}")
        return jsonify({"error": "An internal server error occurred."}), 500


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

# Start app with proper host/port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)