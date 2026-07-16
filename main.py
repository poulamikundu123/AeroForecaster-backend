from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from predict import make_prediction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aqi_backend")

app = FastAPI(
    title="AQI Prediction API",
    description="FastAPI Backend for AI-powered Air Quality Index Forecasting",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development and demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    city: str

@app.get("/")
def read_root():
    return {"message": "AQI Prediction API Running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "Random Forest Regressor",
        "features_count": 480
    }

@app.post("/predict")
def predict_aqi(payload: PredictionRequest):
    city = payload.city.strip()
    if not city:
        raise HTTPException(status_code=400, detail="City name cannot be empty.")
    
    try:
        logger.info(f"Predicting AQI for city: {city}")
        result = make_prediction(city)
        return result
    except Exception as e:
        logger.error(f"Error forecasting AQI for {city}: {str(e)}")
        # If city is not found (raised from geocoding), return 404
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
