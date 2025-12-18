import serial
import csv
import os
import time

# --- Configuration ---
SERIAL_PORT = 'COM11'  # This must be the receiving end of the virtual port pair
BAUD_RATE = 9600
CSV_FILE = 'xbee_data_log.csv'
# --- Configuration ---

def initialize_csv(filename):
    """Creates the CSV file and writes the header if it doesn't exist."""
    # Check if file exists to prevent writing header multiple times
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # The header must match the order of data being sent by the simulator
            header = ["Timestamp", "Sensor_ID", "Temperature_C", "Humidity_Pct"]
            writer.writerow(header)
            print(f"📝 Created new CSV file: {filename} with header: {header}")

def receive_and_log():
    initialize_csv(CSV_FILE)
    
    try:
        # Open the serial port connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Data Logger listening on {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        while True:
            # Read until the newline character (\n) is found
            # This is the standard way to read a complete serial message
            if ser.in_waiting > 0:
                # read_until() handles the buffering for a complete line
                data_line = ser.read_until(b'\n')
                
                # Decode the bytes to a string and remove whitespace (like \r\n)
                data_string = data_line.decode('utf-8').strip()

                if data_string:
                    print(f"<- Received: {data_string}")
                    
                    # Split the string by the comma delimiter
                    data_fields = data_string.split(',')
                    
                    if len(data_fields) == 4: # Basic data validation
                        # Append the parsed data fields to the CSV file
                        with open(CSV_FILE, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(data_fields)
                            print("    -> Logged successfully to CSV.")
                    else:
                        print(f"    ⚠️ Warning: Received malformed data: {data_string}")
            
            # Prevent busy waiting
            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"❌ Error: Could not open serial port {SERIAL_PORT}. Is the simulator running on the paired port?")
        print(f"Details: {e}")
    except KeyboardInterrupt:
        print("\nData Logger stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    receive_and_log()
