# Finnish Word Breakdown — Project Spec

## Goal

A tool that takes a Finnish word and breaks it down into its morphological components, showing the dictionary root and each morpheme with its grammatical role. Built for Finnish learners who want to understand *what* each part of a word contributes.

---

## Actual Output Format

Given input `tiesitkö`, the API returns:

```json
{
  "word": "tiesitkö",
  "unknown": false,
  "readings": [
    {
      "word_id": "tietää",
      "morphemes": [
        { "surface": "ties", "roles": ["stem"] },
        { "surface": "i",    "roles": [] },
        { "surface": "t",    "roles": ["active voice", "past tense", "2nd person singular"] },
        { "surface": "kö",   "roles": ["question particle"] }
      ]
    }
  ]
}
```

Key principles:
- `word_id` is the dictionary form (from Omorfi's analyser)
- `stem` is the surface root as it appears in the inflected word — distinct from the dictionary form
- Morphemes with no label from Omorfi are surfaced with an empty `roles` array rather than dropped or merged. This is honest: the `i` is a real morpheme boundary but Omorfi doesn't label it independently.
- Multiple readings are returned when a word is ambiguous, ordered by corpus frequency where available

Surface change explanations (e.g. why `tietää` → `ties`) are out of scope for v1 — see SURFACE-CHANGES.md.

---

## How Omorfi Is Used

Two Omorfi functions are called per request:

**Analyser** (`omorfi.analyse.hfst`) — returns the dictionary root and full feature set:
```
tiesitkö  →  [WORD_ID=tietää][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PAST][PERS=SG2][CLIT=KO]
```
Used for: `word_id` (dictionary form).

**Label segmenter** (`omorfi.labelsegment.hfst`) — returns surface morphemes with embedded grammatical labels:
```
tiesitkö  →  ti{STUB}[VERB]es{MB}i{MB}t[ACTV][PAST][SG2]{MB}kö[KO]
```
Used for: morpheme segmentation and role labels.

Format: `{STUB}` marks the root stub, `{MB}` marks morpheme boundaries, `[TAG]` labels follow the segment they describe. Labels are attached to the *last* segment of a morphological slot — intermediate phonological material (like the past tense theme vowel `i`) is left unlabeled.

Our parser reconstructs morphemes from this format and translates raw labels (`[SG2]`, `[KO]`, `[PAST]`) into human-readable strings via a lookup table.

Omorfi is Apache 2.0 licensed — compatible with free distribution.

---

## Architecture

```
input word
    ├── load_analyser  →  word_id (dictionary lemma)
    └── load_labelsegmenter  →  surface morphemes + embedded labels
            ↓
        parse_labelsegment()
            ↓
        LABEL_MAP translation table
            ↓
        JSON response  →  React frontend
```

**Stack**: FastAPI (Python) backend + React + Vite frontend (no router — single screen).
Omorfi Python bindings loaded once at startup, called in-process per request.
See HOSTING.md for infrastructure decisions.

---

## Known Limitations

**Derivational morphology is not covered.** Omorfi's labelsegmenter handles inflectional morphology only — how a word is declined or conjugated from its base form. It does not trace how that base form was itself derived from another word. For example, `keksintö` is segmented as `keksin` (stem) + `tö` (nominative singular), but the connection back to the verb `keksiä` — via the deverbal noun suffix `-ntO` — is invisible to Omorfi. `keksintö` is simply a lexical entry in its own right.

---

## Decisions Log

| Question | Decision |
|---|---|
| Multiple readings | Show all, most common first |
| Interface | Local web app first, then hosted |
| Label depth | Grammatical role only for v1; surface change explanations deferred (see SURFACE-CHANGES.md) |
| Omorfi process model | Python bindings in-process via `load_analyser` + `load_labelsegmenter` |
| Unlabeled morphemes | Surface them with empty roles — don't drop or merge into adjacent segments |
| Stem | Always shown as its own row labeled "stem" |
| Unknown words | Return `"unknown": true`, show plain message in UI |
