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
    solar_rad:     List[float]
    soil_moisture: List[float]


@app.post("/api/add")
def read_item(hb: Heartbeat):

    et = compute_eto(
        temp       = hb.temp,
        altitude   = -27,
        wind_speed = hb.wind_speed,
        humidity   = hb.humidity,
        precip     = hb.precip,
        solar_rad  = hb.solar_rad
    )

    return {
        "success": True,
        "et": et,
        "schedule": [0, 0]
    }