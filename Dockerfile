FROM omorfi

RUN apt-get update && apt-get install -y --no-install-recommends \
    libvoikko1 voikko-fi python3-libvoikko \
  && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn voikko httpx pytest --break-system-packages

COPY backend/ ./backend/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
