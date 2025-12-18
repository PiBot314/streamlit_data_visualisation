import streamlit as st
import pandas as pd

FILE_NAME = "flightdata.csv"

# --- Data Loading (No caching needed as data is static) ---
def load_static_data(file_path):
    """Loads static flight data."""
    try:
        df = pd.read_csv(file_path)
        # Convert MISSION_TIME to string for better plotting
        df['MISSION_TIME'] = df['MISSION_TIME'].astype(str) 
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return None


def run_streamlit_app():
    st.set_page_config(
        page_title="Static Flight Data Dashboard",
        layout="wide"
    )
    
    st.title('🚀 nyoom nyoom')
    st.markdown(f"Displaying analysis of static file: **{FILE_NAME}**")

    # Load data once at the start
    df = load_static_data(FILE_NAME)

    if df is None:
        st.error(f"Error: The file '{FILE_NAME}' was not found. Please ensure it is in the same folder as this script.")
        return
    
    # --- Sidebar Filters ---
    st.sidebar.header("Data Controls")
    
    # Slider to filter the number of packets displayed
    max_packets = len(df)
    packet_limit = st.sidebar.slider(
        "Select Packet Count Limit (viewing latest):", 
        min_value=1, 
        max_value=max_packets, 
        value=max_packets, 
        step=1
    )
    
    # Filter the DataFrame to show only the newest data points
    df_filtered = df.tail(packet_limit)

    # --- Main Dashboard Layout ---

    # 1. Key Metrics Section
    st.header("📈 Key Telemetry Metrics")
    
    # Guard against empty filter result
    if df_filtered.empty:
        st.warning("No data points selected by the current filter.")
    else:
        col1, col2, col3 = st.columns(3)
        latest_row = df_filtered.iloc[-1]
        
        with col1:
            st.metric(label="Latest Altitude (m)", value=f"{latest_row.get('ALTITUDE', 'N/A'):.2f}")
        
        with col2:
            st.metric(label="Latest Temperature (°C)", value=f"{latest_row.get('TEMPERATURE', 'N/A'):.2f}")
            
        with col3:
            st.metric(label="Current Mode", value=latest_row.get('MODE', 'N/A'))
            
        st.markdown("---")
        
        # 2. Charts Section
        
        # Altitude vs. Time Chart
        st.subheader('Altitude & Pressure vs. Mission Time')
        
        if all(col in df_filtered.columns for col in ['MISSION_TIME', 'ALTITUDE', 'PRESSURE']):
            alt_press_data = df_filtered[['MISSION_TIME', 'ALTITUDE', 'PRESSURE']].set_index('MISSION_TIME')
            st.line_chart(alt_press_data)

        # Voltage & Current Chart
        st.subheader('Voltage and Current Over Time')
        
        if all(col in df_filtered.columns for col in ['MISSION_TIME', 'VOLTAGE', 'CURRENT']):
            volt_current_data = df_filtered[['MISSION_TIME', 'VOLTAGE', 'CURRENT']].set_index('MISSION_TIME')
            st.line_chart(volt_current_data)
    
    # 3. Raw Data Table
    st.header("📋 Raw Flight Data (Filtered)")
    st.dataframe(df_filtered)
    
    # --- NO REFRESH LOGIC ---
    # The script now simply ends, and Streamlit waits for user interaction (like the slider)
    # or the browser refresh button to re-run.


if __name__ == '__main__':
    run_streamlit_app()