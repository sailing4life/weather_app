import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.colors as mcolors

st.title("Weather Data Visualization App")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    # Read CSV, replace ° symbol from columns
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.replace('°', 'deg')

    # Parse time column
    df['Time'] = pd.to_datetime(df['W. Europe Daylight Time'], utc=True, errors='coerce')
    df = df.dropna(subset=['Time'])

    # Show columns for user info
    st.write("Columns detected:")
    st.write(df.columns.tolist())

    # Input model name
    model_name = st.text_input("Enter model name:", "UM-Global")

    # Select time range to display
    min_time = df['Time'].min()
    max_time = df['Time'].max()
    start_time, end_time = st.slider(
        "Select time range to display:",
        min_value=min_time,
        max_value=max_time,
        value=(min_time, max_time),
        format="YYYY-MM-DD HH:mm"
    )

    # Filter data by time range
    df_filtered = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]

    # Prepare columns for plotting
    df_filtered['TWS'] = pd.to_numeric(df_filtered['kt'], errors='coerce')
    df_filtered['TWD'] = pd.to_numeric(df_filtered['Wind10m deg'], errors='coerce')
    df_filtered['Gust'] = pd.to_numeric(df_filtered['kt.3'], errors='coerce')

    # Drop rows with missing TWS or TWD or Gust
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

    # Labels for TWS points
    for x, y in zip(df_filtered['Time'], df_filtered['TWS']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='blue', fontsize=8, ha='center')

    # Labels for Gust points
    for x, y in zip(df_filtered['Time'], df_filtered['Gust']):
        ax1.text(x, y + 0.3, f'{y:.1f}', color='lightblue', fontsize=8, ha='center')

    ax2 = ax1.twinx()
    ax2.set_ylabel('TWD (°)', color='red')
    ax2.plot(df_filtered['Time'], df_filtered['TWD'], 'r-', marker='.', label='TWD')
    ax2.tick_params(axis='y', labelcolor='red')

    # Labels for TWD points
    for x, y in zip(df_filtered['Time'], df_filtered['TWD']):
        ax2.text(x, y + 3, f'{int(y)}', color='red', fontsize=8, ha='center')

    # Format X-axis: only date and time
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()

    st.pyplot(fig)

    # Data Table with color gradient on TWS
    st.subheader("Filtered Data Table")
    display_df = df_filtered[['Time', 'TWS', 'TWD', 'Gust']].copy()
    display_df['Time'] = display_df['Time'].dt.strftime('%Y-%m-%d %H:%M')

    cmap = mcolors.LinearSegmentedColormap.from_list('blue_green_red', ['blue', 'green', 'red'])
    styled_df = display_df.style.background_gradient(cmap=cmap, subset=['TWS'], axis=0, vmin=display_df['TWS'].min(), vmax=display_df['TWS'].max())

    st.dataframe(styled_df)

else:
    st.info("Please upload a CSV file to start.")
