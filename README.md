# Finnish Word Breakdown

A tool for understanding how Finnish words are constructed. Enter a Finnish word and see it broken down into its grammatical components: root, tense markers, person endings, clitics, and more—with progressive English translations showing how meaning builds up morpheme by morpheme.

**Example:** `tiesitkö` → `tie` (root: know) + `si` (past) + `t` (you) + `kö` (question) = **"did you know?"**

Built by a Finnish learner for other learners. This is not a professional linguistic tool—it synthesizes information from existing resources (Voikko, Wiktionary, online grammar sites) to help decode inflected Finnish words.

## Quick Start

**Hosted version (may not be permanent):**  
https://finnish-words.hakan-d2d.workers.dev/

**Recommended: Run locally with Docker:**
```bash
git clone https://github.com/hkan/finnish-words.git
cd finnish-words
docker-compose up
```

Then open http://localhost:5273 in your browser.

## What This Tool Does

### Word Breakdown
Shows how Finnish words are inflected—each grammatical piece labeled and explained.

**Example:** `kirjoitin` (I wrote)
- `kirjoit` — root
- `i` — past tense marker
- `n` — 1st person singular (I)

### Progressive English Translations
Shows how meaning accumulates as morphemes are added:

```
kirjoit         write
  + i  →  kirjoiti     wrote
  + n  →  kirjoitin    I wrote
```

For "be" verbs, conjugation adjusts automatically:
```
synn            be born
  + yi  →  synnyi      was born
  + n  →  synnyin      I was born
```

### Question Forms
Question clitics (`-ko/-kö`) show the full question:

```
kirjoitin              I wrote
  + ko  →  kirjoitinko     did I write?
```

"Be" verbs use inversion:
```
synnyin                I was born
  + kö  →  synnyinkö       was I born?
```

### Grammar Documentation Links
Non-question clitics link to detailed grammar explanations on [uusikielemme.fi](https://uusikielemme.fi):

- `-han/-hän` (emphasis) → clickable link to grammar page
- `-kin/-kaan/-kään` (also/even/not even) → clickable link
- `-pa/-pä` (contrast) → clickable link

Hover over clitic translations to see tooltips with explanations.

### Multi-Language Interface
UI available in English, Finnish, and Turkish. Labels and explanations adjust automatically.

## Known Limitations

The tool has specific constraints. Here's what it can and cannot do:

#### Inflectional Morphology Only
The tool shows how words *inflect* (change endings based on grammar) but not how they *derive* (form new words from roots).

**What this means:** `keksintö` (invention) comes from the verb `keksiä` (to invent) + the noun-forming suffix `-ntö`. The tool won't show this connection. It only shows that `keksintö` is a noun and how it inflects:
- `keksintö` → nominative
- `keksinnön` → genitive (shows the `ö → ö` change)

Similarly, `juoksija` (runner) derives from `juosta` (to run) + `-ja` (agent suffix), but the tool treats `juoksija` as a standalone noun.

#### Passive Voice Not Segmented
The tool detects passive voice but doesn't break it into segments.

**Example:** `kirjoitettiin` (it was written) is recognized as passive voice of `kirjoittaa`, but you won't see the morpheme breakdown. Only active voice forms get segment-by-segment analysis.

#### Present Tense: Partial Support
Present tense verbs show segments but not English translations.

**Example:** `kirjoitan` (I write)
- ✓ Shows segments: `kirjoit` + `a` + `n`
- ✗ No progressive English translations yet (only past tense has full translation support)

The dictionary translation still appears at the top ("to write"), but the step-by-step meaning build-up is only available for past tense forms.

#### Some Voikko Analysis Gaps
The tool relies on [Voikko](https://voikko.puimula.org/) for morphological analysis. If Voikko can't parse a word, neither can this tool.

**Known issue:** Certain clitic stacks fail. `menithänkö` (did you go + emphasis + question) returns "Unknown word" even though both `menithän` and `menitköhän` work individually. This is a Voikko limitation.

#### English Translation Coverage
- **Verbs:** ~98% coverage (9,131 of 9,347 verb lemmas)
- **All words:** ~27% coverage (68,042 of 250,939 dictionary entries)

**What this means:** Most verbs will show progressive English translations, but many nouns, adjectives, and other word types won't. When translations aren't available, you'll still see the morpheme segments and grammatical labels—just not the English meaning.

## How It Works

### Architecture
```
Finnish word input
    ↓
Voikko morphological analysis (libvoikko)
    ↓
Normalize features (CLASS/MOOD/TENSE → internal codes)
    ↓
Extract verb root (from Voikko's FSTOUTPUT)
    ↓
Build morpheme segments (peel clitics, person, tense)
    ↓
Add English translations (from Wiktionary data)
    ↓
JSON response → React frontend
```

### Core Components

**Voikko (`libvoikko`):** GPL-licensed morphological analyser for Finnish. Provides lemma, grammatical features, and finite-state transducer output.

**Custom Segmentation (`backend/chain.py`):** Hand-built logic to break inflected forms into individual morphemes. Handles:
- Finnish verb types 1-4
- Irregular verbs (`olla`, `tehdä`, `nähdä`, etc.)
- Consonant gradation (strong/weak stem alternation)
- Clitic stacks (peeled greedily from right to left)

**Translation Data (`backend/data/`):**
- `fi_en.json` — 250k Finnish lemma → English gloss mappings
- `fi_en_past.json` — 68k Finnish verb → English past tense phrases
- Generated from [Wiktionary](https://en.wiktionary.org) via [kaikki.org](https://kaikki.org) JSONL dumps

**Progressive Translation Logic (`backend/translate.py`):**
- Builds cumulative translations for each morpheme role
- Handles "be" verb conjugation (was/were)
- Generates question forms (inversion vs "did" auxiliary)
- Adds clitic hints with documentation links

### Tech Stack
- **Backend:** Python, FastAPI, libvoikko
- **Frontend:** React, Vite
- **Deployment:** Docker Compose (local), Cloudflare Workers (hosted)
- **Data:** Wiktionary (CC BY-SA 4.0)

## Running Locally

### Prerequisites
- Docker and Docker Compose

### Setup
```bash
git clone https://github.com/hkan/finnish-words.git
cd finnish-words
docker-compose up
```

The backend API runs on http://localhost:8000  
The frontend runs on http://localhost:5273

### Development
Backend code is in `backend/`, automatically reloaded via uvicorn's `--reload` flag.  
Frontend code is in `frontend/`, hot-reloaded via Vite.

### Running Tests
```bash
./test.sh
```

Tests are in `backend/tests/` (pytest).

## Data Sources & Attribution

### Morphological Analysis
- **[Voikko](https://voikko.puimula.org/)** (GPL) — Finnish morphological analyser
- **voikko-fi** — Finnish language data for Voikko

### Translation Data
- **[Wiktionary](https://en.wiktionary.org)** (CC BY-SA 4.0) — English glosses and past tense forms
- **[kaikki.org](https://kaikki.org)** — Wiktionary data extracts in structured JSONL format

Translation data files (`backend/data/fi_en*.json`) are derivatives of Wiktionary content and remain under CC BY-SA 4.0.

### Grammar Documentation
- **[uusikielemme.fi](https://uusikielemme.fi)** — Finnish grammar explanations (linked from clitic hints)

## License

**Code:** GNU General Public License v3.0 (GPLv3)

**Translation Data:** Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)  
Files `backend/data/fi_en.json` and `backend/data/fi_en_past.json` are derived from Wiktionary.

**Dependencies:**
- Voikko and voikko-fi are GPL-licensed
- This project complies with GPL requirements for derivative works

See LICENSE file for full GPLv3 text.

## Caveats

- This tool was built by a Finnish learner, not a linguistics professional
- The implementation is based on information gathered from online resources (grammar sites, documentation, forum posts)
- Morphological segmentation rules are hand-coded based on understanding of Finnish grammar patterns
- The hosted version (https://finnish-words.hakan-d2d.workers.dev/) may not remain available indefinitely
- **Recommended usage:** Clone the repository and run locally via Docker

## Contributing

This is primarily a personal learning project. While the code is open source, active contribution solicitation or maintenance of submitted PRs is not guaranteed.

If you find issues or have suggestions, feel free to [open an issue](https://github.com/hkan/finnish-words/issues) on GitHub.

## See Also

- [SPEC.md](SPEC.md) — Detailed technical specification
- [TRANSLATION_PLAN.md](TRANSLATION_PLAN.md) — Implementation plan for progressive translations feature
