from datetime import UTC, datetime

import httpx

from .models import Location, WeatherSnapshot

GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class OpenWeatherClient:
    def __init__(
        self,
        api_key: str,
        *,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OpenWeather API key is required.")
        self.api_key = api_key
        self._owns_client = client is None
        self.client = client or httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def geocode(self, query: str) -> Location:
        response = self.client.get(
            GEOCODING_URL,
            params={
                "q": query,
                "limit": 1,
                "appid": self.api_key,
            },
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(f"Location not found: {query}")

        item = results[0]
        return Location(
            name=item["name"],
            state=item.get("state"),
            country=item["country"],
            latitude=float(item["lat"]),
            longitude=float(item["lon"]),
        )

    def current(self, query: str, *, language: str = "en") -> WeatherSnapshot:
        location = self.geocode(query)
        response = self.client.get(
            CURRENT_WEATHER_URL,
            params={
                "lat": location.latitude,
                "lon": location.longitude,
                "appid": self.api_key,
                "units": "metric",
                "lang": language,
            },
        )
        response.raise_for_status()
        data = response.json()

        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})

        return WeatherSnapshot(
            location=location,
            observed_at_utc=datetime.fromtimestamp(data["dt"], tz=UTC),
            timezone_offset_seconds=int(data.get("timezone", 0)),
            condition=weather["main"],
            description=weather["description"],
            temperature_c=float(main["temp"]),
            feels_like_c=float(main["feels_like"]),
            humidity_percent=float(main["humidity"]),
            pressure_hpa=float(main["pressure"]),
            wind_speed_mps=float(wind.get("speed", 0.0)),
            cloud_percent=float(clouds.get("all", 0.0)),
        )
