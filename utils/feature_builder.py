import os
import sys
import joblib
import pandas as pd

# ==========================================
# Fix Import Path
# ==========================================

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(BACKEND_DIR)

# ==========================================
# Paths
# ==========================================

FEATURE_COLUMNS_PATH = os.path.join(
    BACKEND_DIR,
    "models",
    "feature_columns.pkl"
)

# ==========================================
# Feature Builder
# ==========================================

def build_feature_vector(aqi_df, weather_df):

    # ------------------------------
    # Convert datetime
    # ------------------------------

    aqi_df["datetime"] = pd.to_datetime(aqi_df["datetime"])
    weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

    # ------------------------------
    # Merge
    # ------------------------------

    df = pd.merge(
        aqi_df,
        weather_df,
        on="datetime",
        how="inner"
    )

    df = df.sort_values("datetime").reset_index(drop=True)

    # ------------------------------
    # Time Features
    # ------------------------------

    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    # ------------------------------
    # Rolling Features
    # ------------------------------

    df["pm25_roll_3"] = df["pm2_5"].rolling(3).mean()
    df["pm25_roll_6"] = df["pm2_5"].rolling(6).mean()

    # ------------------------------
    # Trend Features
    # ------------------------------

    df["pm25_change"] = df["pm2_5"].diff()

    df["temp_change"] = df["temperature"].diff()

    df["wind_change"] = df["wind_speed"].diff()

    # ------------------------------
    # Ratio Features
    # ------------------------------

    df["pm25_pm10_ratio"] = (
        df["pm2_5"] /
        df["pm10"]
    )

    df["no2_so2_ratio"] = (
        df["no2"] /
        df["so2"]
    )

    # ------------------------------
    # Fill Missing Values
    # ------------------------------

    df = df.bfill()

    df = df.ffill()

    # ==========================================
    # Keep only last 24 hours
    # ==========================================

    df = df.tail(24).reset_index(drop=True)

    # ==========================================
    # Features used during training
    # ==========================================

    FEATURES = [

        "pm2_5",
        "pm10",
        "no2",
        "so2",
        "co",
        "o3",

        "temperature",
        "humidity",
        "wind_speed",

        "hour",
        "day_of_week",
        "month",
        "is_weekend",

        "pm25_roll_3",
        "pm25_roll_6",

        "pm25_change",
        "temp_change",
        "wind_change",

        "pm25_pm10_ratio",
        "no2_so2_ratio"

    ]

    # ==========================================
    # Flatten 24x20 -> 480
    # ==========================================

    values = df[FEATURES].values

    flattened = values.flatten().tolist()

    feature_columns = []

    WINDOW_SIZE = 24

    for hour in range(WINDOW_SIZE):

        for feature in FEATURES:

            feature_columns.append(
                f"{feature}_t-{WINDOW_SIZE-hour}"
            )

    sequence_df = pd.DataFrame(
        [flattened],
        columns=feature_columns
    )

    # ==========================================
    # Match training feature order
    # ==========================================

    trained_columns = joblib.load(
        FEATURE_COLUMNS_PATH
    )

    sequence_df = sequence_df[
        trained_columns
    ]

    return sequence_df