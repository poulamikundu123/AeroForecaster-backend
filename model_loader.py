import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "aqi_model.pkl"
)

FEATURE_PATH = os.path.join(
    BASE_DIR,
    "models",
    "feature_columns.pkl"
)

print("Loading AQI Model...")

model = joblib.load(MODEL_PATH)

print("Model Loaded Successfully!")

feature_columns = joblib.load(FEATURE_PATH)

print(f"Loaded {len(feature_columns)} Features")