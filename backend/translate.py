#!/usr/bin/env python3
"""
Progressive English translation composer for Finnish morpheme segments.

Builds cumulative translations as morphemes are added:
- stem: base verb phrase
- tense: past/present phrase
- person: subject + phrase
- question: question form (inverted for "be" verbs, "did" auxiliary for others)
"""

import re
from typing import Optional


# Clitic meanings (for non-KO clitics)
# Tuple: (short_hint, explanation, optional_url)
CLITIC_HINTS = {
    "han": (
        "(emphasis)",
        "emphatic particle: adds confirmation or emphasis",
        "https://uusikielemme.fi/finnish-grammar/syntax/liitepartikkelit/han-han-liitepartikkeli-clitic-minahan-sanoin"
    ),
    "hän": (
        "(emphasis)",
        "emphatic particle: adds confirmation or emphasis",
        "https://uusikielemme.fi/finnish-grammar/syntax/liitepartikkelit/han-han-liitepartikkeli-clitic-minahan-sanoin"
    ),
    "pa": ("(contrast)", "contrastive particle: 'though', 'on the other hand'", None),
    "pä": ("(contrast)", "contrastive particle: 'though', 'on the other hand'", None),
    "ka": ("(also/too)", "emphatic particle: 'also', 'too'", None),
    "kä": ("(also/too)", "emphatic particle: 'also', 'too'", None),
    "kin": ("(also/even)", "'also', 'even', 'too'", None),
    "kaan": ("(either/not even)", "negative polarity: 'either', 'not even'", None),
    "kään": ("(either/not even)", "negative polarity: 'either', 'not even'", None),
    "s": ("(colloquial)", "colloquial particle", None),
}

# Subject pronouns for each person
SUBJECTS = {
    "SG1": "I",
    "SG2": "you",
    "SG3": "he/she",
    "PL1": "we",
    "PL2": "you",
    "PL3": "they"
}


def is_be_verb(past_phrase: Optional[str]) -> bool:
    """Check if a past tense phrase uses 'be' conjugation."""
    if not past_phrase:
        return False
    return past_phrase.startswith("was ") or past_phrase.startswith("were ") or past_phrase == "was" or past_phrase == "were"


def get_stem_phrase(lemma: str, translations: dict[str, str]) -> Optional[str]:
    """Get base verb phrase from lemma, stripping 'to' prefix and qualifiers."""
    gloss = translations.get(lemma)
    if not gloss:
        return None
    
    # Clean qualifiers and extra info (same as build_past_gloss in build_translations.py)
    # Remove all [...] and (...) content
    gloss = re.sub(r'\[[^\]]*\]', '', gloss)
    gloss = re.sub(r'\([^\)]*\)', '', gloss)
    # Take only up to first comma (for multi-part definitions)
    gloss = gloss.split(',')[0].strip()
    
    # Strip "to " prefix
    if gloss.startswith("to "):
        gloss = gloss[3:]
    
    return gloss if gloss else None


def get_tense_phrase(lemma: str, features: dict, past_translations: dict[str, str]) -> Optional[str]:
    """Get tense phrase (past or present)."""
    tense = features.get("TENSE")
    
    if tense == "PAST":
        return past_translations.get(lemma)
    
    # For present tense, would return base phrase
    # Deferred for now - only handling PAST
    return None


def get_person_phrase(lemma: str, features: dict, translations: dict[str, str], past_translations: dict[str, str]) -> Optional[str]:
    """Get phrase with subject pronoun added."""
    person = features.get("PERS")
    if not person:
        return None
    
    subject = SUBJECTS.get(person)
    if not subject:
        return None
    
    tense_phrase = get_tense_phrase(lemma, features, past_translations)
    if not tense_phrase:
        return None
    
    # Check if this is a "be" verb
    if is_be_verb(tense_phrase):
        # Handle was/were conjugation
        if person in ["SG1", "SG3"]:
            # "I was", "he/she was"
            verb_phrase = tense_phrase
        else:
            # "you were", "we were", "you were", "they were"
            # Replace "was" with "were"
            if tense_phrase.startswith("was "):
                verb_phrase = "were " + tense_phrase[4:]
            elif tense_phrase == "was":
                verb_phrase = "were"
            else:
                verb_phrase = tense_phrase
        
        return f"{subject} {verb_phrase}"
    else:
        # Regular verb: just add subject
        return f"{subject} {tense_phrase}"


def get_question_phrase(lemma: str, features: dict, translations: dict[str, str], past_translations: dict[str, str]) -> Optional[str]:
    """Get question form."""
    if features.get("CLITIC") != "KO":
        return None
    
    person = features.get("PERS")
    if not person:
        return None
    
    subject = SUBJECTS.get(person)
    if not subject:
        return None
    
    tense_phrase = get_tense_phrase(lemma, features, past_translations)
    if not tense_phrase:
        return None
    
    stem = get_stem_phrase(lemma, translations)
    if not stem:
        return None
    
    # Check if this is a "be" verb
    if is_be_verb(tense_phrase):
        # Invert: "was I born?"
        if person in ["SG1", "SG3"]:
            aux = "was"
        else:
            aux = "were"
        
        # Extract the rest after "was/were"
        if tense_phrase.startswith("was "):
            rest = tense_phrase[4:]
            return f"{aux} {subject} {rest}?"
        elif tense_phrase.startswith("were "):
            rest = tense_phrase[5:]
            return f"{aux} {subject} {rest}?"
        elif tense_phrase in ["was", "were"]:
            return f"{aux} {subject}?"
        else:
            return None
    else:
        # Use "did": "did I write?"
        return f"did {subject} {stem}?"


def segment_translations(lemma: str, features: dict, translations: dict[str, str], past_translations: dict[str, str]) -> dict[str, Optional[str]]:
    """
    Build progressive translations for each segment role.
    
    Args:
        lemma: Finnish verb lemma
        features: grammatical features dict (TENSE, PERSON, CLITIC, etc.)
        translations: Finnish lemma → English gloss mapping
        past_translations: Finnish lemma → English past phrase mapping
    
    Returns:
        Dict mapping segment role to translation string (or None if unavailable)
        Keys: "stem", "tense", "person", "question"
    """
    return {
        "stem": get_stem_phrase(lemma, translations),
        "tense": get_tense_phrase(lemma, features, past_translations),
        "person": get_person_phrase(lemma, features, translations, past_translations),
        "question": get_question_phrase(lemma, features, translations, past_translations)
    }


def annotate_segments(segments: list[dict], lemma: str, features: dict, 
                      translations: Optional[dict[str, str]], 
                      past_translations: Optional[dict[str, str]]) -> None:
    """
    Annotate segments list in-place with translation field.
    
    Args:
        segments: list of segment dicts (modified in-place)
        lemma: Finnish verb lemma
        features: grammatical features dict
        translations: Finnish lemma → English gloss mapping (optional)
        past_translations: Finnish lemma → English past phrase mapping (optional)
    """
    if not translations or not past_translations:
        # No translation data available
        for seg in segments:
            seg["translation"] = None
        return
    
    # Check if there's a KO clitic in the segments
    # KO has variants: ko, kö (vowel harmony)
    has_ko_clitic = any(
        seg.get("role") == "clitic" and seg.get("surface") in ["ko", "kö"]
        for seg in segments
    )
    
    # Build features dict with CLITIC if we found KO
    features_with_clitic = features.copy()
    if has_ko_clitic:
        features_with_clitic["CLITIC"] = "KO"
    
    trans_map = segment_translations(lemma, features_with_clitic, translations, past_translations)
    
    for seg in segments:
        role = seg.get("role")
        # Only KO clitic gets question translation
        if role == "clitic" and seg.get("surface") in ["ko", "kö"]:
            seg["translation"] = trans_map.get("question")
        elif role == "clitic":
            # Other clitics get descriptive hint
            surface = seg.get("surface", "")
            hint_info = CLITIC_HINTS.get(surface)
            if hint_info:
                seg["translation"] = hint_info[0]
                seg["translation_note"] = hint_info[1]
                if len(hint_info) > 2 and hint_info[2]:
                    seg["translation_link"] = hint_info[2]
            else:
                seg["translation"] = None
        else:
            seg["translation"] = trans_map.get(role)
