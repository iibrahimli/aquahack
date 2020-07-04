import numpy as np


def compute_eto(day,
                month,
                year,
                latitude,
                altitude,
                temp,
                wind_speed,
                humidity):
    """
    Compute reference evapotranspiration

     * ET calculation procedure: http://www.fao.org/3/x0490e/x0490e08.htm
     * Equations:                http://www.fao.org/3/x0490e/x0490e07.htm
     * Meteorological tables:    http://www.fao.org/3/x0490e/x0490e0j.htm

    Args:
        day (int): Day of month
        month (int): Month
        year (int): Year
        latitude (float): Latitude (deg)
        altitude (float): Altitude of the station (m)
        temp ([float]): Temperature (C)
        wind_speed ([float]): Wind speed (m/s)
        humidity ([float]): Humidity (%)
    
    Returns:
        float: ETo (mm/day)
    """

    """
    test: (Brussels, 100 m, 6 July 2019, sunshine_hours = 9.25)
    {
        "station_id": "string",
        "datetime": "string",
        "temp": [
            12.3, 21.5
        ],
        "wind_speed": [
            2.77778, 2.77778
        ],
        "humidity": [
            63, 84
        ],
        "precip": [
            0, 0, 0
        ],
        "solar_rad": [
            0, 0, 0
        ],
        "soil_moisture": [
            0, 0, 0
        ]
    }
    result: 3.8752704372798217
    """

    sunshine_hours = 9.25     # hours
    pressure       = 101.592  # kPa
    gamma          = 0.067    # kPa/C

    temp       = np.array(temp)
    wind_speed = np.array(wind_speed)
    humidity   = np.array(humidity)

    mean_temp    = temp.mean()
    min_temp     = temp.min()
    max_temp     = temp.max()
    min_humidity = humidity.min()
    max_humidity = humidity.max()

    # convert wind speed to measured at 2 m
    wind_measure_height = 10
    mean_wind_speed = wind_speed.mean() * 4.87 \
                      / np.log(67.8 * wind_measure_height - 5.42)

    # saturated vapor pressure (converted to kPa)
    sv_pressure = 0.6108 * np.exp((17.27 * temp) / (237.3 + temp))
    min_temp_idx, max_temp_idx = temp.argmin(), temp.argmax()
    sv_pressure_at_tmin = sv_pressure[min_temp_idx]
    sv_pressure_at_tmax = sv_pressure[max_temp_idx]
    mean_sv_pressure = (sv_pressure_at_tmin + sv_pressure_at_tmax) / 2

    # vapor pressure deficit
    e_s = (sv_pressure_at_tmin + sv_pressure_at_tmax) / 2
    e_a = (sv_pressure_at_tmin * max_humidity / 100 \
           + sv_pressure_at_tmax * min_humidity / 100) / 2
    vp_deficit = e_s - e_a

    # saturation vapor pressure slope
    vp_slope = 4098 * (0.6108 * np.exp((17.27 * mean_temp) / (mean_temp + 237.3))) \
               / (mean_temp + 237.3)**2
    
    # radiation
    J = int(275 * (month / 9) - 30 + day) - 2
    if month < 3: J += 2
    # TODO: actually check leap year
    if year % 4 == 0 and month > 2: J += 1
    d_r = 1 + 0.033 * np.cos(2 * np.pi / 365 * J)
    sigma = 0.409 * np.sin(2 * np.pi / 365 * J - 1.39)
    latitude_rad = np.pi / 180 * latitude
    w_s = np.arccos(-np.tan(latitude_rad) * np.tan(sigma))
    daylight_hours = (24 / np.pi) * w_s
    R_a = ((24 * 60) / np.pi) * 0.0820 * d_r \
          * (w_s * np.sin(latitude_rad) * np.sin(sigma) \
             + np.cos(latitude_rad) * np.cos(sigma) * np.sin(w_s))
    R_s = (0.25 + 0.50 * sunshine_hours / daylight_hours) * R_a
    R_so = (0.75 + 2 * 1e-5 * altitude) * R_a
    R_ns = (1 - 0.23) * R_s
    sigma_min_temp = 4.903 * 1e-9 * (min_temp + 273.16)**4
    sigma_max_temp = 4.903 * 1e-9 * (max_temp + 273.16)**4
    R_nl = (sigma_min_temp + sigma_max_temp) / 2 * (0.34 - 0.14 * np.sqrt(e_a)) \
           * (1.35 * R_s / R_so - 0.35)
    R_n = R_ns - R_nl
    G = 0

    eto = (0.408 * vp_slope * (R_n - G) \
           + gamma * 900 / (mean_temp + 273) * mean_wind_speed * vp_deficit) \
          / \
          (vp_slope + gamma * (1 + 0.34 * mean_wind_speed))

    return eto