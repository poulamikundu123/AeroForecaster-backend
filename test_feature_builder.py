from services.aqi_api import get_air_quality
from services.weather_api import get_weather
from utils.feature_builder import build_feature_vector

aqi = get_air_quality(
    22.5726,
    88.3639
)

weather = get_weather(
    22.5726,
    88.3639
)

feature_vector = build_feature_vector(
    aqi,
    weather
)

print(feature_vector.head())

print("\nShape:")
print(feature_vector.shape)