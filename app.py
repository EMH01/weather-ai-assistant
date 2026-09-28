import os
from datetime import date

import gradio as gr
from openai import OpenAI

from weather_assistant.assistant import answer_weather_question
from weather_assistant.config import Settings
from weather_assistant.history import BoulderHistoryRepository
from weather_assistant.weather import OpenWeatherClient

settings = Settings()


def ask_weather(city: str, question: str, historical_date: str):
    if not city.strip():
        raise gr.Error("Enter a location.")
    if not question.strip():
        raise gr.Error("Enter a weather-related question.")
    if not settings.openweather_api_key:
        raise gr.Error("Set OPENWEATHER_API_KEY before running the assistant.")
    if not os.getenv("OPENAI_API_KEY"):
        raise gr.Error("Set OPENAI_API_KEY before running the assistant.")

    with OpenWeatherClient(
        settings.openweather_api_key,
        timeout_seconds=settings.http_timeout_seconds,
    ) as weather_client:
        snapshot = weather_client.current(city.strip())

    historical = None
    if historical_date.strip():
        if settings.boulder_history_csv is None:
            raise gr.Error(
                "Historical Boulder data is not configured. Set BOULDER_HISTORY_CSV."
            )
        try:
            day = date.fromisoformat(historical_date.strip())
        except ValueError as exc:
            raise gr.Error("Historical date must use YYYY-MM-DD.") from exc
        historical = BoulderHistoryRepository(settings.boulder_history_csv).get(day)
        if historical is None:
            raise gr.Error(f"No Boulder historical row found for {day.isoformat()}.")

    answer = answer_weather_question(
        OpenAI(),
        question=question.strip(),
        snapshot=snapshot,
        model=settings.openai_model,
        historical=historical,
    )
    current = (
        f"**{snapshot.location.label}** · {snapshot.description}\n\n"
        f"- Temperature: {snapshot.temperature_c:.1f} °C\n"
        f"- Feels like: {snapshot.feels_like_c:.1f} °C\n"
        f"- Humidity: {snapshot.humidity_percent:.0f}%\n"
        f"- Wind: {snapshot.wind_speed_mps:.1f} m/s\n"
        f"- Clouds: {snapshot.cloud_percent:.0f}%"
    )
    return answer, current


with gr.Blocks(title="Weather AI Assistant") as demo:
    gr.Markdown(
        "# 🌤️ Weather AI Assistant\n"
        "Grounded conversational answers backed by live weather data."
    )
    with gr.Row():
        city = gr.Textbox(label="Location", placeholder="Granada, ES")
        historical_date = gr.Textbox(
            label="Optional Boulder historical date",
            placeholder="2023-01-02",
        )
    question = gr.Textbox(
        label="Question",
        placeholder="Do I need a jacket if I go out this evening?",
        lines=2,
    )
    ask = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Markdown(label="Assistant")
        current = gr.Markdown(label="Verified current data")

    ask.click(
        ask_weather,
        inputs=[city, question, historical_date],
        outputs=[answer, current],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
