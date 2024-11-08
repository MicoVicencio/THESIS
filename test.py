import serial
import re
import mysql.connector
from datetime import datetime

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="micopogi",
    database="RFID_System"
)

cursor = db.cursor()

# Set up the serial connection
ser = serial.Serial("COM4", baudrate=115200, timeout=1)

# Regular expression patterns
hex_pattern = re.compile(r"Received Hex Code: ([0-9a-fA-F]+)")
admin_pattern = re.compile(r"(Admin on|Admin off)")
lab_a_pattern = re.compile(r"Lab A")

# Variable to store the last timein user
last_timein_user = None

try:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode("utf-8").strip()
        
        if line:
            print(f"Serial Output: {line}")  # Print all serial output

            # Check if the serial output contains "Lab A"
            if lab_a_pattern.search(line):
                # Query LabA_logs to check if there are any records
                cursor.execute("SELECT * FROM LabA_logs")
                logs = cursor.fetchall()

            # Check if the serial output contains "admin on" or "admin off"
            elif admin_pattern.search(line):
                status = "Admin on" if "Admin on" in line else "Admin off"
                # Log the admin status in LabA_logs
                print(f"Admin status: {status} recorded")

            # Search for the hex code in the serial output
            match = hex_pattern.search(line)
            if match:
                hex_code = match.group(1)  # Extract the hex code
                print(f"Hex Code Received: {hex_code}")

                # Check if the hex code matches a user and retrieve name and department
                cursor.execute("SELECT name, department FROM users WHERE hexcode = %s", (hex_code,))
                user = cursor.fetchone()
                
                if user:
                    name, department = user
                    print(f"User Found: {name}, Department: {department}")
                    
                    # Check if the last timein user has timed out or not
                    cursor.execute("SELECT id FROM LabA_logs WHERE name = %s AND timeout IS NULL", (name,))
                    record = cursor.fetchone()

                    if last_timein_user is None or last_timein_user == name:
                        if record:
                            # If a timein record already exists without a timeout, update it to timeout
                            cursor.execute("UPDATE LabA_logs SET timeout = %s WHERE id = %s", (datetime.now(), record[0]))
                            print(f"Timeout recorded for {name}")
                            # Reset last_timein_user immediately after the timeout
                            last_timein_user = None
                        else:
                            # Insert new Timein record if the user doesn't have a pending timeout
                            cursor.execute("INSERT INTO LabA_logs (name, timein) VALUES (%s, %s)", (name, datetime.now()))
                            print(f"Timein recorded for {name}")
                            last_timein_user = name
                        
                        # Commit the transaction
                        db.commit()

                        
                    else:
                        # Another user has already timed in, so ignore this user's timein
                        print(f"User {name} cannot time in because {last_timein_user} has already timed in.")
                else:
                    print("Hex code not found in the database.")
            
        # Optional delay for stability
        # time.sleep(0.1)  # Uncomment if needed to prevent high CPU usage

except KeyboardInterrupt:
    print("Exiting...")

finally:
    ser.close()  # Ensure the serial port is closed when done
    cursor.close()
    db.close()   # Close the database connection when done
