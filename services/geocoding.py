import requests

import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(BACKEND_DIR)

from config import GEOCODING_URL


def get_coordinates(city):

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(GEOCODING_URL, params=params)

    if response.status_code != 200:
        raise Exception("Unable to connect to Geocoding API.")

    data = response.json()

    if "results" not in data:
        raise Exception(f"City '{city}' not found.")

    location = data["results"][0]

    return {
        "city": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    }


if __name__ == "__main__":

    city = input("Enter City: ")

    result = get_coordinates(city)

    print(result)