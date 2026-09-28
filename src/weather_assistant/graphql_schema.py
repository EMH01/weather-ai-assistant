from datetime import date

import strawberry

from .config import Settings
from .history import BoulderHistoryRepository
from .time_utils import current_time_in_zone, local_time_from_offset
from .weather import OpenWeatherClient


@strawberry.type
class Weather:
    location: str
    observed_at_utc: str
    local_time: str
    condition: str
    description: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_mps: float
    cloud_percent: float


@strawberry.type
class HistoricalWeather:
    location: str
    date: str
    temperature_c: float
    min_temperature_c: float
    max_temperature_c: float
    humidity_percent: float
    conditions: str
    description: str


def create_schema(settings: Settings | None = None) -> strawberry.Schema:
    config = settings or Settings()

    @strawberry.type
    class Query:
        @strawberry.field
        def weather(self, city: str, language: str = "en") -> Weather:
            if not config.openweather_api_key:
                raise ValueError("OPENWEATHER_API_KEY is not configured.")

            with OpenWeatherClient(
                config.openweather_api_key,
                timeout_seconds=config.http_timeout_seconds,
            ) as client:
                snapshot = client.current(city, language=language)

            local_observed = local_time_from_offset(
                snapshot.timezone_offset_seconds,
                now=snapshot.observed_at_utc,
            )
            return Weather(
                location=snapshot.location.label,
                observed_at_utc=snapshot.observed_at_utc.isoformat(),
                local_time=local_observed.isoformat(),
                condition=snapshot.condition,
                description=snapshot.description,
                temperature_c=snapshot.temperature_c,
                feels_like_c=snapshot.feels_like_c,
                humidity_percent=snapshot.humidity_percent,
                pressure_hpa=snapshot.pressure_hpa,
                wind_speed_mps=snapshot.wind_speed_mps,
                cloud_percent=snapshot.cloud_percent,
            )

        @strawberry.field
        def local_time(self, timezone_name: str) -> str:
            return current_time_in_zone(timezone_name).isoformat()

        @strawberry.field
        def historical_boulder(self, day: str) -> HistoricalWeather | None:
            if config.boulder_history_csv is None:
                return None
            parsed_day = date.fromisoformat(day)
            result = BoulderHistoryRepository(config.boulder_history_csv).get(parsed_day)
            if result is None:
                return None
            return HistoricalWeather(
                location=result.location,
                date=result.day.isoformat(),
                temperature_c=result.temperature_c,
                min_temperature_c=result.min_temperature_c,
                max_temperature_c=result.max_temperature_c,
                humidity_percent=result.humidity_percent,
                conditions=result.conditions,
                description=result.description,
            )

    return strawberry.Schema(query=Query)
