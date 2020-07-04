import numpy as np
import pandas as pd
from datetime import datetime
import dateutil.parser
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
    # soil_moisture: List[float]\


class UnknownStationError(Exception):
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.message = f"unknown station id: {station_id}"
        super().__init__(self.message)


def get_station_loc(station_id):
    stations_df = pd.read_csv("../data/stations.csv")
    if bool(stations_df['id'].isin([station_id]).any()) is False:
        raise UnknownStationError(station_id)
    lat = stations_df.loc[stations_df['id'] == station_id, 'lat'].item()
    lon = stations_df.loc[stations_df['id'] == station_id, 'lon'].item()
    alt = stations_df.loc[stations_df['id'] == station_id, 'alt'].item()
    return lat, lon, alt


@app.post("/api/add")
async def add(hb: Heartbeat):

    try:
        lat, _, alt = get_station_loc(hb.station_id)

        # parse datetime
        # dt = datetime.strptime(hb.datetime, '%Y-%m-%dT%H:%M:%S.%f')
        dt = dateutil.parser.isoparse(hb.datetime)
        day = dt.day
        month = dt.month
        year = dt.year

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
        return {
            "success": False,
            "error": str(e)
        }

    return {
        "success": True,
        "et": eto,
        "schedule": [0,]
    }