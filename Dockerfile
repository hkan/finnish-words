FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvoikko1 voikko-fi python3-libvoikko \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn httpx pytest

# python3-libvoikko installs into the debian-system python's dist-packages.
ENV PYTHONPATH=/usr/lib/python3/dist-packages

WORKDIR /app
COPY backend/ ./backend/
WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
