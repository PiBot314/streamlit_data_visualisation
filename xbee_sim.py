import serial
import time
import random
from datetime import datetime

# --- Configuration ---
SERIAL_PORT = 'COM10'  # Use a virtual serial port created by com0com or similar tool
BAUD_RATE = 9600
# --- Configuration ---

def generate_sensor_data():
    """Generates a comma-separated data string."""
    # Simulate a small temperature fluctuation (e.g., 20.0 to 25.0)
    temperature = round(random.uniform(20.0, 25.0), 2)
    # Simulate relative humidity (e.g., 40.0 to 60.0)
    humidity = round(random.uniform(40.0, 60.0), 2)
    # Simulated unique sensor ID
    sensor_id = "SENS_A01"
    # Current timestamp for logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Data format: [Timestamp],[Sensor ID],[Temperature],[Humidity]\r\n
    # \r\n (CRLF) is a common end-of-line delimiter for serial/telemetry data
    data_string = f"{timestamp},{sensor_id},{temperature},{humidity}\r\n"
    return data_string.encode('utf-8') # Encode string to bytes for serial transmission

def simulate_xbee():
    try:
        # Open the serial port connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ XBee Simulator connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        while True:
            data_to_send = generate_sensor_data()
            
            # Write the data to the serial port
            ser.write(data_to_send)
            
            print(f"-> Sent: {data_to_send.decode('utf-8').strip()}")
            
            # Wait for 5 seconds before sending the next reading
            time.sleep(5)

    except serial.SerialException as e:
        print(f"❌ Error: Could not open or communicate with serial port {SERIAL_PORT}.")
        print("Please ensure the port is available and a virtual port pair (e.g., COM10 -> COM11) is set up.")
        print(f"Details: {e}")
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    simulate_xbee()
