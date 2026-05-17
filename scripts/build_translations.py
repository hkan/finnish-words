#!/usr/bin/env python3
"""
Extract Finnish → English glosses from a kaikki.fi Wiktionary JSONL dump.

Usage:
    python scripts/build_translations.py \
        --input kaikki.org-dictionary-Finnish.jsonl \
        --output backend/data/fi_en.json

Source data: https://kaikki.org/dictionary/Finnish/
License: CC BY-SA 4.0 (inherited from Wiktionary)
"""

import argparse
import json
import re
import sys
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",  required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    extract(args.input, args.output)


if __name__ == "__main__":
    main()
