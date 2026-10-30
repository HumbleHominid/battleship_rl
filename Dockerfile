FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY game/ ./game/
COPY server.py ./
COPY checkpoints/q_agent.pt ./checkpoints/q_agent.pt

RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
