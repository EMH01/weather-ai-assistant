import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    openweather_api_key: str | None = os.getenv("OPENWEATHER_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    boulder_history_csv: Path | None = (
        Path(value) if (value := os.getenv("BOULDER_HISTORY_CSV")) else None
    )
    http_timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
