import requests
import pandas as pd
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(BACKEND_DIR)

from config import (
    WEATHER_URL,
    PAST_HOURS,
    FORECAST_HOURS,
    TIMEZONE
)


def get_weather(latitude, longitude):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "hourly":
        "temperature_2m,relative_humidity_2m,wind_speed_10m",

        "past_hours": PAST_HOURS,

        "forecast_hours": FORECAST_HOURS,

        "timezone": TIMEZONE

    }

    response = requests.get(
        WEATHER_URL,
        params=params
    )

    if response.status_code != 200:
        raise Exception("Unable to fetch weather data.")

    data = response.json()

    hourly = data["hourly"]

    df = pd.DataFrame({

        "datetime": hourly["time"],

        "temperature": hourly["temperature_2m"],

        "humidity": hourly["relative_humidity_2m"],

        "wind_speed": hourly["wind_speed_10m"]

    })

    return df


if __name__ == "__main__":

    df = get_weather(
        22.5726,
        88.3639
    )

    print(df.head())