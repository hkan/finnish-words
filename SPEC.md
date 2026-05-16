# Finnish Word Breakdown — Project Spec

## Goal

A tool that takes a Finnish word and breaks it down into its morphological components, showing the dictionary root and each morpheme with its grammatical role. Built for Finnish learners who want to understand *what* each part of a word contributes.

---

## Output Format

Given input `tiesitkö`, the API returns:

```json
{
  "word": "tiesitkö",
  "unknown": false,
  "readings": [
    {
      "word_id": "tietää",
      "root": "tie",
      "upos": "VERB",
      "segments": [
        { "surface": "tie", "role": "stem",   "label": "root" },
        { "surface": "si",  "role": "tense",  "label": "past tense marker (-si)" },
        { "surface": "t",   "role": "person", "label": "2nd person singular (you)" },
        { "surface": "kö",  "role": "clitic", "label": "question particle (-kö)" }
      ],
      "features": {
        "mood": "indicative mood",
        "tense": "past tense",
        "pers": "2nd person singular",
        "voice": "active voice",
        "num": "singular"
      }
    }
  ]
}
```

Key principles:
- `word_id` is the dictionary form (lemma) extracted from Voikko's FST output.
- `root` is the morphological root used by the chain builder — the part the lemma derives from after stripping infinitive endings and undoing gradation where applicable.
- `segments` is our hand-built morpheme chain (see `backend/chain.py`). Each segment has a `surface` string, a `role` (`stem` / `tense` / `person` / `clitic` / ...), and a human-readable `label`.
- `features` is a dict of grammatical features (mood, tense, person, voice, case, ...) translated to readable strings.
- Multiple readings are returned when a word is ambiguous (e.g. `opin` = both past 1sg and present 1sg of `oppia`).
- Readings with a segment chain are sorted before chainless siblings.

---

## How Voikko Is Used

Voikko (`libvoikko`) is the sole morphological analyser. One call per request:

```python
from libvoikko import Voikko
voikko = Voikko("fi")
results = voikko.analyze("tiesitkö")
# [{'BASEFORM': 'tietää', 'CLASS': 'teonsana', 'MOOD': 'indicative',
#   'TENSE': 'past_imperfective', 'PERSON': '2', 'NUMBER': 'singular',
#   'FSTOUTPUT': '[Lt][Xp]tietää[X]ties[Tt][Ai][P2][Ny][Ef]it[Fko][Ef]kö', ...}]
```

`main.py:_normalise()` maps Voikko's vocabulary (CLASS, MOOD, TENSE, PERSON, NUMBER, SIJAMUOTO) to our internal feature codes (`VERB`/`INDV`/`PAST`/`SG2`/`ACT`/...). The lemma is pulled from FSTOUTPUT's `[Xp]...[X]` tag so participles like `tehnyt` correctly surface `tehdä` as the verb lemma.

For verbs with a derivable root, `stem.py` extracts the morphological root from Voikko's FSTOUTPUT (with a small exceptions table for `juosta`/`nousta`), and `chain.py` builds the segment chain by:
1. Peeling clitics off the end greedily (`-kin`, `-kö`, `-han`, `-pa`, etc., including stacks).
2. Peeling the person ending.
3. Identifying the tense marker (`-i-`, `-si-`).
4. Emitting the stem with appropriate gradation handling.

Verb-type-specific logic covers types 1–4, irregular forms (`olla` → `on`/`ovat`), alternating stems (`tehdä`, `nähdä`), and overrides for `käydä`, `saada`, `syödä`, `juoda`, `tuoda`, `viedä`, `myydä`, `lyödä`.

Voikko (and `voikko-fi`) is GPL-licensed; we ship it via the standard Debian packages inside Docker.

---

## Architecture

```
input word
    ↓
voikko.analyze(word)         (libvoikko, single call)
    ↓
_normalise()                 (map CLASS/MOOD/TENSE → internal codes)
    ↓
get_verb_root(lemma)         (extract root from FSTOUTPUT; stem.py)
    ↓
build_segments(...)          (peel clitics + person + tense; emit chain; chain.py)
    ↓
dedup + sort + filter        (collapse duplicate readings; chained-first)
    ↓
JSON response  →  React frontend
```

**Stack**: FastAPI (Python) backend + React + Vite frontend (no router — single screen). See HOSTING.md for infrastructure decisions.

---

## Known Limitations

- **Derivational morphology is not surfaced.** We expose inflectional morphology only (how a word is conjugated or declined). The connection from `keksintö` back to the verb `keksiä` via the deverbal-noun suffix `-ntO` is not shown.
- **Passive forms** are detected (`PERSON=4` → `VOICE=PASS`) but no segment chain is built for them.
- **Stacked clitic order** has at least one known Voikko gap: `menithänkö` is rejected even though `menithän` and `menitköhän` are accepted.

---

## Decisions Log

| Question | Decision |
|---|---|
| Multiple readings | Show all; chained readings first |
| Interface | Local web app first, then hosted |
| Label depth | Grammatical role + human-readable label per segment |
| Analyser | Voikko-only (Omorfi removed) |
| Segmentation | Custom chain builder in `chain.py`, not the analyser's segmenter |
| Stem | Always shown as its own row labeled "root" |
| Unknown words | Return `"unknown": true`, show plain message in UI |
| URL sync | `?word=` debounced 1s on input; popstate fires immediately |
