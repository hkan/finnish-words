#!/usr/bin/env python3
"""Integration tests for segment translations in the full pipeline."""

import json
from pathlib import Path
from chain import build_segments


# Load translation data once for all tests
DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "fi_en.json") as f:
    TRANSLATIONS = json.load(f)

with open(DATA_DIR / "fi_en_past.json") as f:
    PAST_TRANSLATIONS = json.load(f)


def test_kirjoitin_past_sg1():
    """kirjoitin (I wrote) - regular verb, past tense, 1st person singular."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitin',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    assert len(segments) == 3
    
    assert segments[0]['role'] == 'stem'
    assert segments[0]['translation'] == 'write'
    
    assert segments[1]['role'] == 'tense'
    assert segments[1]['translation'] == 'wrote'
    
    assert segments[2]['role'] == 'person'
    assert segments[2]['translation'] == 'I wrote'


def test_synnyin_past_sg1():
    """synnyin (I was born) - 'be' verb conjugation, past tense, 1st person singular."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='synnyin',
        root='synty',
        upos='VERB',
        features=features,
        lemma='syntyä',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    assert len(segments) == 3
    
    assert segments[0]['role'] == 'stem'
    assert segments[0]['translation'] == 'be born'
    
    assert segments[1]['role'] == 'tense'
    assert segments[1]['translation'] == 'was born'
    
    assert segments[2]['role'] == 'person'
    assert segments[2]['translation'] == 'I was born'


def test_kirjoitinko_question():
    """kirjoitinko (did I write?) - regular verb with question clitic."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitinko',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    assert len(segments) == 4
    
    assert segments[0]['translation'] == 'write'
    assert segments[1]['translation'] == 'wrote'
    assert segments[2]['translation'] == 'I wrote'
    
    assert segments[3]['role'] == 'clitic'
    assert segments[3]['translation'] == 'did I write?'


def test_synnyinko_question():
    """synnyinkö (was I born?) - 'be' verb with question clitic (inverted form)."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='synnyinkö',
        root='synty',
        upos='VERB',
        features=features,
        lemma='syntyä',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    assert len(segments) == 4
    
    assert segments[0]['translation'] == 'be born'
    assert segments[1]['translation'] == 'was born'
    assert segments[2]['translation'] == 'I was born'
    
    assert segments[3]['role'] == 'clitic'
    assert segments[3]['translation'] == 'was I born?'


def test_olimme_were_plural():
    """olimme (we were) - 'be' verb uses 'were' for plural."""
    features = {'TENSE': 'PAST', 'PERS': 'PL1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='olimme',
        root='ol',
        upos='VERB',
        features=features,
        lemma='olla',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    assert len(segments) == 3
    
    assert segments[0]['translation'] == 'be'
    assert segments[1]['translation'] == 'was'
    assert segments[2]['translation'] == 'we were'


def test_olit_were_sg2():
    """olit (you were) - 'be' verb uses 'were' for SG2."""
    features = {'TENSE': 'PAST', 'PERS': 'SG2', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='olit',
        root='ol',
        upos='VERB',
        features=features,
        lemma='olla',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    # Find the person segment
    person_seg = next(s for s in segments if s['role'] == 'person')
    assert person_seg['translation'] == 'you were'


def test_oli_was_sg3():
    """oli (he/she was) - 'be' verb uses 'was' for SG3."""
    features = {'TENSE': 'PAST', 'PERS': 'SG3', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='oli',
        root='ol',
        upos='VERB',
        features=features,
        lemma='olla',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    # Find the person segment
    person_seg = next(s for s in segments if s['role'] == 'person')
    assert person_seg['translation'] == 'he/she was'


def test_clean_stem_removes_qualifiers():
    """Stem should have qualifiers removed (e.g., 'olla' → 'be', not 'be (indicating...)')."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='olin',
        root='ol',
        upos='VERB',
        features=features,
        lemma='olla',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    stem_seg = next(s for s in segments if s['role'] == 'stem')
    assert stem_seg['translation'] == 'be'
    # Should not contain qualifiers like "(indicating that the subject...)"
    assert '(' not in stem_seg['translation']
    assert '[' not in stem_seg['translation']
