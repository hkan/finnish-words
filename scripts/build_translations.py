#!/usr/bin/env python3
"""
Extract Finnish → English glosses from a kaikki.fi Wiktionary JSONL dump.

Usage:
    # Extract Finnish → English glosses:
    python scripts/build_translations.py \
        --input kaikki.org-dictionary-Finnish.jsonl \
        --output backend/data/fi_en.json

    # Extract Finnish verb → English past tense:
    python scripts/build_translations.py \
        --input kaikki.org-dictionary-Finnish.jsonl \
        --output backend/data/fi_en.json \
        --en-input kaikki.org-dictionary-English.jsonl \
        --past-output backend/data/fi_en_past.json

Source data: https://kaikki.org/dictionary/Finnish/ and https://kaikki.org/dictionary/English/
License: CC BY-SA 4.0 (inherited from Wiktionary)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# Prefer verb entries when a word has multiple POS entries (e.g. "olla" as
# both verb and particle). Within a POS, pick the first non-empty gloss.
POS_PRIORITY = {"verb": 0, "adj": 1, "adv": 2, "noun": 3}

# Strip parenthetical and bracketed qualifiers from the front of a gloss.
_LEADING_RE = re.compile(r"^[\(\[][^\)\]]+[\)\]]\s*")


def clean_gloss(gloss: str) -> str:
    # Strip leading qualifiers like "(transitive)" or "[with elative]" repeatedly.
    while _LEADING_RE.match(gloss):
        gloss = _LEADING_RE.sub("", gloss).strip()
    # Keep only the primary sense (before first semicolon).
    return gloss.split(";")[0].strip()


def extract(input_path: Path, output_path: Path) -> None:
    # word → (pos_priority, gloss)
    best: dict[str, tuple[int, str]] = {}

    with input_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 100_000 == 0:
                print(f"  {i:,} lines processed…", file=sys.stderr)
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            word = entry.get("word", "").strip()
            if not word:
                continue

            pos = entry.get("pos", "")
            priority = POS_PRIORITY.get(pos, 99)

            for sense in entry.get("senses", []):
                glosses = sense.get("glosses", [])
                if not glosses:
                    continue
                gloss = clean_gloss(glosses[0])
                if not gloss:
                    continue

                existing = best.get(word)
                if existing is None or priority < existing[0]:
                    best[word] = (priority, gloss)
                break  # first valid sense per entry is enough

    result = {word: gloss for word, (_, gloss) in sorted(best.items())}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {len(result):,} entries → {output_path}", file=sys.stderr)


def extract_past_form(word: str, forms: list[dict]) -> Optional[str]:
    """Extract simple past form from an English verb's forms list.
    
    Returns the first valid past form, excluding participles, archaic,
    and subjunctive forms. For 'be', returns 'was' (singular form).
    """
    for form_entry in forms:
        tags = form_entry.get("tags", [])
        if "past" not in tags:
            continue
        if any(skip in tags for skip in ["participle", "archaic", "subjunctive"]):
            continue
        form = form_entry.get("form", "").strip()
        if form:
            # For 'be', prefer 'was' over 'were'
            if word == "be" and form == "were":
                continue
            return form
    return None


def build_past_gloss(gloss: str, past_forms: dict[str, str]) -> Optional[str]:
    """Convert a Finnish verb gloss to English past tense.
    
    Examples:
        'to write' + {'write': 'wrote'} → 'wrote'
        'to be born' + {'be': 'was'} → 'was born'
        '(intransitive) to go' + {'go': 'went'} → 'went'
    """
    if not gloss:
        return None
    
    # Clean the gloss using same logic as main extract
    gloss = clean_gloss(gloss)
    
    if not gloss:
        return None
    
    # Remove "to " prefix if present
    if gloss.startswith("to "):
        gloss = gloss[3:]
    
    if not gloss:
        return None
    
    # More aggressive cleaning: remove all bracketed/parenthetical content
    # and take only the core verb phrase before any qualifier
    # e.g., "go [with illative...] (move away...)" → "go"
    # e.g., "know [with elative...], be aware of" → "know"
    import re
    # Remove all [...] and (...) content
    gloss = re.sub(r'\[[^\]]*\]', '', gloss)
    gloss = re.sub(r'\([^\)]*\)', '', gloss)
    # Take only up to first comma (for multi-part definitions)
    gloss = gloss.split(',')[0].strip()
    
    if not gloss:
        return None
    
    # Split into words, look up first word's past form
    words = gloss.split()
    if not words:
        return None
    
    first_word = words[0]
    past = past_forms.get(first_word)
    
    if past is None:
        return None
    
    # Reconstruct with past form
    if len(words) == 1:
        return past
    else:
        return past + " " + " ".join(words[1:])


def build_past_glosses(fi_en: dict[str, str], en_past: dict[str, str]) -> dict[str, str]:
    """Build Finnish verb lemma → English past phrase mappings.
    
    Only processes entries that look like verb glosses (contain 'to' or successfully
    convert to past tense).
    """
    result = {}
    
    for lemma, gloss in fi_en.items():
        # Try to build past gloss
        past_gloss = build_past_gloss(gloss, en_past)
        
        # Only include if we successfully generated a past form
        if past_gloss:
            result[lemma] = past_gloss
    
    return result


def extract_past(fi_path: Path, en_path: Path, output_path: Path) -> None:
    """Extract English past forms and build Finnish verb → past tense mappings."""
    print(f"Loading Finnish glosses from {fi_path}...", file=sys.stderr)
    with fi_path.open(encoding="utf-8") as f:
        fi_en = json.load(f)
    
    print(f"Extracting English past forms from {en_path}...", file=sys.stderr)
    en_past: dict[str, str] = {}
    
    with en_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i % 100_000 == 0:
                print(f"  {i:,} lines processed…", file=sys.stderr)
            
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if entry.get("pos") != "verb":
                continue
            
            word = entry.get("word", "").strip()
            if not word or word in en_past:
                continue
            
            forms = entry.get("forms", [])
            past_form = extract_past_form(word, forms)
            
            if past_form:
                en_past[word] = past_form
    
    print(f"Extracted {len(en_past):,} English past forms", file=sys.stderr)
    print(f"Building Finnish → English past glosses...", file=sys.stderr)
    
    result = build_past_glosses(fi_en, en_past)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))
    
    print(f"Wrote {len(result):,} entries → {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",  required=True, type=Path, help="Finnish JSONL input")
    parser.add_argument("--output", required=True, type=Path, help="Finnish→English JSON output")
    parser.add_argument("--en-input", type=Path, help="English JSONL input (for past forms)")
    parser.add_argument("--past-output", type=Path, help="Finnish→English past tense JSON output")
    args = parser.parse_args()
    
    # Always extract basic Finnish → English glosses
    extract(args.input, args.output)
    
    # If English input provided, also extract past forms
    if args.en_input and args.past_output:
        extract_past(args.output, args.en_input, args.past_output)
    elif args.en_input or args.past_output:
        print("Error: Both --en-input and --past-output must be provided together", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
