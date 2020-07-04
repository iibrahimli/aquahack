import uuid
import base64
import datetime
from os.path import join
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

np.random.seed(42)


# ============= initialize stuff =============


DATA_PATH = "../data/"

# measured data
MEASUREMENT_LABELS = [
    'temperature (C)',
    'wind speed (m/s)',
    'humidity (%)',
    'precipitation (mm)',
    'soil moisture (%)',
]
N_SENSORS = len(MEASUREMENT_LABELS)
MEASUREMENT_MEANS = [
    27,   # temperature
    3,    # wind speed
    60,   # humidity
    0,    # precipitation
    32,   # soil moisture
]
MEASUREMENT_STDS = [
    7,    # temperature
    6,    # wind speed
    7,    # humidity
    3,    # precipitation
    7,    # soil moisture    
]
MEASUREMENT_LIMITS = [
    (-100, 100),  # temperature
    (0, None),    # wind speed
    (0, 100),     # humidity
    (0, None),    # precipitation
    (0, 100),     # soil moisture
]

# interval between measurements - 1 hour
SENSOR_DELTA_T = '1H'


# ============= utility functions =============


def random_id():
    alphabet = [c for c in string.ascii_lowercase + string.digits]
    return ''.join(np.random.choice(alphabet, size=8))


@st.cache
def generate_stations(n_stations):
    """
    Generate random stations

    Returns:
        pd.DataFrame with columns 'id', 'region', 'lat', 'lon'
    """

    regions_df = pd.read_csv(join(DATA_PATH, "cities.tsv"), sep='\t')
    latlon_df = regions_df[['lat', 'lon']].sample(n=n_stations, replace=True) \
                + np.random.randn(n_stations, 2) * 0.05
    df = pd.DataFrame({
        'id': [random_id() for _ in range(n_stations)],
        'region': regions_df['name'].sample(n=n_stations, replace=True).to_numpy(),
        **latlon_df.reset_index(),
        'alt': np.random.uniform(-30, 200, size=n_stations)
    }).drop('index', axis='columns')
    return df


def generate_station_df(n_samples, delta_t,
                        n_sensors=N_SENSORS,
                        means=None, stds=None, limits=None):
    """
    Generate normally distributed fake data for a station

    Args:
        n_samples (int): Number of samples
        delta_t (dt): Time interval between measurements
        n_sensors (int): Number of sensors per sample
        means (list(float)): Mean of each sensor, optional
        stds (list(float)): Std of each sensor, optional
        limits (list(tuple([float, None]))): Limits of each sensor
    
    Returns:
        pd.DataFrame with station time series
    """

    if means is None:
        means = [0] * n_sensors
    if stds is None:
        stds = [1] * n_sensors
    vals = np.random.randn(n_samples, n_sensors) * stds + means
    for i in range(len(limits)):
        vals[:, i] = np.clip(vals[:, i], *limits[i])
    station_df = pd.DataFrame(
        vals,
        columns=MEASUREMENT_LABELS
    )
    station_df['dt'] = pd.date_range(end=datetime.datetime.now().strftime('%Y/%m/%d'),
                                     periods=n_samples,
                                     freq=delta_t)
    return station_df


@st.cache
def get_stations_avg(stations_df, stations_data):
    """
    Get averages for each station

    Returns:
        pd.DataFrame of means
    """

    # calculate means
    means = np.empty(shape=(len(stations_df), N_SENSORS))
    for i, station_id in enumerate(stations_df['id']):
        means[i, :] = stations_data[station_id].mean(axis=0)
    means_df = pd.DataFrame(means, columns=MEASUREMENT_LABELS)

    means_df = pd.DataFrame({
        'id': stations_df['id'].to_numpy(),
        'region': stations_df['region'].to_numpy(),
        **means_df
    })

    return means_df


def get_table_download_link(df):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    Args:
        df (dataframe)
    
    Returns:
        href string
    """

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV file</a>'
    return href


# ============= generate fake data =============

n_stations = 12
n_samples = 24 * 7

# station names & locations
stations_df = generate_stations(n_stations)
# stations_df.to_csv(join(DATA_PATH, "stations.csv"), index=False)

# last n_samples samples from station time series
stations_data = {
    station_id: generate_station_df(
        n_samples, SENSOR_DELTA_T,
        means=MEASUREMENT_MEANS,
        stds=MEASUREMENT_STDS,
        limits=MEASUREMENT_LIMITS
    )
    for station_id in stations_df['id']
}

sd = next(iter(stations_data.values()))
start_dt = sd['dt'].min()
end_dt = sd['dt'].max()

# averages
station_avgs = get_stations_avg(stations_df, stations_data)


# ============= visualize =============


st.title("Satet Demo")
st.markdown("This is a prototype of the Satet agricultural data collection "
            "platform. Each deployed station is identified by a unique "
            "alphanumeric ID. Stations regularly submit meteorological "
            "measurements in an automated fashion.")
st.markdown("You can use the sidebar on the left to download the data for "
            "any station shown here.")


# sidebar - import/export
st.sidebar.title("Data")
st.sidebar.markdown("You can import or export the data as CSV. "
                    "Choose a station, click 'Export as CSV' "
                    "and a download link will appear")
export_station = st.sidebar.selectbox(
    "Choose a station to export",
    options=list(range(n_stations)),
    format_func=lambda idx:
        f"{stations_df.loc[idx, 'id']} ({stations_df.loc[idx, 'region']})"
)
selected_station_id = stations_df.loc[export_station, 'id']
selected_station_df = stations_data[selected_station_id]

if st.sidebar.button("Export as CSV"):
    st.sidebar.markdown(get_table_download_link(selected_station_df),
                           unsafe_allow_html=True)


# map with stations
st.header("Deployed stations")
st.map(
    data=stations_df,
    zoom=6
)
st.write(f"Total: {n_stations} stations")


# table with means
st.header("Average values")
st.markdown(f"Calculated for last {n_samples} measurements.")
st.markdown(f"Collection period:  {start_dt} - {end_dt}")
st.markdown(
    "Minimum in <span style=\"color:red\">red</span>, "
    "maximum in <span style=\"color:green\">green</span>",
    unsafe_allow_html=True
)
st.dataframe(
    station_avgs.style
    .highlight_max(color='#AAFFAA')
    .highlight_min(color='#FFAAAA')
)


# past data plot
st.header("Past data")

# select station
selected_station_index = st.selectbox(
    "Choose a station",
    options=list(range(n_stations)),
    format_func=lambda idx:
        f"{stations_df.loc[idx, 'id']} ({stations_df.loc[idx, 'region']})"
)
selected_station_id = stations_df.loc[selected_station_index, 'id']
selected_station_df = stations_data[selected_station_id]

# select sensors
selected_sensors = st.multiselect(
    "Select measurements to plot (default: all)",
    options=MEASUREMENT_LABELS,
)
# if empty, display all
if not selected_sensors:
    selected_sensors = MEASUREMENT_LABELS

# select datetime range
dt_range = st.date_input(
    "Select date range to plot",
    value=[selected_station_df['dt'].min(), selected_station_df['dt'].max()],
    min_value=selected_station_df['dt'].min(),
    max_value=selected_station_df['dt'].max()
)

past_chart = st.empty()

past_df = selected_station_df[['dt'] + selected_sensors].set_index('dt')

dt_range = list(dt_range)
if len(dt_range) < 2:
    past_chart.markdown("Please select a valid date range (you can select "
                        "the same day as start and end date)")
else:
    if dt_range[0] == dt_range[1]:
        dt_range[1] += datetime.timedelta(days=1)

    start_dt = past_df.index.get_loc(dt_range[0], method='nearest')
    end_dt   = past_df.index.get_loc(dt_range[1], method='nearest')

    past_chart.line_chart(
        past_df.iloc[start_dt:end_dt],
    )