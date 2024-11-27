import serial
import time
import firebase_admin
from firebase_admin import credentials, db

# Firebase setup
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://thesis-86ff4-default-rtdb.firebaseio.com/'
})

# Serial port setup (adjust COM port and baud rate as needed)
serial_port = "COM4"  # Change to the port ESP32 is connected to (e.g., /dev/ttyUSB0 for Linux/Mac)
baud_rate = 115200
esp32 = serial.Serial(serial_port, baud_rate, timeout=1)

def get_status_from_firebase():
    ref = db.reference("status")  # Adjust path if needed
    return ref.get()

def send_command_to_esp32(command):
    esp32.write((command + '\n').encode())  # Send command to ESP32
    print(f"Sent to ESP32: {command}")
    time.sleep(1)  # Allow time for ESP32 to process

def main():
    last_status = None

    while True:
        try:
            # Get the current status from Firebase
            current_status = get_status_from_firebase()

            if current_status != last_status:  # Only send command if status has changed
                if current_status == "on":
                    send_command_to_esp32("on")
                elif current_status == "off":
                    send_command_to_esp32("off")
                
                last_status = current_status

            time.sleep(1)  # Check Firebase every 2 seconds

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)  # Wait before retrying in case of error

if __name__ == "__main__":
    main()
