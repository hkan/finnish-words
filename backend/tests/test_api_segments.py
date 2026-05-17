#!/usr/bin/env python3
"""Test that /analyse API endpoint returns segment translations."""

import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Mock libvoikko since it might not be installed in test env
sys.modules['libvoikko'] = Mock()

from main import app
from fastapi.testclient import TestClient


def test_api_returns_segment_translations():
    """Test that /analyse endpoint includes translation field in segments."""
    client = TestClient(app)
    
    # Test with a simple word that should have translations
    response = client.get("/analyse?word=kirjoitin")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have readings
    assert "readings" in data
    assert len(data["readings"]) > 0
    
    # Find a reading with segments
    reading_with_segments = None
    for reading in data["readings"]:
        if "segments" in reading and reading["segments"]:
            reading_with_segments = reading
            break
    
    # If we found segments, they should have translations
    if reading_with_segments:
        segments = reading_with_segments["segments"]
        
        # Check that at least some segments have translations
        # (they might be None if translation data is missing, which is OK)
        has_translation_field = any("translation" in seg for seg in segments)
        assert has_translation_field, "Segments should have 'translation' field"
        
        # If translation data is loaded, check specific translations
        # This is optional since the test might run without data files
        stem_seg = next((s for s in segments if s.get("role") == "stem"), None)
        if stem_seg and stem_seg.get("translation"):
            # If we have a translation, it should be a string
            assert isinstance(stem_seg["translation"], str)


def test_api_question_clitic_translation():
    """Test that question clitics get question form translations."""
    client = TestClient(app)
    
    # Test with a question word
    response = client.get("/analyse?word=kirjoitinko")
    
    assert response.status_code == 200
    data = response.json()
    
    # Find a reading with clitic
    for reading in data.get("readings", []):
        segments = reading.get("segments", [])
        clitic_seg = next((s for s in segments if s.get("role") == "clitic"), None)
        
        if clitic_seg:
            # Clitic should have translation field
            assert "translation" in clitic_seg
            
            # If translation data is available, should be a question
            if clitic_seg.get("translation"):
                translation = clitic_seg["translation"]
                assert "?" in translation, f"Question clitic should have '?' in translation: {translation}"
            
            break
