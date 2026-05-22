from twilio.rest import Client
import datetime

class Notifier:
    def __init__(self):
        # Twilio setup
        account_sid = "YOUR_TWILIO_SID"
auth_token = "YOUR_TWILIO_AUTH_TOKEN"
twilio_number = "YOUR_TWILIO_NUMBER" 
        self.client = Client(self.twilio_sid, self.twilio_token)

    def notify(self, message):
        """Simple alert (string message) → SMS format"""
        event = {
            "type": message,
            "location": "Smart Traffic Camera",
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }

        print("🚨 Alert Triggered:", event["type"])

        try:
            self.client.messages.create(
                body=f"🚨 {event['type']} at {event['location']} — {event['time']}",
                from_=self.twilio_number,
                to="your mobile number"
            )
            print("✅ SMS alert sent!")
        except Exception as e:
            print("❌ SMS failed:", e)



