import serial
import csv
import os
import time

# --- Configuration ---
# IMPORTANT: This must be the receiving port (e.g., COM11 if using COM10 in simulator)
SERIAL_PORT = 'COM11' 
BAUD_RATE = 9600
CSV_FILE = 'flight_telemetry_log.csv'

# Define the expected header row based on your data format
CSV_HEADER = [
    "TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "MODE", "STATE", "ALTITUDE",
    "TEMPERATURE", "PRESSURE", "VOLTAGE", "CURRENT", "GYRO_R", "GYRO_P",
    "GYRO_Y", "ACCEL_R", "ACCEL_P", "ACCEL_Y", "GPS_TIME", "GPS_ALTITUDE",
    "GPS_LATITUDE", "GPS_LONGITUDE", "GPS_SATS", "CMD_ECHO"
]
# --- Configuration ---

def initialize_csv(filename, header):
    """Creates the CSV file and writes the header if it doesn't exist."""
    file_exists = os.path.exists(filename)
    
    # Open the file in append mode ('a') with newline=''
    # newline='' prevents extra blank rows on Windows
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write the header only once when the file is created
            writer.writerow(header)
            print(f"📝 Created new CSV file: {filename} with header.")

def receive_and_log():
    # 1. Initialize the CSV file
    initialize_csv(CSV_FILE, CSV_HEADER)
    
    try:
        # 2. Setup the Serial Port
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Data Logger listening on {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        while True:
            # 3. Read Data Line-by-Line
            if ser.in_waiting > 0:
                # ser.read_until() reads bytes until it finds the delimiter (b'\n')
                data_line_bytes = ser.read_until(b'\n')
                
                # Decode bytes to string and strip whitespace/delimiters (\r\n)
                data_string = data_line_bytes.decode('utf-8').strip()

                if data_string:
                    # 4. Parse the String
                    # Split the string by the comma delimiter
                    data_fields = data_string.split(',')
                    
                    if len(data_fields) == len(CSV_HEADER):
                        # 5. Write to CSV
                        with open(CSV_FILE, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(data_fields)
                            print(f"<- Received and Logged: {data_fields[0]}, {data_fields[1]}, {data_fields[2]}...")
                    else:
                        print(f"    ⚠️ Warning: Data count mismatch. Expected {len(CSV_HEADER)} fields, got {len(data_fields)}. Skipping.")
            
            time.sleep(0.01) # Small delay to prevent 100% CPU usage

    except serial.SerialException as e:
        print(f"❌ Error: Could not open serial port {SERIAL_PORT}.")
        print("Please ensure the virtual port is active and correct.")
        print(f"Details: {e}")
    except KeyboardInterrupt:
        print("\nData Logger stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    receive_and_log()
