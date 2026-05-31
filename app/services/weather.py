"""
Serviço de clima — Open-Meteo API
Sem chave API, completamente gratuita.
Docs: https://open-meteo.com/en/docs
"""
import httpx
from app.config import settings

# Códigos WMO → descrição em português
WMO_DESCRIPTIONS = {
    0:  "Céu limpo",
    1:  "Maioritariamente limpo",
    2:  "Parcialmente nublado",
    3:  "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com geada",
    51: "Chuvisco leve",
    53: "Chuvisco moderado",
    55: "Chuvisco intenso",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve forte",
    80: "Aguaceiros leves",
    81: "Aguaceiros moderados",
    82: "Aguaceiros fortes",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte",
}


async def get_current_weather() -> dict:
    """Obtém clima atual no campus via Open-Meteo."""
    params = {
        "latitude":  settings.CAMPUS_LATITUDE,
        "longitude": settings.CAMPUS_LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "uv_index",
        ],
        "wind_speed_unit": "kmh",
        "timezone": "Europe/Lisbon",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.OPEN_METEO_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]
    code = current.get("weather_code", 0)

    return {
        "temperature":          current["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "humidity":             current["relative_humidity_2m"],
        "precipitation":        current["precipitation"],
        "wind_speed":           current["wind_speed_10m"],
        "wind_direction":       current["wind_direction_10m"],
        "uv_index":             current.get("uv_index", 0),
        "weather_code":         code,
        "description":          WMO_DESCRIPTIONS.get(code, "Desconhecido"),
        "timestamp":            current["time"],
    }


async def get_forecast() -> dict:
    """Previsão para os próximos 3 dias."""
    params = {
        "latitude":  settings.CAMPUS_LATITUDE,
        "longitude": settings.CAMPUS_LONGITUDE,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weather_code",
            "wind_speed_10m_max",
        ],
        "timezone":   "Europe/Lisbon",
        "forecast_days": 3,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.OPEN_METEO_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data["daily"]
    days = []
    for i in range(len(daily["time"])):
        code = daily["weather_code"][i]
        days.append({
            "date":            daily["time"][i],
            "temp_max":        daily["temperature_2m_max"][i],
            "temp_min":        daily["temperature_2m_min"][i],
            "precipitation":   daily["precipitation_sum"][i],
            "wind_speed_max":  daily["wind_speed_10m_max"][i],
            "weather_code":    code,
            "description":     WMO_DESCRIPTIONS.get(code, "Desconhecido"),
        })

    return {"forecast": days}