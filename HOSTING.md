# Hosting & Infrastructure

## Stack

- **Backend**: FastAPI (Python) — wraps Omorfi, exposes `GET /analyse?word=` endpoint
- **Frontend**: React + Vite — no router (single-screen tool)
- Local dev: Docker Compose runs both; Vite proxies `/analyse` to the API container on port 8000

## Docker Setup

Omorfi is not installed locally — it only works inside Docker. Our app extends the `omorfi` image:

```dockerfile
FROM omorfi
RUN pip install fastapi uvicorn --break-system-packages
COPY backend/ ./backend/
WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The omorfi image already includes `python3-hfst` and `pip install omorfi`, so Python bindings are available inside the container without any extra setup.

Docker Compose runs two services:
- `api` — our image (omorfi + FastAPI), port 8000
- `web` — Vite dev server via `node:22-alpine`, port 5173

## Development Workflow

`./backend` is mounted as a volume into the api container, and uvicorn runs with `--reload`. This means any save to `backend/main.py` hot-reloads the server — no rebuild needed during development. The frontend already has Vite HMR.

First-time setup requires `docker compose up --build` to build the image. After that, `docker compose up` is enough.

## Omorfi Python API

The `Omorfi` class is instantiated once at FastAPI startup. The correct API (confirmed by inspecting the installed package inside the container):

```python
from omorfi import Omorfi, Token

omorfi = Omorfi()
omorfi.load_analyser("/app/src/generated/omorfi.analyse.hfst")
omorfi.load_labelsegmenter("/app/src/generated/omorfi.labelsegment.hfst")

token = Token("tiesitkö")
omorfi.analyse(token)
# results in: token.analyses  (list of Analysis objects)
# each analysis: analysis.raw, analysis.get_lemmas()

token2 = Token("tiesitkö")
omorfi.labelsegment(token2)
# results in: token2.labelsegmentations  (list of objects)
# each: .raw  →  "ti{STUB}[VERB]es{MB}i{MB}t[ACTV][PAST][SG2]{MB}kö[KO]"
```

Note: there is no `load_from_dir()` or `find_omorfi()` — those don't exist in this version. Load each transducer file explicitly.

## Deployment Target

**Koyeb** — persistent container host with native scale-to-zero. Serverless is ruled out: Omorfi/HFST tools have real memory footprint and need to stay warm between requests, not reload per invocation.

- Free tier: 512MB RAM, no credit card required, never expires. Upgrade to ~€5/mo (1GB) only if Omorfi exceeds 512MB.
- Budget ceiling: €20/mo.
- Scale-to-zero: container sleeps when idle, wakes on request. Cold start (~10–30s) is acceptable — see UX below.
- Standard OCI image, no proprietary config — low vendor lock-in.

For production, the **single combined image** (omorfi + FastAPI + Vite static build) is shipped to Koyeb. No separate frontend service.

**Domain & CDN**: Cloudflare — handles the custom domain, CDN, and first-line rate limiting/abuse protection.

## Cold Start UX

The frontend polls `/health` on page load. While the backend is unresponsive, a "warming up…" state is shown — non-blocking, folded into the normal request spinner/loading indicator. The user can type immediately; their first submission waits if the backend isn't ready yet. No separate blocking splash screen.

## Abuse Prevention

- **Rate limiting**: Cloudflare as first line of defense (absorbs volumetric abuse before it reaches the container); `slowapi` as app-level backstop. Limit: **20 requests per minute per IP**.
- **Input validation** before anything reaches Omorfi: max 50 characters, Finnish character set only (`[a-zA-ZäöåÄÖÅ-]`).
- **Caching** Omorfi results — in-memory dict to start, upgradeable to Redis. Common words will dominate traffic; this also reduces rate limiting pressure.
- **Spend alerts** set at the Koyeb hosting level.
