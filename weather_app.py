import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Weather Plot", layout="wide")
st.title("Weather Data Visualization")

# Input for model name
model_name = st.text_input("Enter model name to show in plot title:", value="UM-Global")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a weather CSV file", type=["csv"])

if uploaded_file is not None:
    # Read and prepare data
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.replace('°', 'deg')

    st.subheader("Detected Columns")
    st.write(list(df.columns))

    # Parse time column
    if 'W. Europe Daylight Time' in df.columns:
        df['Time'] = pd.to_datetime(df['W. Europe Daylight Time'], errors='coerce', utc=True)
    else:
        st.error("Required time column not found.")
        st.stop()

    # Check for required columns
    for col in ['kt', 'Wind10m deg', 'kt.3']:
        if col not in df.columns:
            st.error(f"Missing expected column: {col}")
            st.stop()

    # Rename key columns
    df['TWS'] = df['kt']
    df['TWD'] = df['Wind10m deg']
    df['Gust'] = df['kt.3']
    df = df.dropna(subset=['TWS', 'TWD'])

    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_title(f'TWS/Direction\nModel: {model_name}', fontsize=12)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('TWS / Gust (kt)', color='blue')

    ax1.plot(df['Time'], df['TWS'], 'b-', marker='.', label='TWS')
    ax1.plot(df['Time'], df['Gust'], color='lightblue', linestyle='--', marker='x', label='Gust')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)

    for x, y in zip(df['Time'], df['TWS']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='blue', fontsize=8, ha='center')

    for x, y in zip(df['Time'], df['Gust']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='lightblue', fontsize=8, ha='center')

    ax2 = ax1.twinx()
    ax2.set_ylabel('TWD (°)', color='red')
    ax2.plot(df['Time'], df['TWD'], 'r-', marker='.', label='TWD')
    ax2.tick_params(axis='y', labelcolor='red')

    for x, y in zip(df['Time'], df['TWD']):
        ax2.text(x, y + 3, f'{int(y)}', color='red', fontsize=8, ha='center')

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    fig.autofmt_xdate()

    st.pyplot(fig)
else:
    st.info("Please upload a CSV file to begin.")
