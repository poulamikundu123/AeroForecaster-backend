def get_health_advice(aqi):

    if aqi <= 50:
        return {
            "category": "Good",
            "color": "#00E400",
            "advice": "Air quality is good. Enjoy outdoor activities."
        }

    elif aqi <= 100:
        return {
            "category": "Moderate",
            "color": "#FFFF00",
            "advice": "Sensitive people should limit prolonged outdoor activity."
        }

    elif aqi <= 150:
        return {
            "category": "Unhealthy for Sensitive Groups",
            "color": "#FF7E00",
            "advice": "Children, elderly, and asthma patients should reduce outdoor exposure."
        }

    elif aqi <= 200:
        return {
            "category": "Unhealthy",
            "color": "#FF0000",
            "advice": "Wear an N95 mask and avoid strenuous outdoor activities."
        }

    elif aqi <= 300:
        return {
            "category": "Very Unhealthy",
            "color": "#8F3F97",
            "advice": "Stay indoors whenever possible. Keep windows closed."
        }

    else:
        return {
            "category": "Hazardous",
            "color": "#7E0023",
            "advice": "Avoid going outside. Follow local health advisories."
        }
    

