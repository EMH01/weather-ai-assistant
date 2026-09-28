from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class Location:
    name: str
    country: str
    latitude: float
    longitude: float
    state: str | None = None

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ", ".join(parts)


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    location: Location
    observed_at_utc: datetime
    timezone_offset_seconds: int
    condition: str
    description: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_mps: float
    cloud_percent: float


@dataclass(frozen=True, slots=True)
class HistoricalWeatherDay:
    location: str
    day: date
    temperature_c: float
    min_temperature_c: float
    max_temperature_c: float
    humidity_percent: float
    conditions: str
    description: str
