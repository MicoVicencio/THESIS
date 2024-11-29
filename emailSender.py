# email_service.py

import requests

class EmailService:
    def __init__(self, service_id, template_id, user_id):
        self.service_id = service_id
        self.template_id = template_id
        self.user_id = user_id
        self.url = "https://api.emailjs.com/api/v1.0/email/send"

    def send_email(self, recipient_email, message):
        # Define the payload with dynamic email and template parameters
        payload = {
            "service_id": self.service_id,
            "template_id": self.template_id,
            "user_id": self.user_id,
            "template_params": {
                "to_name": "Recipient",  # You can modify this dynamically if needed
                "from_name": "RFID System",  # The sender's name
                "message": message,  # The message content
                "to_email": recipient_email,  # Dynamically set the recipient's email address
                "reply_to": "micovicencio55@gmail.com"  # The reply-to email address
            }
        }

        # Send the email request
        response = requests.post(self.url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            print("Email sent successfully!")
        else:
            print(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")


class EmailHandler:
    def __init__(self, email, message):
        self.email = email
        self.message = message
        self.email_service = EmailService(service_id='service_9zbj8qj', template_id='template_94nqmxf', user_id='Dj3EBJY39okL6yTPP')

    def send(self):
        # Use the EmailService to send the email
        self.email_service.send_email(self.email, self.message)
