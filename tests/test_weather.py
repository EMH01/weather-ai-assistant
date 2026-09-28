import httpx
import pytest

from weather_assistant.weather import OpenWeatherClient


def test_current_weather_uses_geocoding_then_coordinates():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/geo/1.0/direct"):
            assert request.url.params["q"] == "Granada, ES"
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "Granada",
                        "state": "Andalusia",
                        "country": "ES",
                        "lat": 37.18,
                        "lon": -3.60,
                    }
                ],
            )

        assert request.url.path.endswith("/data/2.5/weather")
        assert request.url.params["lat"] == "37.18"
        assert request.url.params["lon"] == "-3.6"
        assert request.url.params["units"] == "metric"
        return httpx.Response(
            200,
            json={
                "dt": 1_700_000_000,
                "timezone": 3600,
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "main": {
                    "temp": 18.5,
                    "feels_like": 18.0,
                    "humidity": 45,
                    "pressure": 1016,
                },
                "wind": {"speed": 2.5},
                "clouds": {"all": 4},
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        client = OpenWeatherClient("test-key", client=http_client)
        snapshot = client.current("Granada, ES")

    assert snapshot.location.label == "Granada, Andalusia, ES"
    assert snapshot.temperature_c == pytest.approx(18.5)
    assert snapshot.timezone_offset_seconds == 3600
    assert snapshot.condition == "Clear"


def test_unknown_location_raises_clear_error():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=[]))
    with httpx.Client(transport=transport) as http_client:
        client = OpenWeatherClient("test-key", client=http_client)
        with pytest.raises(ValueError, match="Location not found"):
            client.geocode("Atlantis")
