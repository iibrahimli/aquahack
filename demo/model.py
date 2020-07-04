import numpy as np


# def compute_eto(temp,
#                 wind_speed,
#                 humidity,
#                 precip,
#                 solar_rad):
#     """
#     Compute reference evapotranspiration
#     http://www.fao.org/3/x0490e/x0490e08.htm

#     Args:
#         temp ([float]): Temperature (C)
#         wind_speed ([float]): Wind speed (m/s)
#         humidity ([float]): Humidity (%)
#         precip ([float]): Precipitation (mm/hour)
    
#     Returns:
#         float: ETo (mm/hour)
#     """

#     temp       = np.array(temp)
#     wind_speed = np.array(wind_speed)
#     humidity   = np.array(humidity)
#     precip     = np.array(precip)
#     solar_rad  = np.array(solar_rad)

#     mean_temp = temp.mean()
#     mean_wind_speed = wind_speed.mean()
#     # Net solar radiation (W/m^2)
#     # https://solrad-net.gsfc.nasa.gov/cgi-bin/type_one_station_flux?site=Barcelona&nachal=0&year=27&month=6&day=3&aero_water=0&level=1&if_day=0&shef_code=P&year_or_month=0
#     mean_solar_rad = solar_rad.mean()
    
#     # psychrometry constant at sea level (converted to kPa/C)
#     # http://ponce.sdsu.edu/psychrometric_constant.html
#     gamma = 0.0655

#     # saturated vapor pressure (converted to kPa)
#     # https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
#     sv_pressure = 0.1 * 6.11 * 10**((7.5 * temp) / (237.3 + temp))

#     # http://www.fao.org/3/X0490E/x0490e07.htm
#     min_temp_idx, max_temp_idx = temp.argmin(), temp.argmax()
#     mean_sv_pressure = (sv_pressure[min_temp_idx] + sv_pressure[max_temp_idx]) / 2

#     # slope of sv pressure - temp curve (kPa/C)
#     # http://www.fao.org/3/X0490E/x0490e0k.htm
#     mean_sv_slope = (4098 * mean_sv_pressure) / (mean_temp + 237.3)**2

#     eto = (0.408 * mean_sv_slope * solar_rad \
#            + gamma * (900 / mean_temp + 273.3) \
#              * mean_wind_speed * mean_sv_pressure) \
#           / (mean_sv_slope + gamma * (1 + 0.34 * mean_wind_speed))

#     print(eto)

#     return float(eto)


def compute_eto(temp,
                altitude,
                wind_speed,
                humidity,
                precip,
                solar_rad):
    """
    Compute reference evapotranspiration
    http://www.fao.org/3/x0490e/x0490e08.htm
    EXAMPLE 18. Determination of ETo with daily data

    Args:
        temp ([float]): Temperature (C)
        altitude (float): Altitude of the station (m)
        wind_speed ([float]): Wind speed (m/s)
        humidity ([float]): Humidity (%)
        precip ([float]): Precipitation (mm/hour)
    
    Returns:
        float: ETo (mm/day)
    """

    temp       = np.array(temp)
    wind_speed = np.array(wind_speed)
    humidity   = np.array(humidity)
    precip     = np.array(precip)
    solar_rad  = np.array(solar_rad)

    mean_temp, min_temp, max_temp = temp.mean(), temp.min(), temp.max()
    min_humidity, max_humidity = humidity.min(), humidity.max()
    mean_wind_speed = wind_speed.mean()
    hours_of_sun = 10   # hours
    pressure = 101.592  # kPa
    sv_slope = 0.122    # kPa/C
    

    

    # Net solar radiation (W/m^2)
    # https://solrad-net.gsfc.nasa.gov/cgi-bin/type_one_station_flux?site=Barcelona&nachal=0&year=27&month=6&day=3&aero_water=0&level=1&if_day=0&shef_code=P&year_or_month=0
    mean_solar_rad = solar_rad.mean()
    
    # psychrometry constant at sea level (converted to kPa/C)
    # http://ponce.sdsu.edu/psychrometric_constant.html
    gamma = 0.0655

    # saturated vapor pressure (converted to kPa)
    # https://www.weather.gov/media/epz/wxcalc/vaporPressure.pdf
    sv_pressure = 0.1 * 6.11 * 10**((7.5 * temp) / (237.3 + temp))

    # http://www.fao.org/3/X0490E/x0490e07.htm
    min_temp_idx, max_temp_idx = temp.argmin(), temp.argmax()
    mean_sv_pressure = (sv_pressure[min_temp_idx] + sv_pressure[max_temp_idx]) / 2

    # slope of sv pressure - temp curve (kPa/C)
    # http://www.fao.org/3/X0490E/x0490e0k.htm
    mean_sv_slope = (4098 * mean_sv_pressure) / (mean_temp + 237.3)**2

    # FAO Penman-Monteith
    eto = (0.408 * mean_sv_slope * solar_rad \
           + gamma * (900 / mean_temp + 273.3) \
             * mean_wind_speed * mean_sv_pressure) \
          / (mean_sv_slope + gamma * (1 + 0.34 * mean_wind_speed))

    print(eto)

    return float(eto)