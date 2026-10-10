"""Weather forecast tool."""
import requests
import traceback
from typing import Optional

from src.studypilot.config import logger

def _get_weather_description(code: int) -> str:
    if code == 0:
        return "Clear sky"
    elif 1 <= code <= 3:
        return "Partly cloudy / Overcast"
    elif 45 <= code <= 48:
        return "Fog"
    elif 51 <= code <= 55:
        return "Drizzle"
    elif 61 <= code <= 65:
        return "Rain"
    elif 71 <= code <= 75:
        return "Snow"
    elif 80 <= code <= 82:
        return "Showers"
    elif 95 <= code <= 99:
        return "Thunderstorm"
    return "Unknown weather condition"

def weather(city: str) -> str:
    """Get the weather forecast for a city."""
    try:
        # Step 1: Geocode
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return f"City not found: {city}"
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        loc_name = f"{location.get('name')}, {location.get('country')}"
        
        # Step 2: Weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=3"
        weather_resp = requests.get(weather_url, timeout=10)
        weather_resp.raise_for_status()
        w_data = weather_resp.json()
        
        current = w_data.get("current_weather", {})
        temp = current.get("temperature", "N/A")
        code = current.get("weathercode", -1)
        desc = _get_weather_description(code)
        
        daily = w_data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        
        output = [f"Weather for {loc_name}:"]
        output.append(f"Current: {temp}°C, {desc}")
        output.append("Forecast (3 days):")
        
        for i in range(len(dates)):
            date = dates[i]
            t_max = max_temps[i] if i < len(max_temps) else "N/A"
            t_min = min_temps[i] if i < len(min_temps) else "N/A"
            output.append(f" - {date}: High {t_max}°C, Low {t_min}°C")
            
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Weather tool error: {e}\n{traceback.format_exc()}")
        return f"Error fetching weather data: {e}"
