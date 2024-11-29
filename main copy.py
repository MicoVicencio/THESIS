import serial
import re
import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
import firebase_admin
from firebase_admin import credentials, db
from sms import ADBHandler
import calendar


class RFIDLogSystem:
    def __init__(self):
        # MySQL connection setup
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="micopogi",
            database="RFID_System"
        )   
        
        self.cursor = self.db.cursor()
        self.first_timein = None
        self.firebase_json_path = "firebase.json"  # Path to your Firebase credentials file
        self.firebase_db_url = "https://thesis-86ff4-default-rtdb.firebaseio.com/"
        self.status_ref_path = "/status/electricity"  # Firebase reference path for status
        # Set up the serial connection
        self.esp_ref_path = "/status/esp32"  # New Firebase reference path for logs
        self.adb_handler = ADBHandler()
        # Firebase setup
        
        self.firebase_cred = credentials.Certificate(self.firebase_json_path)
        firebase_admin.initialize_app(self.firebase_cred, {'databaseURL': self.firebase_db_url})
        self.status_ref = db.reference(self.status_ref_path)
        self.esp32_ref = db.reference(self.esp_ref_path)  # Add another reference here
        self.last_status = None
            
        self.esp32 = serial.Serial("COM4", baudrate=115200, timeout=1)

        # Regular expression patterns
        self.hex_pattern = re.compile(r"Received Hex Code: ([0-9a-fA-F]+)")
        self.admin_pattern = re.compile(r"(Admin on|Admin off)")
        self.lab_a_pattern = re.compile(r"Lab A")

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("RFID Log System")
        self.root.geometry("1500x800")
        self.root.configure(bg="#f0f0f0")
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Configure grid layout with weight distribution for full space utilization
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_columnconfigure(2, weight=1)

        # Load and display the logo in the top-left corner
        self.load_logo()

        # Add label for "SMART ELECTRICITY CONTROL SYSTEM" next to the seal
        self.system_label = tk.Label(self.root, text="SMART ELECTRICITY CONTROL SYSTEM - Lab A", font=('Arial', 22, 'bold'), bg="#d9eaf5", bd=2, relief="solid", anchor="w")
        self.system_label.grid(row=0, column=1, columnspan=2, padx=(10, 5), pady=10, sticky="w")

        # Time label to display the current time and date next to the system label
        self.time_label = tk.Label(self.root, font=('Arial', 20, 'bold'), bg="#d9eaf5", bd=2, relief="solid", anchor="e")
        self.time_label.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="e")
        self.update_time_label()

        # Profile Section (Left side)
        self.profile_frame = tk.Frame(self.root, width=250, height=300, bg="#cfe2f3", bd=2, relief="solid")
        self.profile_frame.grid(row=1, column=0, padx=10, pady=10)

        # Frame for the current user's information
        self.profile_info_frame = tk.Frame(self.profile_frame, width=250, bg="#cfe2f3")
        self.profile_info_frame.pack(pady=10)

        # Label to display current user
        self.current_user_label = tk.Label(self.profile_info_frame, text="Current User", font=('Arial', 25,), bg="#cfe2f3")
        self.current_user_label.grid(row=0, column=0, padx=10)

        # Placeholder for profile picture
        self.load_profile_picture()

        # Labels for displaying the current user's profile (name and department)
        self.profile_name_label = tk.Label(self.profile_info_frame, text="Name: ", font=('Arial', 20), bg="#cfe2f3", width=20, anchor="w")
        self.profile_name_label.grid(row=2, column=0, padx=10)
        self.profile_dept_label = tk.Label(self.profile_info_frame, text="Department: ", font=('Arial', 20), bg="#cfe2f3", width=20, anchor="w")
        self.profile_dept_label.grid(row=3, column=0, padx=10)

        # Logs Section (Center and Right side)
        self.logs_frame = tk.Frame(self.root, width=706, height=120, bg="red", bd=2, relief="solid")
        self.logs_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Treeview style customization
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Arial', 17), padding=(5, 5), rowheight=55)
        self.style.configure("Treeview.Heading", font=('Arial', 20, 'bold'))

        # Treeview to display logs (Time In and Time Out)
        self.tree = ttk.Treeview(self.logs_frame, columns=("Name", "Department", "Time In", "Time Out"), show="headings", height=10, style="Treeview")
        self.tree.heading("Name", text="Name", anchor="center")
        self.tree.heading("Department", text="Department", anchor="center")
        self.tree.heading("Time In", text="Time In", anchor="center")
        self.tree.heading("Time Out", text="Time Out", anchor="center")

        # Configure columns
        self.tree.column("Name", width=250, anchor="center")
        self.tree.column("Department", width=250, anchor="center")
        self.tree.column("Time In", width=250, anchor="center")
        self.tree.column("Time Out", width=250, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Start serial communication in a separate thread
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
        self.update_logs()
        self.monitor_thread = threading.Thread(target=self.monitor_and_control)
        self.monitor_thread.daemon = True  # Ensures the thread will exit when the main program ends
        self.monitor_thread.start()
        self.set_online()
        
    def set_status(self, status):
        """Sets the status in the Firebase Realtime Database."""
        if self.esp32_ref:
            self.esp32_ref.set(status)
            print(f"Status set to '{status}'")
        else:
            print("Database reference is not initialized.")

    def set_online(self):
        """Sets status to 'on'."""
        self.set_status("ONLINE")

    def set_offline(self):
        """Sets status to 'offline'."""
        self.set_status("offline")
        
    def on_close(self):
        """Handle the window close event."""
        print("Closing the app...")
        self.set_offline()
        self.root.destroy()
        
    def load_logo(self):
        # Load and resize the logo image
        image = Image.open("logo.png")
        image = image.resize((200, 150), Image.LANCZOS)
        self.logo_image = ImageTk.PhotoImage(image)

        # Display logo on the top-left corner
        logo_label = tk.Label(self.root, image=self.logo_image, bg="#f0f0f0")
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def load_profile_picture(self):
        # Load a placeholder profile picture
        placeholder_image = Image.open("placeholder.png")  # Replace "placeholder.png" with the path to your placeholder image
        placeholder_image = placeholder_image.resize((300, 260), Image.LANCZOS)
        self.profile_picture = ImageTk.PhotoImage(placeholder_image)

        # Profile picture label below "Current User"
        self.profile_picture_label = tk.Label(self.profile_info_frame, image=self.profile_picture, bg="#cfe2f3")
        self.profile_picture_label.grid(row=1, column=0, pady=(10, 10))

    def update_time_label(self):
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%A, %B %d, %Y")
        self.time_label.config(text=f"{current_date}\n{current_time}")
        self.root.after(1000, self.update_time_label)

    def update_logs(self):
        """Fetch and display the latest 11 logs in the TreeView with privacy-masked names."""
        # Query to fetch logs
        self.cursor.execute("""
            SELECT l.name, l.timein, l.timeout, u.department 
            FROM LabA_logs l
            JOIN users u ON l.name = u.name
            ORDER BY l.timein DESC
            LIMIT 11
        """)
        logs = self.cursor.fetchall()

        # Clear previous logs before inserting the updated logs
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert each log entry into the TreeView and apply zebra striping
        for i, row in enumerate(logs):
            if len(row) == 4:  # Ensure there are exactly 4 elements in the row
                masked_name = self.mask_name(row[0])  # Mask the name for privacy
                tag = "even" if i % 2 == 0 else "odd"  # Apply 'even' or 'odd' tag for zebra striping
                self.tree.insert('', 'end', values=(masked_name, row[3], row[1], row[2]), tags=(tag,))  # Insert name, department, timein, timeout into the tree

        # Configure zebra striping
        self.tree.tag_configure("even", background="#f0f0f0")  # Light color for even rows
        self.tree.tag_configure("odd", background="#ffffff")
        
    def generate_message(self, name, do):
        now = datetime.now()
    
    # Get the full weekday name (e.g., Monday, Tuesday)
        day_of_week = now.strftime("%A")
    
    # Get the month in words (e.g., July)
        month_name = calendar.month_name[now.month]
    
    # Get the day, year, and time (formatted as 12-hour with AM/PM)
        day = now.day
        year = now.year
        time = now.strftime("%I:%M %p")  # Time in 12-hour format with AM/PM

    # Create the personalized message based on whether it's timein or timeout
        if do == "timein":
            message = f"Good day {name}, You entered the laboratory on {day_of_week}, {month_name} {day}, {year} at {time}"
        elif do == "timeout":
            message = f"Good day {name}, You left the laboratory on {day_of_week}, {month_name} {day}, {year} at {time}"
    
        return message
    
        
        
    def add_log_entry(self, name):
        """Add a time-in or time-out entry to the log."""
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Mask the name for privacy
        masked_name = self.mask_name(name)

        # Check if the user has a time-in record that is not closed (no timeout)
        self.cursor.execute("SELECT id FROM LabA_logs WHERE name = %s AND timeout IS NULL", (name,))
        record = self.cursor.fetchone()

        # Check if there's an existing time-in
        if record:
            # User is already timed in, so record the timeout
            self.cursor.execute("UPDATE LabA_logs SET timeout = %s WHERE id = %s", (current_time, record[0]))
            print(f"Timeout recorded for {name}")
            self.profile_dept_label.config(text="Department: None")  # Clear the current user after timeout
            self.profile_name_label.config(text="Name: None")  # Clear the current user after timeout
            # Reset `first_timein` to allow new time-ins after timeout
            
            self.cursor.execute("SELECT phone_number FROM users WHERE name = %s", (name,))
            phone_number = self.cursor.fetchone()
            self.adb_handler.open_google_messages()
            time.sleep(3)
            phone_number_sms = phone_number[0]
            message = self.generate_message(name,"timeout")
            self.adb_handler.send_message(phone_number_sms,message)
                
            self.first_timein = None
        else:
            # Only log new time-in if `first_timein` is None
            if self.first_timein is None:
                # Insert Time-in entry if no previous open record exists
                self.cursor.execute("INSERT INTO LabA_logs (name, timein) VALUES (%s, %s)", (name, current_time))
                print(f"Timein recorded for {name}")
                # Update labels with the new user's information
                self.cursor.execute("SELECT department FROM users WHERE name = %s", (name,))
                department = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT phone_number FROM users WHERE name = %s", (name,))
                phone_number = self.cursor.fetchone()
                self.adb_handler.open_google_messages()
                time.sleep(1)
                phone_number_sms = phone_number[0]
                message = self.generate_message(name,"timein")
                self.adb_handler.send_message(phone_number_sms,message)
                
                
                self.profile_name_label.config(text=f"Name: {masked_name}")  # Use masked name
                self.profile_dept_label.config(text=f"Department: {department}")
                # Set `first_timein` to this user's name to prevent another time-in
                self.first_timein = name

        # Commit the transaction
        self.db.commit()

        # Refresh the TreeView to show all logs
        self.update_logs()
        
    def mask_name(self, name):
        """Masks a name by showing the first two characters and the last letter, replacing the middle part with asterisks."""
        name_parts = name.split(" ")  # Split the name by spaces (for first and last name)

        masked_name_parts = []
        for part in name_parts:
            if len(part) > 2:  # Mask only if the part has more than 2 characters
                # Mask the middle characters, keeping the first 2 and last character intact
                middle_length = len(part) - 3  # Subtract 2 for the first and last character
                masked_name = part[:2] + '•' * middle_length + part[-1]
                masked_name_parts.append(masked_name)
            else:
                # Keep short names (like "Jo") as they are
                masked_name_parts.append(part)

        return " ".join(masked_name_parts)


    def read_serial_data(self):
        while True:
            line = self.esp32.readline().decode("utf-8").strip()

            if line:
                print(f"Serial Output: {line}")  # Print all serial output

                # Check if the serial output contains "Lab A"
                if self.lab_a_pattern.search(line):
                    # Query LabA_logs to check if there are any records
                    self.cursor.execute("SELECT * FROM LabA_logs")
                    logs = self.cursor.fetchall()

                # Check if the serial output contains "admin on" or "admin off"
                elif self.admin_pattern.search(line):
                    status = "Admin on" if "Admin on" in line else "Admin off"
                    # Log the admin status in LabA_logs
                    print(f"Admin status: {status} recorded")

                # Search for the hex code in the serial output
                match = self.hex_pattern.search(line)
                if match:
                    hex_code = match.group(1)  # Extract the hex code
                    print(f"Hex Code Received: {hex_code}")

                    # Check if the hex code matches a user and retrieve name and department
                    self.cursor.execute("SELECT name FROM users WHERE hexcode = %s", (hex_code,))
                    user = self.cursor.fetchone()

                    if user:
                        name = user[0]
                        print(f"User Found: {name}")
                        self.add_log_entry(name)
                    else:
                        print("Hex code not found in the database.")
                        
    def monitor_and_control(self):
        """Combined function to monitor Firebase and send commands to ESP32."""
        while True:
            try:
                # Fetch the current status from Firebase
                current_status = self.status_ref.get()

                # Check if the status has changed
                if current_status != self.last_status:
                    if current_status == "on":
                        self.esp32.write(('on' + '\n').encode())
                        print(f"Sent to ESP32: on")
                    elif current_status == "off":
                        self.esp32.write(('off' + '\n').encode())
                        print(f"Sent to ESP32: off")

                    # Update the last status
                    self.last_status = current_status

                time.sleep(1)  # Delay before checking again
            except Exception as e:
                print(f"Error in monitor_and_control: {e}")
                time.sleep(1)  # Retry delay in case of error
                
    def run(self):
        # Run the Tkinter event loop
        self.root.mainloop()
        


# Run the application
if __name__ == "__main__":
    system = RFIDLogSystem()
    system.run()
