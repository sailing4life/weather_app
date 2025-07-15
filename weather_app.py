# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:14:39 2025

@author: NAVPC
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.title("Weather Data Visualization")

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV with latin1 encoding
    df = pd.read_csv(uploaded_file, encoding='latin1')
    # Clean column names
    df.columns = df.columns.str.replace('°', 'deg')
    
    st.subheader("Columns in the CSV")
    st.write(list(df.columns))
    
    # Parse time column safely
    if 'W. Europe Daylight Time' in df.columns:
        df['Time'] = pd.to_datetime(df['W. Europe Daylight Time'], errors='coerce', utc=True)
    else:
        st.error("Column 'W. Europe Daylight Time' not found!")
        st.stop()
    
    # Extract needed columns
    for col in ['kt', 'Wind10m deg', 'kt.3']:
        if col not in df.columns:
            st.error(f"Column '{col}' not found!")
            st.stop()
    df['TWS'] = df['kt']
    df['TWD'] = df['Wind10m deg']
    df['Gust'] = df['kt.3']
    
    # Drop rows with missing TWS or TWD
    df = df.dropna(subset=['TWS', 'TWD'])
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_title('TWS/Direction\nModels: UM-Global', fontsize=12)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('TWS / Gust (kt)', color='blue')
    
    ax1.plot(df['Time'], df['TWS'], 'b-', marker='.', label='TWS')
    ax1.plot(df['Time'], df['Gust'], color='lightblue', linestyle='--', marker='x', label='Gust')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    
    # Add labels for TWS
    for x, y in zip(df['Time'], df['TWS']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='blue', fontsize=8, ha='center')
    
    # Add labels for Gust
    for x, y in zip(df['Time'], df['Gust']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='lightblue', fontsize=8, ha='center')
    
    # Secondary axis for TWD
    ax2 = ax1.twinx()
    ax2.set_ylabel('TWD (°)', color='red')
    ax2.plot(df['Time'], df['TWD'], 'r-', marker='.', label='TWD')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Add labels for TWD
    for x, y in zip(df['Time'], df['TWD']):
        ax2.text(x, y + 3, f'{int(y)}', color='red', fontsize=8, ha='center')
    
    # Format x-axis for time only
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    fig.autofmt_xdate()
    
    # Legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    st.pyplot(fig)
else:
    st.write("Upload a CSV file to visualize the weather data.")
