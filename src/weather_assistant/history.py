import csv
from datetime import date
from pathlib import Path

from .models import HistoricalWeatherDay


def fahrenheit_to_celsius(value: float) -> float:
    return (value - 32.0) * 5.0 / 9.0


class BoulderHistoryRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get(self, day: date) -> HistoricalWeatherDay | None:
        with self.path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if date.fromisoformat(row["datetime"]) != day:
                    continue
                return HistoricalWeatherDay(
                    location=row["name"],
                    day=day,
                    temperature_c=fahrenheit_to_celsius(float(row["temp"])),
                    min_temperature_c=fahrenheit_to_celsius(float(row["tempmin"])),
                    max_temperature_c=fahrenheit_to_celsius(float(row["tempmax"])),
                    humidity_percent=float(row["humidity"]),
                    conditions=row["conditions"],
                    description=row["description"],
                )
        return None
