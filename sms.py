import subprocess
import time
import urllib.parse

class ADBHandler:
    def __init__(self, adb_path="C:/Users/micov/AppData/Local/Android/Sdk/platform-tools/adb.exe"):
        self.adb_path = adb_path

    def adb_command(self, command):
        """Execute an ADB command."""
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Command executed successfully.")
            print(result.stdout)
        else:
            print("Error executing command.")
            print(result.stderr)

    def open_google_messages(self):
        """Open the Google Messages app."""
        command = f"{self.adb_path} shell am start -n com.google.android.apps.messaging/com.google.android.apps.messaging.ui.ConversationListActivity"
        self.adb_command(command)

    def send_message(self, phone_number, message):
        """Send a message to a specific phone number."""
        # Tap the "Start chat" button (adjust coordinates as per your screen)
        self.adb_command(f"{self.adb_path} shell input tap 835 2279")
        time.sleep(1)  # Wait for the "Start chat" screen to load
        
        # Enter the phone number
        self.adb_command(f"{self.adb_path} shell input text {phone_number}")
        time.sleep(1)  # Wait for the phone number input
        
        # Press Enter to confirm the phone number
        self.adb_command(f"{self.adb_path} shell input keyevent 66")
        time.sleep(2)  # Wait for the chat screen to load
        
        # Simulate typing the message character by character
        for char in message:
            if char == " ":
                # Simulate space key
                self.adb_command(f"{self.adb_path} shell input keyevent 62")
            elif char.isupper():
                # Simulate SHIFT key press for uppercase letters
                self.adb_command(f"{self.adb_path} shell input keyevent 59")  # SHIFT key
                self.adb_command(f"{self.adb_path} shell input text {char.lower()}")
                self.adb_command(f"{self.adb_path} shell input keyevent 60")  # SHIFT key release
            else:
                # Type lowercase letters or special characters
                self.adb_command(f"{self.adb_path} shell input text {char}")
            time.sleep(0.05)  # Reduced delay to make typing faster

        # Tap the "Send" button (adjust coordinates as per your screen)
        self.adb_command(f"{self.adb_path} shell input tap 980 1741")
        print(f"Message sent to {phone_number}: {message}")
        time.sleep(1)
        # Close the app by forcing it to stop
        self.adb_command(f"{self.adb_path} shell am force-stop com.google.android.apps.messaging")
