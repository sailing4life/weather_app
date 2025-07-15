import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide", page_title="Weather Plotter")

st.title("Weather Data Viewer")

# Upload CSV
uploaded_file = st.file_uploader("Upload a weather CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        df.columns = df.columns.str.replace('°', 'deg')  # Clean column names
        st.subheader("Available Columns")
        st.write(df.columns.tolist())

        # Parse time
        if 'W. Europe Daylight Time' in df.columns:
            df['Time'] = pd.to_datetime(df['W. Europe Daylight Time'], errors='coerce')
            df = df.dropna(subset=['Time'])

            # Select model name
            model_name = st.text_input("Enter model name", value="UM-Global")

            # Date filter
            st.subheader("Date Filter")
            min_date = df['Time'].dt.date.min()
            max_date = df['Time'].dt.date.max()
            date_range = st.date_input("Select date range", [min_date, max_date])

            if isinstance(date_range, list) and len(date_range) == 2:
                start_date, end_date = date_range
                df = df[df['Time'].dt.date.between(start_date, end_date)]

            # Select required columns
            try:
                df['TWS'] = df['kt']
                df['TWD'] = df['Wind10m deg']
                df['Gust'] = df['kt.3']
            except KeyError as e:
                st.error(f"Missing expected column: {e}")
                st.stop()

            df = df.dropna(subset=['TWD', 'TWS', 'Gust'])

            # Plotting
            fig, ax1 = plt.subplots(figsize=(12, 6))

            ax1.set_title(f"TWS / Direction\nModel: {model_name}", fontsize=14)
            ax1.set_xlabel("Time")
            ax1.set_ylabel("TWS / Gust (kt)", color='blue')

            ax1.plot(df['Time'], df['TWS'], 'b-', marker='.', label='TWS')
            ax1.plot(df['Time'], df['Gust'], color='lightblue', linestyle='--', marker='x', label='Gust')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)

            # Add value labels
            for x, y in zip(df['Time'], df['TWS']):
                ax1.text(x, y + 0.3, f'{y:.1f}', color='blue', fontsize=8, ha='center')
            for x, y in zip(df['Time'], df['Gust']):
                ax1.text(x, y + 0.3, f'{y:.1f}', color='lightblue', fontsize=8, ha='center')

            # Right Y-axis: TWD
            ax2 = ax1.twinx()
            ax2.set_ylabel("TWD (°)", color='red')
            ax2.plot(df['Time'], df['TWD'], 'r-', marker='.', label='TWD')
            ax2.tick_params(axis='y', labelcolor='red')

            for x, y in zip(df['Time'], df['TWD']):
                ax2.text(x, y + 3, f'{int(y)}', color='red', fontsize=8, ha='center')

            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate()

            st.pyplot(fig)
        else:
            st.error("The file must contain a 'W. Europe Daylight Time' column.")

    except Exception as e:
        st.error(f"Error reading file: {e}")
