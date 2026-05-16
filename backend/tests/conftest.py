"""
Shared fixtures for the API test suite.

We construct a single TestClient at module scope. FastAPI's lifespan handler
(which loads Omorfi) runs once when the client enters its context manager,
so all tests reuse one loaded analyser.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make backend modules importable as `main`, `chain`, `stem` (matching the
# layout uvicorn expects).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
