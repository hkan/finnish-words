"""
Shared fixtures for the API test suite.

We construct a single TestClient at module scope so all tests share one
loaded Voikko analyser.
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
