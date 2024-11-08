import serial
import re
import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

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

        # Set up the serial connection
        self.ser = serial.Serial("COM4", baudrate=115200, timeout=1)

        # Regular expression patterns
        self.hex_pattern = re.compile(r"Received Hex Code: ([0-9a-fA-F]+)")
        self.admin_pattern = re.compile(r"(Admin on|Admin off)")
        self.lab_a_pattern = re.compile(r"Lab A")

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("RFID Log System")
        self.root.geometry("1500x800")
        self.root.configure(bg="#f0f0f0")  # Set background color for the main window

        # Load and add logo to the top-left corner
        logo_image = Image.open("logo.png")
        logo_image = logo_image.resize((200, 150), Image.LANCZOS)  # Resize the logo
        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg="#f0f0f0")
        self.logo_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")

        # Configure grid layout with weight distribution for full space utilization
        self.root.grid_rowconfigure(0, weight=0)  # Title row
        self.root.grid_rowconfigure(1, weight=1)  # Main content rows (Profile and Logs)
        self.root.grid_columnconfigure(0, weight=1)  # Left column (Profile)
        self.root.grid_columnconfigure(1, weight=2)  # Center column (Logs area)
        self.root.grid_columnconfigure(2, weight=1)  # Right column (Time label and additional content)

        # Add label for "SMART ELECTRICITY CONTROL SYSTEM" next to the logo
        self.system_label = tk.Label(self.root, text="SMART ELECTRICITY CONTROL SYSTEM", font=('Arial', 30, 'bold'), bg="#d9eaf5", bd=2, relief="solid", anchor="w")
        self.system_label.grid(row=0, column=1, columnspan=2, padx=(10, 5), pady=10, sticky="w")

        # Time label to display the current time next to the system label
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
        self.current_user_label = tk.Label(self.profile_info_frame, text="Current User", font=('Arial', 16, 'italic'), bg="#cfe2f3")
        self.current_user_label.grid(row=0, column=0, padx=10)

        # Labels for displaying the current user's profile (name and department)
        self.profile_name_label = tk.Label(self.profile_info_frame, text="Name: ", font=('Arial', 16), bg="#cfe2f3", width=20, anchor="w")
        self.profile_name_label.grid(row=1, column=0, padx=10)
        self.profile_dept_label = tk.Label(self.profile_info_frame, text="Department: ", font=('Arial', 16), bg="#cfe2f3", width=20, anchor="w")
        self.profile_dept_label.grid(row=2, column=0, padx=10)

        # Logs Section (Center and Right side)
        self.logs_frame = tk.Frame(self.root, width=706, height=120, bg="red", bd=2, relief="solid")
        self.logs_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Treeview style customization
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Arial', 17), padding=(5, 5), rowheight=50)
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
        
    def update_time_label(self):
        # Get the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Update the time label text
        self.time_label.config(text=current_time)
        # Schedule this function to run again after 1 second
        self.root.after(1000, self.update_time_label)

    def update_logs(self):
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
                tag = "even" if i % 2 == 0 else "odd"  # Apply 'even' or 'odd' tag for zebra striping
                self.tree.insert('', 'end', values=(row[0], row[3], row[1], row[2]), tags=(tag,))  # Insert name, department, timein, timeout into the tree

        # Configure zebra striping
        self.tree.tag_configure("even", background="#f0f0f0")  # Light color for even rows
        self.tree.tag_configure("odd", background="#ffffff")   # White color for odd rows

    def add_log_entry(self, name):
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
                self.profile_name_label.config(text=f"Name: {name}")
                self.profile_dept_label.config(text=f"Department: {department}")
                # Set `first_timein` to this user's name to prevent another time-in
                self.first_timein = name

        # Commit the transaction
        self.db.commit()

        # Refresh the TreeView to show all logs
        self.update_logs()

    def read_serial_data(self):
        while True:
            line = self.ser.readline().decode("utf-8").strip()

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

    def run(self):
        # Run the Tkinter event loop
        self.root.mainloop()


# Run the application
if __name__ == "__main__":
    system = RFIDLogSystem()
    system.run()
