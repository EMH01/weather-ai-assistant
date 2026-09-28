import json
from typing import Any

from .models import HistoricalWeatherDay, WeatherSnapshot
from .time_utils import local_time_from_offset

SYSTEM_INSTRUCTIONS = """You are a weather assistant.
Answer only weather-related questions using the supplied weather context.
Do not invent measurements or forecasts that are not present in the context.
Reply in the same language as the user's question.
If the available context is insufficient, explain what information is missing."""


def weather_context(
    snapshot: WeatherSnapshot,
    historical: HistoricalWeatherDay | None = None,
) -> dict[str, object]:
    local_observed = local_time_from_offset(
        snapshot.timezone_offset_seconds,
        now=snapshot.observed_at_utc,
    )
    context: dict[str, object] = {
        "current": {
            "location": snapshot.location.label,
            "observed_at_local": local_observed.isoformat(),
            "condition": snapshot.condition,
            "description": snapshot.description,
            "temperature_c": snapshot.temperature_c,
            "feels_like_c": snapshot.feels_like_c,
            "humidity_percent": snapshot.humidity_percent,
            "pressure_hpa": snapshot.pressure_hpa,
            "wind_speed_mps": snapshot.wind_speed_mps,
            "cloud_percent": snapshot.cloud_percent,
        }
    }
    if historical is not None:
        context["historical_boulder"] = {
            "date": historical.day.isoformat(),
            "temperature_c": historical.temperature_c,
            "min_temperature_c": historical.min_temperature_c,
            "max_temperature_c": historical.max_temperature_c,
            "humidity_percent": historical.humidity_percent,
            "conditions": historical.conditions,
            "description": historical.description,
        }
    return context


def answer_weather_question(
    client: Any,
    *,
    question: str,
    snapshot: WeatherSnapshot,
    model: str,
    historical: HistoricalWeatherDay | None = None,
) -> str:
    context = weather_context(snapshot, historical)
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=(
            f"User question:\n{question}\n\n"
            f"Verified weather context:\n{json.dumps(context, ensure_ascii=False)}"
        ),
    )
    return response.output_text.strip()
