import requests

# EmailJS API endpoint
url = "https://api.emailjs.com/api/v1.0/email/send"

# Payload with your service, template, and user IDs
payload = {
    "service_id": "service_vueoden",  # Replace with your EmailJS service ID
    "template_id": "template_ve0mi1i",  # Replace with your EmailJS template ID
    "user_id": "p-vEdPnblIB1wBjtt",  # Replace with your EmailJS user ID
    "template_params": {
        "fullname": "John Doe",  # Replace with dynamic data
        "email": "micovicenciio55@gmail.com",
        "phone": "+1234567890",
        "subject": "Inquiry about Python",
        "message": "I would like to know more about Python email APIs.",
    }
}

# Set headers
headers = {"Content-Type": "application/json"}

# Send the request
response = requests.post(url, json=payload, headers=headers)

# Handle the response
if response.status_code == 200:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {response.text}")
