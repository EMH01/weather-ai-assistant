FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home appuser

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY app.py graphql_app.py ./

USER appuser

CMD ["python", "app.py"]
