FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvoikko1 voikko-fi \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn httpx pytest libvoikko

WORKDIR /app
COPY backend/ ./backend/
WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
