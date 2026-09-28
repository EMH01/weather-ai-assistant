from datetime import UTC, datetime
from types import SimpleNamespace

from weather_assistant.assistant import answer_weather_question, weather_context
from weather_assistant.models import Location, WeatherSnapshot


def snapshot():
    return WeatherSnapshot(
        location=Location(
            name="Granada",
            state="Andalusia",
            country="ES",
            latitude=37.18,
            longitude=-3.60,
        ),
        observed_at_utc=datetime(2026, 9, 28, 10, 0, tzinfo=UTC),
        timezone_offset_seconds=7200,
        condition="Clear",
        description="clear sky",
        temperature_c=24.0,
        feels_like_c=23.5,
        humidity_percent=35.0,
        pressure_hpa=1018.0,
        wind_speed_mps=2.0,
        cloud_percent=3.0,
    )


def test_weather_context_contains_verified_measurements():
    context = weather_context(snapshot())

    assert context["current"]["location"] == "Granada, Andalusia, ES"
    assert context["current"]["temperature_c"] == 24.0
    assert context["current"]["observed_at_local"].startswith("2026-09-28T12:00:00")


def test_answer_passes_grounded_context_to_model():
    captured = {}

    class Responses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text="Hace buen tiempo.")

    client = SimpleNamespace(responses=Responses())
    answer = answer_weather_question(
        client,
        question="¿Hace buen tiempo?",
        snapshot=snapshot(),
        model="test-model",
    )

    assert answer == "Hace buen tiempo."
    assert captured["model"] == "test-model"
    assert '"temperature_c": 24.0' in captured["input"]
    assert "Do not invent" in captured["instructions"]
