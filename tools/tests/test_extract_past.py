#!/usr/bin/env python3
"""Tests for extract_past() functionality in build_translations.py"""

import pytest
import sys
from pathlib import Path

# Add scripts dir to path so we can import build_translations
sys.path.insert(0, str(Path(__file__).parent.parent))

from build_translations import extract_past_form, build_past_gloss


class TestExtractPastForm:
    """Test extracting simple past forms from English verb entries."""
    
    def test_regular_verb(self):
        """Regular verb with simple past form."""
        forms = [
            {"form": "writes", "tags": ["present"]},
            {"form": "wrote", "tags": ["past"]},
            {"form": "written", "tags": ["past", "participle"]}
        ]
        assert extract_past_form("write", forms) == "wrote"
    
    def test_be_verb_returns_was(self):
        """The verb 'be' should return 'was' (singular form)."""
        forms = [
            {"form": "was", "tags": ["past"]},
            {"form": "were", "tags": ["past"]}
        ]
        assert extract_past_form("be", forms) == "was"
    
    def test_skips_participle(self):
        """Should skip forms tagged with 'participle'."""
        forms = [
            {"form": "written", "tags": ["past", "participle"]},
            {"form": "wrote", "tags": ["past"]}
        ]
        assert extract_past_form("write", forms) == "wrote"
    
    def test_skips_archaic(self):
        """Should skip forms tagged with 'archaic'."""
        forms = [
            {"form": "wast", "tags": ["past", "archaic"]},
            {"form": "was", "tags": ["past"]}
        ]
        assert extract_past_form("be", forms) == "was"
    
    def test_skips_subjunctive(self):
        """Should skip forms tagged with 'subjunctive'."""
        forms = [
            {"form": "were", "tags": ["past", "subjunctive"]},
            {"form": "was", "tags": ["past"]}
        ]
        assert extract_past_form("be", forms) == "was"
    
    def test_no_past_form(self):
        """Return None if no valid past form found."""
        forms = [
            {"form": "writing", "tags": ["present", "participle"]}
        ]
        assert extract_past_form("write", forms) is None
    
    def test_empty_forms(self):
        """Return None for empty forms list."""
        assert extract_past_form("write", []) is None


class TestBuildPastGloss:
    """Test building past tense glosses from Finnish verb glosses."""
    
    def test_simple_infinitive(self):
        """Convert 'to write' → 'wrote'."""
        past_forms = {"write": "wrote"}
        assert build_past_gloss("to write", past_forms) == "wrote"
    
    def test_multi_word_verb(self):
        """Convert 'to be born' → 'was born'."""
        past_forms = {"be": "was"}
        assert build_past_gloss("to be born", past_forms) == "was born"
    
    def test_strip_qualifier_parens(self):
        """Strip (qualifier) prefix from gloss."""
        past_forms = {"go": "went"}
        assert build_past_gloss("(intransitive) to go", past_forms) == "went"
    
    def test_strip_qualifier_brackets(self):
        """Strip [qualifier] prefix from gloss."""
        past_forms = {"run": "ran"}
        assert build_past_gloss("[archaic] to run", past_forms) == "ran"
    
    def test_multi_word_verb_with_qualifier(self):
        """Handle qualifier + multi-word verb."""
        past_forms = {"be": "was"}
        assert build_past_gloss("(intransitive) to be born", past_forms) == "was born"
    
    def test_no_to_prefix(self):
        """Handle gloss without 'to' prefix."""
        past_forms = {"go": "went"}
        assert build_past_gloss("go", past_forms) == "went"
    
    def test_missing_past_form(self):
        """Return None if first word has no past form."""
        past_forms = {"write": "wrote"}
        assert build_past_gloss("to read", past_forms) is None
    
    def test_empty_gloss(self):
        """Return None for empty gloss."""
        past_forms = {"write": "wrote"}
        assert build_past_gloss("", past_forms) is None
    
    def test_multi_word_first_word_lookup(self):
        """For 'take care', look up 'take' not 'care'."""
        past_forms = {"take": "took"}
        assert build_past_gloss("to take care", past_forms) == "took care"
    
    def test_phrasal_verb(self):
        """Handle phrasal verbs like 'to give up'."""
        past_forms = {"give": "gave"}
        assert build_past_gloss("to give up", past_forms) == "gave up"


class TestExtractPastIntegration:
    """Integration test with mock data."""
    
    def test_full_pipeline(self):
        """Test complete pipeline with mock Finnish and English data."""
        # Mock Finnish lemma → English gloss
        fi_en = {
            "kirjoittaa": "to write",
            "syntyä": "to be born",
            "mennä": "to go"
        }
        
        # Mock English verb → past form lookup
        en_past = {
            "write": "wrote",
            "be": "was",
            "go": "went"
        }
        
        # Build past glosses
        from build_translations import build_past_glosses
        result = build_past_glosses(fi_en, en_past)
        
        assert result == {
            "kirjoittaa": "wrote",
            "syntyä": "was born",
            "mennä": "went"
        }
    
    def test_skip_non_verbs(self):
        """Only process verb lemmas (those with 'to' or that look like verbs)."""
        fi_en = {
            "kirjoittaa": "to write",
            "kissa": "cat",  # noun, no "to"
            "syntyä": "to be born"
        }
        
        en_past = {
            "write": "wrote",
            "be": "was"
        }
        
        from build_translations import build_past_glosses
        result = build_past_glosses(fi_en, en_past)
        
        # Should skip "kissa" since it's not a verb gloss
        assert "kissa" not in result
        assert result == {
            "kirjoittaa": "wrote",
            "syntyä": "was born"
        }
