import uuid 
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
    'sv pressure (kPa)',        # saturation vapor pressure
    'solar radiation (W/m^2)',
    'soil moisture (%)',
]
N_SENSORS = len(MEASUREMENT_LABELS)
MEASUREMENT_MEANS = [
    27,   # temperature
    3,    # wind speed
    60,   # humidity
    0,    # precipitation
    1,    # sv pressure
    11,   # solar radiation
    32,   # soil moisture
]
MEASUREMENT_STDS = [
    5,    # temperature
    6,    # wind speed
    12,   # humidity
    3,    # precipitation
    0.1,  # sv pressure
    2,    # solar radiation
    10,   # soil moisture    
]
MEASUREMENT_LIMITS = [
    (-100, 100),  # temperature
    (0, None),    # wind speed
    (0, 100),     # humidity
    (0, None),    # precipitation
    (0, None),    # sv pressure
    (0, None),    # solar radiation
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


# ============= generate fake data =============

n_stations = 12
n_samples = 24

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


st.title("Aquahack Demo")
st.sidebar.title("Selected Region")
st.markdown("Text 1")
st.sidebar.markdown("Text 2")

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

# select region
selected_region_index = st.selectbox(
    "Choose a station",
    options=list(range(n_stations)),
    format_func=lambda idx:
        f"{stations_df.loc[idx, 'id']} ({stations_df.loc[idx, 'region']})"
)
selected_region_id = stations_df.loc[selected_region_index, 'id']
selected_region_df = stations_data[selected_region_id]

# select sensors
selected_sensors = st.multiselect(
    "Select measurements to plot",
    options=MEASUREMENT_LABELS,
)
# if empty, display all
if not selected_sensors:
    selected_sensors = MEASUREMENT_LABELS
st.line_chart(
    selected_region_df[['dt'] + selected_sensors].set_index('dt'),
)