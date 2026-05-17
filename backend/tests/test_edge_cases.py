#!/usr/bin/env python3
"""Edge case tests for segment translations."""

import json
from pathlib import Path
from chain import build_segments


DATA_DIR = Path(__file__).parent.parent / "data"
with open(DATA_DIR / "fi_en.json") as f:
    TRANSLATIONS = json.load(f)

with open(DATA_DIR / "fi_en_past.json") as f:
    PAST_TRANSLATIONS = json.load(f)


def test_present_tense_deferred():
    """Present tense returns segments but tense/person translations should be None (deferred)."""
    features = {'TENSE': 'PRESENT', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitan',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    # Stem should work (uses basic gloss)
    stem = next(s for s in segments if s['role'] == 'stem')
    assert stem['translation'] == 'write'
    
    # Tense and person should be None (present tense not implemented)
    person = next(s for s in segments if s['role'] == 'person')
    assert person['translation'] is None


def test_non_ko_clitic_shows_hint():
    """Non-KO clitics (like -han, -pa) should show descriptive hint, not question."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitinhan',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    clitic = next((s for s in segments if s['role'] == 'clitic'), None)
    assert clitic is not None
    assert clitic['surface'] == 'han'
    
    # Should have descriptive hint, not question form
    assert clitic['translation'] == '(emphasis)'
    assert 'translation_note' in clitic
    assert 'emphatic' in clitic['translation_note']
    
    # Should have documentation link for -han
    assert 'translation_link' in clitic
    assert 'uusikielemme.fi' in clitic['translation_link']


def test_stacked_clitics_han_ko():
    """With stacked clitics like -han-kö, -han gets hint, -kö gets question."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitinhankö',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    clitics = [s for s in segments if s['role'] == 'clitic']
    assert len(clitics) == 2
    
    # First clitic (-han) should have descriptive hint
    assert clitics[0]['surface'] in ['han', 'hän']
    assert clitics[0]['translation'] == '(emphasis)'
    assert 'translation_note' in clitics[0]
    
    # Second clitic (-kö) should have question translation
    assert clitics[1]['surface'] in ['ko', 'kö']
    assert clitics[1]['translation'] == 'did I write?'


def test_missing_translation_data_no_crash():
    """Unknown verb should return None translations without crashing."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='xyzin',
        root='xyz',
        upos='VERB',
        features=features,
        lemma='xyzää',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    # All translations should be None
    for seg in segments:
        assert seg['translation'] is None


def test_passive_voice_not_supported():
    """Passive voice should return None segments (not implemented)."""
    features = {'TENSE': 'PAST', 'PERS': 'SG3', 'MOOD': 'INDV', 'VOICE': 'PASS'}
    segments = build_segments(
        surface='kirjoitettiin',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    # Passive not supported in build_segments
    assert segments is None


def test_conditional_mood_not_supported():
    """Conditional mood should return None segments (not implemented)."""
    features = {'TENSE': 'PRESENT', 'PERS': 'SG1', 'MOOD': 'COND', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoittaisin',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    # Conditional not supported in build_segments
    assert segments is None


def test_kin_clitic_shows_also():
    """The -kin clitic should show '(also/even)' hint."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitinkin',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    clitic = next((s for s in segments if s['role'] == 'clitic'), None)
    assert clitic is not None
    assert clitic['surface'] == 'kin'
    assert clitic['translation'] == '(also/even)'
    assert 'also' in clitic['translation_note']


def test_pa_clitic_shows_contrast():
    """The -pa clitic should show '(contrast)' hint."""
    features = {'TENSE': 'PAST', 'PERS': 'SG1', 'MOOD': 'INDV', 'VOICE': 'ACT'}
    segments = build_segments(
        surface='kirjoitinpa',
        root='kirjoitta',
        upos='VERB',
        features=features,
        lemma='kirjoittaa',
        lang='en',
        translations=TRANSLATIONS,
        past_translations=PAST_TRANSLATIONS
    )
    
    assert segments is not None
    
    clitic = next((s for s in segments if s['role'] == 'clitic'), None)
    assert clitic is not None
    assert clitic['surface'] == 'pa'
    assert clitic['translation'] == '(contrast)'
    assert 'contrast' in clitic['translation_note'].lower()
