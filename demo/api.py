import numpy as np
import pandas as pd
from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel

from model import compute_eto


app = FastAPI()


class Heartbeat(BaseModel):
    station_id:    str
    datetime:      str
    temp:          List[float]
    wind_speed:    List[float]
    humidity:      List[float]
    precip:        List[float]
    # soil_moisture: List[float]


def get_station_loc(station_id):
    stations_df = pd.read_csv("../data/stations.csv")
    lat = stations_df.loc[stations_df['id'] == station_id, 'lat'].item()
    lon = stations_df.loc[stations_df['id'] == station_id, 'lon'].item()
    alt = stations_df.loc[stations_df['id'] == station_id, 'alt'].item()
    return lat, lon, alt


@app.post("/api/add")
def read_item(hb: Heartbeat):

    try:
        lat, _, alt = get_station_loc(hb.station_id)

        # parse datetime
        day = 6
        month = 7
        year = 2020

        eto = compute_eto(
            day        = day,
            month      = month,
            year       = year,
            latitude   = lat,
            altitude   = alt,
            temp       = hb.temp,
            wind_speed = hb.wind_speed,
            humidity   = hb.humidity
        )
    except Exception as e:
        print(e)
        return {
            "success": False
        }

    return {
        "success": True,
        "et": eto,
        "schedule": [0,]
    }