import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time
import matplotlib.colors as mcolors

st.title("Weather Data Visualization App")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.replace('°', 'deg')

    if 'W. Europe Daylight Time' in df.columns:
        # Parse time column with your method
        df['Time'] = pd.to_datetime(df['W. Europe Daylight Time'], errors='coerce')
        df = df.dropna(subset=['Time'])

        st.write("Columns detected:")
        st.write(df.columns.tolist())

        model_name = st.text_input("Enter model name:", "UM-Global")

        # Date filter UI
        st.subheader("Date Filter")
        min_date = df['Time'].dt.date.min()
        max_date = df['Time'].dt.date.max()
        date_range = st.date_input("Select date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

        # Time filter UI
        st.subheader("Time Filter")
        start_time = st.time_input("Start time", value=time(8, 0))
        end_time = st.time_input("End time", value=time(20, 0))

        # Filter by date range
        if isinstance(date_range, (tuple, list)):
            start_date, end_date = date_range
            df_filtered = df[(df['Time'].dt.date >= start_date) & (df['Time'].dt.date <= end_date)]
        else:
            df_filtered = df[df['Time'].dt.date == date_range]

        # Filter by time of day
        df_filtered = df_filtered[df_filtered['Time'].dt.time.between(start_time, end_time)]

        # Prepare columns for plotting
        df_filtered['TWS'] = pd.to_numeric(df_filtered['kt'], errors='coerce')
        df_filtered['TWD'] = pd.to_numeric(df_filtered['Wind10m deg'], errors='coerce')
        df_filtered['Gust'] = pd.to_numeric(df_filtered['kt.3'], errors='coerce')
        df_filtered = df_filtered.dropna(subset=['TWS', 'TWD', 'Gust'])

        # Plotting
        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.set_title(f'TWS/Direction - Model: {model_name}', fontsize=14)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('TWS / Gust (kt)', color='blue')

        ax1.plot(df_filtered['Time'], df_filtered['TWS'], 'b-', marker='.', label='TWS')
        ax1.plot(df_filtered['Time'], df_filtered['Gust'], color='lightblue', linestyle='--', marker='x', label='Gust')

        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)

        for x, y in zip(df_filtered['Time'], df_filtered['TWS']):
            ax1.text(x, y + 0.3, f'{y:.1f}', color='blue', fontsize=8, ha='center')

        for x, y in zip(df_filtered['Time'], df_filtered['Gust']):
            ax1.text(x, y + 0.3, f'{y:.1f}', color='lightblue', fontsize=8, ha='center')

        ax2 = ax1.twinx()
        ax2.set_ylabel('TWD (°)', color='red')
        ax2.plot(df_filtered['Time'], df_filtered['TWD'], 'r-', marker='.', label='TWD')
        ax2.tick_params(axis='y', labelcolor='red')

        for x, y in zip(df_filtered['Time'], df_filtered['TWD']):
            ax2.text(x, y + 3, f'{int(y)}', color='red', fontsize=8, ha='center')

        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()

        st.pyplot(fig)

        # Data Table with color gradient on TWS
        st.subheader("Filtered Data Table")
        display_df = df_filtered[['Time', 'TWS', 'TWD', 'Gust']].copy()
        display_df['Time'] = display_df['Time'].dt.strftime('%Y-%m-%d %H:%M')

        cmap = mcolors.LinearSegmentedColormap.from_list('blue_green_red', ['blue', 'green', 'red'])
        styled_df = display_df.style.background_gradient(
            cmap=cmap,
            subset=['TWS'],
            axis=0,
            vmin=display_df['TWS'].min(),
            vmax=display_df['TWS'].max()
        )

        st.dataframe(styled_df)

    else:
        st.error("CSV must contain the 'W. Europe Daylight Time' column.")

else:
    st.info("Please upload a CSV file to start.")
