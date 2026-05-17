#!/usr/bin/env python3
"""Tests for backend/translate.py segment translation composer."""

import pytest


def test_import():
    """Basic import test."""
    from backend.translate import segment_translations


class TestSegmentTranslations:
    """Test segment_translations function."""
    
    def test_kirjoittaa_past_sg1(self):
        """kirjoittaa PAST SG1 → 'I wrote'"""
        from backend.translate import segment_translations
        
        translations = {"kirjoittaa": "to write"}
        past_translations = {"kirjoittaa": "wrote"}
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        result = segment_translations("kirjoittaa", features, translations, past_translations)
        
        assert result["stem"] == "write"
        assert result["tense"] == "wrote"
        assert result["person"] == "I wrote"
    
    def test_syntya_past_sg1(self):
        """syntyä PAST SG1 → 'I was born'"""
        from backend.translate import segment_translations
        
        translations = {"syntyä": "to be born"}
        past_translations = {"syntyä": "was born"}
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        result = segment_translations("syntyä", features, translations, past_translations)
        
        assert result["stem"] == "be born"
        assert result["tense"] == "was born"
        assert result["person"] == "I was born"
    
    def test_syntya_past_pl1(self):
        """syntyä PAST PL1 → 'we were born'"""
        from backend.translate import segment_translations
        
        translations = {"syntyä": "to be born"}
        past_translations = {"syntyä": "was born"}
        features = {"TENSE": "PAST", "PERSON": "PL1"}
        
        result = segment_translations("syntyä", features, translations, past_translations)
        
        assert result["stem"] == "be born"
        assert result["tense"] == "was born"
        assert result["person"] == "we were born"
    
    def test_menna_past_sg2(self):
        """mennä PAST SG2 → 'you went'"""
        from backend.translate import segment_translations
        
        translations = {"mennä": "to go"}
        past_translations = {"mennä": "went"}
        features = {"TENSE": "PAST", "PERSON": "SG2"}
        
        result = segment_translations("mennä", features, translations, past_translations)
        
        assert result["stem"] == "go"
        assert result["tense"] == "went"
        assert result["person"] == "you went"
    
    def test_olla_past_sg3(self):
        """olla PAST SG3 → 'he/she was'"""
        from backend.translate import segment_translations
        
        translations = {"olla": "to be"}
        past_translations = {"olla": "was"}
        features = {"TENSE": "PAST", "PERSON": "SG3"}
        
        result = segment_translations("olla", features, translations, past_translations)
        
        assert result["stem"] == "be"
        assert result["tense"] == "was"
        assert result["person"] == "he/she was"
    
    def test_kirjoittaa_past_sg1_question(self):
        """kirjoittaa PAST SG1 + question → 'did I write?'"""
        from backend.translate import segment_translations
        
        translations = {"kirjoittaa": "to write"}
        past_translations = {"kirjoittaa": "wrote"}
        features = {"TENSE": "PAST", "PERSON": "SG1", "CLITIC": "KO"}
        
        result = segment_translations("kirjoittaa", features, translations, past_translations)
        
        assert result["stem"] == "write"
        assert result["tense"] == "wrote"
        assert result["person"] == "I wrote"
        assert result["question"] == "did I write?"
    
    def test_syntya_past_sg1_question(self):
        """syntyä PAST SG1 + question → 'was I born?'"""
        from backend.translate import segment_translations
        
        translations = {"syntyä": "to be born"}
        past_translations = {"syntyä": "was born"}
        features = {"TENSE": "PAST", "PERSON": "SG1", "CLITIC": "KO"}
        
        result = segment_translations("syntyä", features, translations, past_translations)
        
        assert result["stem"] == "be born"
        assert result["tense"] == "was born"
        assert result["person"] == "I was born"
        assert result["question"] == "was I born?"
    
    def test_olla_past_pl2(self):
        """olla PAST PL2 → 'you were' (plural)"""
        from backend.translate import segment_translations
        
        translations = {"olla": "to be"}
        past_translations = {"olla": "was"}
        features = {"TENSE": "PAST", "PERSON": "PL2"}
        
        result = segment_translations("olla", features, translations, past_translations)
        
        assert result["stem"] == "be"
        assert result["tense"] == "was"
        assert result["person"] == "you were"
    
    def test_olla_past_pl3(self):
        """olla PAST PL3 → 'they were'"""
        from backend.translate import segment_translations
        
        translations = {"olla": "to be"}
        past_translations = {"olla": "was"}
        features = {"TENSE": "PAST", "PERSON": "PL3"}
        
        result = segment_translations("olla", features, translations, past_translations)
        
        assert result["stem"] == "be"
        assert result["tense"] == "was"
        assert result["person"] == "they were"
    
    def test_unknown_lemma_no_crash(self):
        """Unknown lemma returns None for all fields, no crash."""
        from backend.translate import segment_translations
        
        translations = {"kirjoittaa": "to write"}
        past_translations = {"kirjoittaa": "wrote"}
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        result = segment_translations("unknownverb", features, translations, past_translations)
        
        # Should return dict with None values
        assert result["stem"] is None
        assert result["tense"] is None
        assert result["person"] is None
    
    def test_missing_past_translation(self):
        """Lemma with no past translation returns None for tense/person."""
        from backend.translate import segment_translations
        
        translations = {"mennä": "to go"}
        past_translations = {}  # empty
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        result = segment_translations("mennä", features, translations, past_translations)
        
        assert result["stem"] == "go"
        assert result["tense"] is None
        assert result["person"] is None


class TestAnnotateSegments:
    """Test annotate_segments function."""
    
    def test_annotate_segments_basic(self):
        """Test basic segment annotation."""
        from backend.translate import annotate_segments
        
        segments = [
            {"role": "stem", "surface": "kirjoit"},
            {"role": "tense", "surface": "i"},
            {"role": "person", "surface": "n"}
        ]
        
        translations = {"kirjoittaa": "to write"}
        past_translations = {"kirjoittaa": "wrote"}
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        annotate_segments(segments, "kirjoittaa", features, translations, past_translations)
        
        assert segments[0]["translation"] == "write"
        assert segments[1]["translation"] == "wrote"
        assert segments[2]["translation"] == "I wrote"
    
    def test_annotate_segments_with_question(self):
        """Test segment annotation with question clitic."""
        from backend.translate import annotate_segments
        
        segments = [
            {"role": "stem", "surface": "kirjoit"},
            {"role": "tense", "surface": "i"},
            {"role": "person", "surface": "n"},
            {"role": "clitic", "surface": "ko"}
        ]
        
        translations = {"kirjoittaa": "to write"}
        past_translations = {"kirjoittaa": "wrote"}
        features = {"TENSE": "PAST", "PERSON": "SG1", "CLITIC": "KO"}
        
        annotate_segments(segments, "kirjoittaa", features, translations, past_translations)
        
        assert segments[0]["translation"] == "write"
        assert segments[1]["translation"] == "wrote"
        assert segments[2]["translation"] == "I wrote"
        assert segments[3]["translation"] == "did I write?"
    
    def test_annotate_segments_missing_data(self):
        """Test that missing translations don't crash, just skip."""
        from backend.translate import annotate_segments
        
        segments = [
            {"role": "stem", "surface": "xxx"},
            {"role": "tense", "surface": "i"}
        ]
        
        translations = {}
        past_translations = {}
        features = {"TENSE": "PAST", "PERSON": "SG1"}
        
        # Should not crash
        annotate_segments(segments, "unknown", features, translations, past_translations)
        
        # Translations should be None (or not set)
        assert segments[0].get("translation") is None
        assert segments[1].get("translation") is None
