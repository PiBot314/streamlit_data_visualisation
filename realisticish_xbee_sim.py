import serial
import time
import random
import csv
from datetime import datetime

# --- Configuration (Must match your virtual serial port setup) ---
SERIAL_PORT = 'COM10'  # Sender side of the virtual pair
BAUD_RATE = 9600
TEAM_ID = "fly"

# Flight Profile Parameters
APOGEE_ALTITUDE = 1000  # meters
RELEASE_ALTITUDE = 100  # meters (for secondary parachute/landing phase)
# --- Configuration ---

# Global State Variables
mission_time = 0
packet_count = 0
altitude_m = 0.0
latitude_deg = 35.0  # Starting Lat
longitude_deg = -106.0 # Starting Lon
temperature_c = 25.0
pressure_pa = 101325.0
voltage_v = 9.0
current_ma = 50.0
flight_state = "PRE-FLIGHT"
flight_mode = "STANDBY"
cmd_echo = "NONE"

# Define the flight stages and their duration/rates
FLIGHT_STAGES = [
    # 0. Wait on Pad
    {"STATE": "PRE-FLIGHT", "DURATION": 10, "ALT_RATE": 0, "TEMP_RATE": 0.0},
    # 1. Ascent (Fast climb)
    {"STATE": "ASCENT", "DURATION": 30, "ALT_RATE": 33.3, "TEMP_RATE": -0.5},
    # 2. Descent (Freefall/Drogue Parachute)
    {"STATE": "DROGUE_DESCENT", "DURATION": 20, "ALT_RATE": -15, "TEMP_RATE": 0.3},
    # 3. Main Parachute (Slower descent)
    {"STATE": "MAIN_DESCENT", "DURATION": 70, "ALT_RATE": -5, "TEMP_RATE": 0.1},
    # 4. Landed
    {"STATE": "LANDED", "DURATION": 30, "ALT_RATE": 0, "TEMP_RATE": 0.0}
]

def save_to_csv(filename, data_list):
    """
    Appends a single list of data as a new row in a CSV file.
    """
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data_list)

def generate_telemetry_line(state_data):
    """Generates a single, comma-separated telemetry line."""
    global mission_time, packet_count, altitude_m, latitude_deg, longitude_deg
    global temperature_c, pressure_pa, voltage_v, current_ma, flight_state, flight_mode, cmd_echo

    # --- 1. Increment Counters & Update State ---
    mission_time += 1
    packet_count += 1
    flight_state = state_data["STATE"]

    # --- 2. Calculate Sensor Values based on Rate ---
    # Altitude: Apply rate + small noise
    altitude_m += state_data["ALT_RATE"] + random.uniform(-0.5, 0.5)
    altitude_m = max(0.0, altitude_m) # Cannot go below zero

    # Pressure: Inverse relationship with altitude (approx. simplified barometric formula)
    # 101325 Pa at sea level. Decreases by ~12 Pa/m.
    pressure_pa = 101325.0 - altitude_m * 12.0 + random.uniform(-50, 50)

    # Temperature: Apply rate + small noise (Temperature cools during ascent)
    temperature_c += state_data["TEMP_RATE"] + random.uniform(-0.1, 0.1)

    # GPS: Simulate movement and acquisition during flight
    if altitude_m > 50:
        # Simulate slight drift during flight (Lat/Lon change by very small amount)
        latitude_deg += random.uniform(-0.00005, 0.00005)
        longitude_deg += random.uniform(-0.00005, 0.00005)
        gps_sats = random.randint(5, 12)
        gps_altitude = round(altitude_m + random.uniform(-10, 10), 2)
    else:
        # On the ground
        gps_sats = random.randint(0, 3) # Signal lost/poor on ground
        gps_altitude = 0.0


    # Voltage/Current: Simulate slight battery drop
    voltage_v = max(8.5, voltage_v - 0.001)
    current_ma = max(10.0, current_ma + random.uniform(-1.0, 1.0))

    # IMU Data: Simulate stable ascent/descent, noisy ground
    if flight_state == "PRE-FLIGHT" or flight_state == "LANDED":
        # Noisy on the ground
        gyro_r = round(random.uniform(-5, 5), 2)
        accel_p = round(random.uniform(-0.5, 0.5), 2)
    else:
        # Stable flight
        gyro_r = round(random.uniform(-0.2, 0.2), 2)
        accel_p = round(random.uniform(0.9, 1.1), 2) # Near 1G vertical acceleration

    # GPS Time (Simulated UTC time)
    gps_time = datetime.now().strftime("%H:%M:%S")

    # --- 3. Format Telemetry String ---
    # The final data must be formatted exactly as requested, delimited by commas.
    data = [
        TEAM_ID, 
        datetime.utcfromtimestamp(mission_time).strftime('%H:%M:%S'), # MISSION_TIME in hh:mm:ss format
        packet_count,
        flight_mode,
        flight_state,
        f"{altitude_m:.2f}",
        f"{temperature_c:.2f}",
        f"{pressure_pa:.2f}",
        f"{voltage_v:.2f}",
        f"{current_ma:.2f}",
        f"{gyro_r:.2f}", # GYRO_R
        f"{random.uniform(-0.2, 0.2):.2f}", # GYRO_P
        f"{random.uniform(-0.2, 0.2):.2f}", # GYRO_Y
        f"{accel_p:.2f}", # ACCEL_R (Roll/X-axis)
        f"{accel_p:.2f}", # ACCEL_P (Pitch/Y-axis)
        f"{random.uniform(0.9, 1.1):.2f}", # ACCEL_Y (Yaw/Z-axis - should be near 1G on descent)
        gps_time, 
        f"{gps_altitude:.2f}",
        f"{latitude_deg:.6f}",
        f"{longitude_deg:.6f}",
        gps_sats,
        cmd_echo
    ]
    
    # Join list with commas and add the serial delimiter (\r\n)
    return ",".join(map(str, data)) + "\r\n"

def simulate_flight():
    global mission_time, flight_state, flight_mode, cmd_echo

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ XBee Simulator connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        print("-" * 50)
        
        start_time = time.time()
        stage_timer = 0
        current_stage = 0
        
        while current_stage < len(FLIGHT_STAGES):
            stage_data = FLIGHT_STAGES[current_stage]
            
            # --- State/Command Logic Triggers ---
            if stage_data["STATE"] == "ASCENT":
                flight_mode = "FLIGHT"
            elif stage_data["STATE"] == "DROGUE_DESCENT" and altitude_m > APOGEE_ALTITUDE - 5:
                # Trigger DROGUE_DESCENT stage when near APOGEE (or after ascent duration)
                print(f"** EVENT: Apogee Reached! Beginning Drogue Descent. **")
                flight_mode = "DEPLOYMENT"
            elif stage_data["STATE"] == "MAIN_DESCENT" and altitude_m < RELEASE_ALTITUDE + 10:
                # Trigger MAIN_DESCENT stage when near the secondary release altitude
                print(f"** EVENT: Secondary Release Altitude Reached! Beginning Main Parachute Descent. **")
                flight_mode = "RECOVERY"
            elif stage_data["STATE"] == "LANDED" and altitude_m < 5:
                # Trigger LANDED state when near ground level
                print(f"** EVENT: Landing Detected. Data Logging Complete. **")
                flight_mode = "LANDED"
            
            # --- Generate and Send Data ---
            data_to_send_str = generate_telemetry_line(stage_data)
            ser.write(data_to_send_str.encode('utf-8'))
            print(f"[{stage_data['STATE']}] -> Sent Pkt {packet_count}: Alt={altitude_m:.1f}m, Temp={temperature_c:.1f}°C")
            
            # --- State Transition Logic ---
            stage_timer += 1
            if stage_timer >= stage_data["DURATION"] or \
               (stage_data["STATE"] == "ASCENT" and altitude_m >= APOGEE_ALTITUDE) or \
               (stage_data["STATE"] == "DROGUE_DESCENT" and altitude_m <= RELEASE_ALTITUDE) or \
               (stage_data["STATE"] == "MAIN_DESCENT" and altitude_m <= 0.0):
                
                # Advance to the next stage
                current_stage += 1
                stage_timer = 0
                cmd_echo = "NEXT_STAGE" # Set temporary command echo
            else:
                cmd_echo = "NONE" # Clear command echo after one cycle
                
            time.sleep(1) # Frequency of 1 second

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
    simulate_flight()
