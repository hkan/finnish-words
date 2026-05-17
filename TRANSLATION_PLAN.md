# Progressive English Translations — Implementation Plan

## Project context

This is a Finnish morpheme breakdown app. The backend (`backend/`) is a FastAPI app using
[libvoikko](https://voikko.puimula.org/) to analyse Finnish words into lemma + grammatical
features, then `backend/chain.py` builds an ordered list of morpheme **segments** (stem,
tense marker, person ending, clitics). The frontend (`frontend/`) is a React/Vite app.

Existing data file `backend/data/fi_en.json` (12 MB, committed) maps Finnish lemma →
English gloss, generated from a [kaikki.fi](https://kaikki.org/dictionary/Finnish/)
Wiktionary JSONL dump by `scripts/build_translations.py`. The JSONL dumps are **not**
committed — they live in the project root:
- `kaikki.org-dictionary-Finnish.jsonl`
- `kaikki.org-dictionary-English.jsonl`

The backend already returns `reading.translation` (the top-level gloss) in the API
response. This plan extends that by adding a `"translation"` field to **each segment**,
showing the cumulative English meaning as morphemes are added.

### TDD approach
Write failing tests first, then implement until they pass. Commit each phase separately.
Run tests from `backend/` with `python -m pytest tests/`.

---

## Goal

Show a cumulative English translation for each morpheme segment in the breakdown.

Example for `kirjoitin`:
```
kirjoit     write
  + i  →  kirjoiti     wrote
  + n  →  kirjoitin    I wrote
```

Example for `synnyin`:
```
synnyi      be born
  + i  →  synnyi       was born
  + n  →  synnyin      I was born
```

Question clitic adds question form: `kirjoitinko` → `"did I write?"`  
"Be" verbs use inversion: `synnyinkö` → `"was I born?"`

---

## Phase 1 — Build `fi_en_past.json`

**File:** `scripts/build_translations.py` (extend existing script)

Add two new CLI args: `--en-input <path>` and `--past-output <path>`.

New `extract_past()` function:

1. Load `fi_en.json` (Finnish lemma → English gloss, e.g. `"syntyä" → "to be born"`)
2. Stream English JSONL (`kaikki.org-dictionary-English.jsonl`), collect `verb` entries:
   - English word → simple past string
   - Accept: `tags` contains `"past"` but NOT `"participle"`, `"archaic"`, `"subjunctive"`
   - For `"be"`: only take `"was"` (SG form); `"were"` is handled in the composer
3. For each Finnish verb lemma in `fi_en.json`:
   - Strip `"to "` and leading `(qualifier)` / `[qualifier]` from gloss → verb phrase (e.g. `"be born"`)
   - Extract first word → e.g. `"be"` → look up past → `"was"`
   - Combine: `"was" + " born"` → `"was born"`
4. Output: `backend/data/fi_en_past.json`

**Tests:** `scripts/tests/test_extract_past.py`
- Unit tests on phrase-building logic with mock gloss + past data
- No JSONL file needed (mock the dicts directly — don't read from disk)

### English JSONL entry shape (for reference)
```json
{
  "word": "write",
  "pos": "verb",
  "forms": [
    {"form": "wrote", "tags": ["past"]},
    {"form": "written", "tags": ["past", "participle"]}
  ]
}
```
For `"be"`, the forms include `{"form": "was", "tags": ["past"]}` and
`{"form": "were", "tags": ["past"]}`. We only want `"was"` at this stage.

---

## Phase 2 — `backend/translate.py`

New module in `backend/`. New file — does not exist yet.

Core function:

```python
def segment_translations(lemma, features, translations, past_translations) -> dict[str, str | None]:
    # Returns e.g.:
    # {"stem": "be born", "tense": "was born", "person": "I was born", "question": "was I born?"}
```

### Rules

| Segment role | Translation shown          | Logic                                                         |
|--------------|----------------------------|---------------------------------------------------------------|
| `stem`       | base verb phrase           | gloss stripped of `"to "` (from `translations`)               |
| `tense`      | past/present phrase        | value from `past_translations` (e.g. `"was born"`, `"wrote"`) |
| `person`     | subject + phrase           | add pronoun; "be" verbs: was→were for SG2/PL                  |
| `clitic` KO  | question form              | "be" verbs: invert (`"was I born?"`); others: `"did I write?"` |

### Subject pronouns

| Code | Subject      |
|------|--------------|
| SG1  | I            |
| SG2  | you          |
| SG3  | he/she/it    |
| PL1  | we           |
| PL2  | you          |
| PL3  | they         |
| SG0  | one (skip for now — SG0 surface is identical to SG3, handled there) |

### "Be" verb detection
A reading uses "be" conjugation when `past_translations[lemma]` starts with `"was"` or `"were"`.

- SG1/SG3 → keep `"was"`
- SG2/PL1/PL2/PL3 → substitute `"were"`

### Present tense
For present tense (`features["TENSE"] == "PRESENT"`), `past_translations` doesn't apply.
The `"tense"` slot should show the base phrase (same as stem) since English present tense
needs no auxiliary. The `"person"` slot adds the subject: `"I write"`, `"you go"`, etc.
For `"be"` verbs: `"I am"`, `"you are"`, `"he/she is"`, `"we are"` etc. — but this can be
deferred; just handle past tense fully first.

### Missing data
Return `None` for any entry where data is missing. Caller skips rendering. Never crash.

**Tests:** `backend/tests/test_translate.py`

| Case                                 | Expected `person`        |
|--------------------------------------|--------------------------|
| `kirjoittaa` PAST SG1                | `"I wrote"`              |
| `syntyä` PAST SG1                    | `"I was born"`           |
| `syntyä` PAST PL1                    | `"we were born"`         |
| `mennä` PAST SG2                     | `"you went"`             |
| `olla` PAST SG3                      | `"he/she was"`           |
| `kirjoittaa` PAST SG1 + question     | `"did I write?"`         |
| `syntyä` PAST SG1 + question         | `"was I born?"`          |
| unknown lemma                        | all `None`, no crash     |

---

## Phase 3 — Wire into segments

**`backend/chain.py`:**
- `build_segments` signature currently: `(surface, root, upos, features, lemma, lang)`
- Add optional `translations` and `past_translations` args (both default `None`)
- After building the segment list, call `translate.annotate_segments(segments, lemma, features, translations, past_translations)`
- This mutates each segment dict in-place, adding `"translation": str | None`

**`backend/main.py`:**
- The lifespan loader already reads `fi_en.json` into `_TRANSLATIONS`
- Add: read `fi_en_past.json` into `_PAST_TRANSLATIONS` (same pattern)
- In the `/analyse` endpoint, `build_segments` is called around line 207 — pass both dicts

**Tests:** Add to `backend/tests/test_api.py` — check that `/analyse?word=tiesitkö` returns
segment-level `translation` fields on the first chained reading.

---

## Phase 4 — Frontend

**`frontend/src/App.jsx`** — `Reading` component (around line 140):
- Each `step` div currently shows `step-surface` and `step-label`
- Add a `step-translation` span showing `s.translation` when present
- Position: right-aligned on the same row as `step-surface`, or below — match the mockup:
  ```
  kirjoit                    write
    + i  →  kirjoiti         wrote
    + n  →  kirjoitin        I wrote
  ```

**`frontend/src/App.css`:**
- Add `.step-translation` — small, italic, muted color (`#888` or similar), `margin-left: auto`

No new JS dependencies needed.

---

## Decisions

- **"be" + plural person:** use `"were"` for SG2/PL*, `"was"` for SG1/SG3
- **Translations in non-EN UI:** still show (same behaviour as existing lemma translation)
- **Missing gloss / missing past:** silently skip — no translation for that segment
- **SG0:** surface form is identical to SG3; skip dedicated handling for now

---

## Commit plan

1. `test_extract_past.py` + extend `build_translations.py`
   → `"feat: extract English past forms for Finnish verb glosses"`
2. `test_translate.py` + `translate.py`
   → `"feat: add segment translation composer"`
3. Wire into `chain.py` + `main.py`
   → `"feat: attach progressive translations to segments"`
4. Frontend changes
   → `"feat: display per-segment translations in breakdown UI"`

---

## Data files

| File                         | Description                                    | License     |
|------------------------------|------------------------------------------------|-------------|
| `backend/data/fi_en.json`    | Finnish lemma → English gloss (250k entries)   | CC BY-SA 4.0 |
| `backend/data/fi_en_past.json` | Finnish verb lemma → English past phrase     | CC BY-SA 4.0 |

Both generated from kaikki.fi Wiktionary dumps. Attribution already added to app drawer.
