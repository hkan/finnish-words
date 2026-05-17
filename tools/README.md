# Data Preparation Tools

This directory contains one-time data preparation scripts that are not part of the main application.

## build_translations.py

Extracts Finnish → English translation mappings from [kaikki.org](https://kaikki.org) Wiktionary dumps.

### Prerequisites

Download the source data files (not included in repository):
- Finnish dictionary: https://kaikki.org/dictionary/Finnish/kaikki.org-dictionary-Finnish.jsonl (~3.6GB)
- English dictionary: https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl (~2.8GB)

Place them in the project root directory.

### Usage

**Extract basic glosses:**
```bash
python tools/build_translations.py \
  --input kaikki.org-dictionary-Finnish.jsonl \
  --output backend/data/fi_en.json
```

**Extract glosses + past tense phrases:**
```bash
python tools/build_translations.py \
  --input kaikki.org-dictionary-Finnish.jsonl \
  --output backend/data/fi_en.json \
  --en-input kaikki.org-dictionary-English.jsonl \
  --past-output backend/data/fi_en_past.json
```

### Output

- `backend/data/fi_en.json` — 250,939 entries, 12 MB
- `backend/data/fi_en_past.json` — 68,042 entries, 2.3 MB

These files are committed to the repository and used by the application.

### Testing

```bash
cd tools
python -m pytest tests/
```

### Notes

- This is a **one-time data extraction** tool
- The 6.4GB source files should **never be committed** to the repository
- Add to `.gitignore`: `kaikki.org-dictionary-*.jsonl`
- Output files are small enough to commit (15 MB total)
