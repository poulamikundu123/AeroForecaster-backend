import os
import sys
import joblib
import pandas as pd
import numpy as np

# Fix Import Path for local imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from services.geocoding import get_coordinates
from services.aqi_api import get_air_quality
from services.weather_api import get_weather
from utils.feature_builder import build_feature_vector
from health import get_health_advice

# Path configuration
MODEL_PATH = os.path.join(CURRENT_DIR, "models", "aqi_model.pkl")
model = joblib.load(MODEL_PATH)

def make_prediction(city_name: str):
    """
    Coordinates geocoding, Open-Meteo fetches, feature building, 
    and predicts Hour +1 and Hour +2 AQI.
    """
    # 1. Geocoding
    coords = get_coordinates(city_name)
    lat = coords["latitude"]
    lon = coords["longitude"]
    city_resolved = coords["city"]

    # 2. Fetch AQI & Weather
    aqi_df = get_air_quality(lat, lon)
    weather_df = get_weather(lat, lon)

    # Parse and sort by datetime
    aqi_df["datetime"] = pd.to_datetime(aqi_df["datetime"])
    weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

    aqi_df = aqi_df.sort_values("datetime").reset_index(drop=True)
    weather_df = weather_df.sort_values("datetime").reset_index(drop=True)

    # Standardize length to at least 26 rows (24 past + 2 forecast)
    if len(aqi_df) < 26 or len(weather_df) < 26:
        # Fallback to copy last row forward if we don't have enough forecast steps
        while len(aqi_df) < 26:
            last_row = aqi_df.iloc[-1].copy()
            last_row["datetime"] = last_row["datetime"] + pd.Timedelta(hours=1)
            aqi_df = pd.concat([aqi_df, pd.DataFrame([last_row])], ignore_index=True)
        while len(weather_df) < 26:
            last_row = weather_df.iloc[-1].copy()
            last_row["datetime"] = last_row["datetime"] + pd.Timedelta(hours=1)
            weather_df = pd.concat([weather_df, pd.DataFrame([last_row])], ignore_index=True)

    # 3. Extract the "current" values (the last observed historical hour at index 23)
    current_idx = 23
    current_row_aqi = aqi_df.iloc[current_idx]
    current_row_weather = weather_df.iloc[current_idx]

    current_aqi_val = int(current_row_aqi["us_aqi"])

    # 4. Predict Hour +1
    h1_aqi_df = aqi_df.iloc[0:24].copy()
    h1_weather_df = weather_df.iloc[0:24].copy()
    feature_vector_h1 = build_feature_vector(h1_aqi_df, h1_weather_df)
    pred_h1 = int(round(model.predict(feature_vector_h1)[0]))

    # 5. Predict Hour +2
    h2_aqi_df = aqi_df.iloc[1:25].copy()
    h2_weather_df = weather_df.iloc[1:25].copy()
    feature_vector_h2 = build_feature_vector(h2_aqi_df, h2_weather_df)
    pred_h2 = int(round(model.predict(feature_vector_h2)[0]))

    # 6. Generate Trend
    diff = pred_h2 - pred_h1
    if diff > 1:
        trend = "Increasing"
    elif diff < -1:
        trend = "Decreasing"
    else:
        trend = "Stable"

    # 7. Generate Health Advice
    health_info = get_health_advice(current_aqi_val)
    health_category = health_info["category"]

    recommendations_map = {
        "Good": [
            "Air quality is satisfactory. Safe for all outdoor activities.",
            "Great time to ventilate your home and open windows."
        ],
        "Moderate": [
            "Sensitive groups (children, elderly, asthma sufferers) should reduce prolonged outdoor activities.",
            "Keep windows closed during peak traffic or pollution hours if you feel irritation."
        ],
        "Unhealthy for Sensitive Groups": [
            "Sensitive groups should limit outdoor exertion and avoid strenuous activities.",
            "Keep windows closed during peak pollution hours to protect indoor air."
        ],
        "Unhealthy": [
            "Everyone should wear an N95 mask if spending time outdoors.",
            "Avoid vigorous outdoor exercise. Limit exposure.",
            "Keep windows closed and run an air purifier if available."
        ],
        "Very Unhealthy": [
            "Avoid all outdoor activities. Stay indoors as much as possible.",
            "Keep windows and doors closed. Use air purifiers on high speed.",
            "Sensitive groups should strictly remain in clean indoor environments."
        ],
        "Hazardous": [
            "Avoid going outside entirely. Air quality is extremely dangerous.",
            "Keep all windows, doors, and ventilation systems closed.",
            "Follow local emergency health guidelines and instructions."
        ]
    }
    recommendations = recommendations_map.get(health_category, [
        "Monitor local air quality index updates.",
        "Take appropriate precautions based on your sensitivity level."
    ])

    return {
        "city": city_resolved,
        "current_aqi": current_aqi_val,
        "predicted_hour_1": pred_h1,
        "predicted_hour_2": pred_h2,
        "trend": trend,
        "health_category": health_category,
        "recommendation": recommendations,
        "pollutants": {
            "pm2_5": float(current_row_aqi["pm2_5"]),
            "pm10": float(current_row_aqi["pm10"]),
            "no2": float(current_row_aqi["no2"]),
            "so2": float(current_row_aqi["so2"]),
            "co": float(current_row_aqi["co"]),
            "o3": float(current_row_aqi["o3"])
        },
        "weather": {
            "temperature": float(current_row_weather["temperature"]),
            "humidity": float(current_row_weather["humidity"]),
            "wind_speed": float(current_row_weather["wind_speed"])
        }
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        city = sys.argv[1]
    else:
        city = "Kolkata"
    try:
        res = make_prediction(city)
        print("Prediction succeeded!")
        import json
        print(json.dumps(res, indent=4))
    except Exception as e:
        print("Prediction failed:", e)
