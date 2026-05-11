# Omorfi — Usage Reference

Omorfi is installed at `../omorfi/` and built as a Docker image tagged `omorfi`. It is **not** available on the host machine — all usage is inside Docker.

---

## Python API (used by the backend)

The preferred interface. Transducers are loaded once at startup and called in-process.

```python
from omorfi import Omorfi, Token

omorfi = Omorfi()
omorfi.load_analyser("/app/src/generated/omorfi.analyse.hfst")
omorfi.load_labelsegmenter("/app/src/generated/omorfi.labelsegment.hfst")
```

**Analyse** — dictionary lemma + feature tags:
```python
token = Token("tiesitkö")
omorfi.analyse(token)

for a in token.analyses:
    print(a.raw)
    # [WORD_ID=tietää][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PAST][PERS=SG2][CLIT=KO][WEIGHT=0.0]
    print(a.get_lemmas())   # ['tietää']
    print(a.get_ufeats())   # {'Tense': 'Past', 'Person': '2', ...}
```

Multiple analyses are returned for ambiguous words.

**Label segment** — surface morphemes with embedded grammatical labels:
```python
token = Token("tiesitkö")
omorfi.labelsegment(token)

for s in token.labelsegmentations:
    print(s.raw)
    # ti{STUB}[VERB]es{MB}i{MB}t[ACTV][PAST][SG2]{MB}kö[KO]
```

**Labelsegment format:**
- `{STUB}` — marks the end of the root stub (surface stem)
- `{MB}` — morpheme boundary; separates segments
- `[TAG]` — grammatical label for the preceding segment
- Labels follow the *last* surface segment of a morphological slot; intermediate phonological material (e.g. the past theme vowel `i`) is left unlabeled

---

## CLI / Bash (for manual inspection)

### Analyse

```bash
echo "tiesitkö" | docker run -i omorfi bash -c "./src/bash/omorfi-analyse-text.sh"
```
```
tiesitkö    [WORD_ID=tietää][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PAST][PERS=SG2][CLIT=KO]
```

### Labelsegment

```bash
echo "tiesitkö" | docker run -i omorfi bash -c "hfst-lookup src/generated/omorfi.labelsegment.hfst"
```
```
tiesitkö    ti{STUB}[VERB]es{MB}i{MB}t[ACTV][PAST][SG2]{MB}kö[KO]
```

### Segment (quick visual check)

```bash
echo "tiesitkö" | docker run -i omorfi bash -c "./src/bash/omorfi-segment.sh"
```
```
ties→ ←i→ ←t→ ←kö
```

### Generate

```bash
echo "[WORD_ID=tietää][UPOS=VERB][VOICE=ACT][MOOD=INDV][TENSE=PAST][PERS=SG2]" \
  | docker run -i omorfi bash -c "./src/bash/omorfi-generate.sh"
```
```
tiesit
```
