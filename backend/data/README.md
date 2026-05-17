# Translation Data

These files contain Finnish → English translation mappings derived from Wiktionary.

## Files

- `fi_en.json` — Finnish lemma → English gloss (250,939 entries)
- `fi_en_past.json` — Finnish verb → English past tense phrase (68,042 entries)

## License

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

These files are derivative works of [Wiktionary](https://en.wiktionary.org) content, processed via [kaikki.org](https://kaikki.org) JSONL dumps.

Original Wiktionary content is licensed under CC BY-SA 4.0.  
These derived files maintain the same license.

### Attribution
- Source: English Wiktionary (https://en.wiktionary.org)
- Extraction: kaikki.org (https://kaikki.org/dictionary/Finnish/)
- Processing: `tools/build_translations.py` in this repository

## Generation

To regenerate these files:

1. Download JSONL dumps from kaikki.org:
   - https://kaikki.org/dictionary/Finnish/
   - https://kaikki.org/dictionary/English/

2. Run the extraction script:
```bash
python3 tools/build_translations.py \
  --input kaikki.org-dictionary-Finnish.jsonl \
  --output backend/data/fi_en.json \
  --en-input kaikki.org-dictionary-English.jsonl \
  --past-output backend/data/fi_en_past.json
```

See `tools/build_translations.py` and `tools/README.md` for details.
