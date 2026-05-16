# Hosting & Infrastructure

## Stack

- **Backend**: FastAPI (Python) — wraps Voikko, exposes `GET /analyse?word=` endpoint
- **Frontend**: React + Vite — no router (single-screen tool)
- Local dev: Docker Compose runs both; Vite proxies `/analyse` to the API container on port 8000

## Docker Setup

The backend runs on `python:3.12-slim` with Voikko installed via apt:

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libvoikko1 voikko-fi python3-libvoikko \
  && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn
ENV PYTHONPATH=/usr/lib/python3/dist-packages
```

`python3-libvoikko` installs into Debian's system Python dist-packages, so the slim image's interpreter needs `PYTHONPATH` to find it.

Docker Compose runs two services:
- `api` — backend image (Voikko + FastAPI), port 8000
- `web` — Vite dev server via `node:22-alpine`, port 5173

## Development Workflow

`./backend` is mounted as a volume into the api container, and uvicorn runs with `--reload`. Any save to `backend/main.py` hot-reloads the server — no rebuild needed during development. Vite handles frontend HMR.

First-time setup: `docker compose up --build`. After that, `docker compose up`.

## Deployment Target

**Koyeb** — persistent container host with native scale-to-zero. Serverless is ruled out: the Voikko analyser needs to stay warm between requests, not reload per invocation.

- Free tier: 512MB RAM, no credit card required, never expires.
- Budget ceiling: €20/mo.
- Scale-to-zero: container sleeps when idle, wakes on request. Cold start (~10–30s) is acceptable — see UX below.
- Standard OCI image, no proprietary config — low vendor lock-in.

Production ships a **single combined image** (Voikko + FastAPI + Vite static build, built from `Dockerfile.prod`). No separate frontend service.

**Domain & CDN**: Cloudflare — custom domain, CDN, and first-line rate limiting/abuse protection.

## Cold Start UX

The frontend polls `/health` on page load. While the backend is unresponsive, a "warming up…" state is shown — non-blocking, folded into the normal request spinner. The user can type immediately; their first submission waits if the backend isn't ready yet. No separate blocking splash screen.

## Abuse Prevention

- **Rate limiting**: Cloudflare as first line of defense; `slowapi` as app-level backstop. Limit: **20 requests per minute per IP**.
- **Input validation** before anything reaches Voikko: max 50 characters, Finnish character set only (`[a-zA-ZäöåÄÖÅ-]`).
- **Caching** analysis results — in-memory dict to start, upgradeable to Redis. Common words dominate traffic; this also reduces rate-limit pressure.
- **Spend alerts** set at the Koyeb hosting level.
