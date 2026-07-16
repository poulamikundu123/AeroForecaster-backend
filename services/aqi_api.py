import requests
import pandas as pd
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(BACKEND_DIR)

from config import (
    AQI_URL,
    PAST_HOURS,
    FORECAST_HOURS,
    TIMEZONE
)


def get_air_quality(latitude, longitude):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "hourly":
        "pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,ozone,carbon_monoxide,us_aqi",

        "past_hours": PAST_HOURS,

        "forecast_hours": FORECAST_HOURS,

        "timezone": TIMEZONE

    }

    response = requests.get(
        AQI_URL,
        params=params
    )

    if response.status_code != 200:
        raise Exception("Unable to fetch AQI data.")

    data = response.json()

    hourly = data["hourly"]

    df = pd.DataFrame({

        "datetime": hourly["time"],

        "pm2_5": hourly["pm2_5"],

        "pm10": hourly["pm10"],

        "no2": hourly["nitrogen_dioxide"],

        "so2": hourly["sulphur_dioxide"],

        "o3": hourly["ozone"],

        "co": hourly["carbon_monoxide"],

        "us_aqi": hourly["us_aqi"]

    })

    return df


if __name__ == "__main__":

    df = get_air_quality(
        22.5726,
        88.3639
    )

    print(df.head())