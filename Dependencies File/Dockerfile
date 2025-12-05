# Simple container for the orchestrator
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY orchestrator ./orchestrator
COPY config ./config

ENV PROVIDERS_CONFIG=/app/config/providers.yaml
EXPOSE 8000

CMD ["uvicorn", "orchestrator.app:app", "--host", "0.0.0.0", "--port", "8000"]
