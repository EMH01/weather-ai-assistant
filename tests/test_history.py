from datetime import date

import pytest

from weather_assistant.history import BoulderHistoryRepository, fahrenheit_to_celsius


def test_fahrenheit_conversion():
    assert fahrenheit_to_celsius(32.0) == pytest.approx(0.0)
    assert fahrenheit_to_celsius(50.0) == pytest.approx(10.0)


def test_historical_boulder_row_is_loaded_and_normalized(tmp_path):
    path = tmp_path / "weather.csv"
    path.write_text(
        "name,datetime,tempmax,tempmin,temp,humidity,conditions,description\n"
        "Boulder,2023-01-02,50,32,41,80,Snow,Cloudy with snow.\n",
        encoding="utf-8",
    )

    result = BoulderHistoryRepository(path).get(date(2023, 1, 2))

    assert result is not None
    assert result.location == "Boulder"
    assert result.temperature_c == pytest.approx(5.0)
    assert result.min_temperature_c == pytest.approx(0.0)
    assert result.max_temperature_c == pytest.approx(10.0)
    assert result.conditions == "Snow"


def test_missing_historical_day_returns_none(tmp_path):
    path = tmp_path / "weather.csv"
    path.write_text(
        "name,datetime,tempmax,tempmin,temp,humidity,conditions,description\n"
        "Boulder,2023-01-02,50,32,41,80,Snow,Cloudy with snow.\n",
        encoding="utf-8",
    )
    assert BoulderHistoryRepository(path).get(date(2023, 1, 3)) is None
