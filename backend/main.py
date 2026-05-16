import re
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from libvoikko import Voikko
from stem import get_verb_root
from chain import build_segments

voikko = Voikko("fi")

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s\t%(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
)


@app.get("/health")
def health():
    return {"ready": True}


_CLASS_TO_UPOS = {
    "teonsana": "VERB",
    "nimisana": "NOUN",
    "laatusana": "ADJ",
    "seikkasana": "ADV",
    "asemosana": "PRON",
    "lukusana": "NUM",
    "suhdesana": "ADP",
    "sidesana": "CCONJ",
    "huudahdussana": "INTJ",
    "kieltosana": "AUX",
    "etunimi": "PROPN",
    "sukunimi": "PROPN",
    "paikannimi": "PROPN",
    "nimi": "PROPN",
    "lyhenne": "X",
}

_MOOD_MAP = {
    "indicative": "INDV",
    "conditional": "COND",
    "imperative": "IMPV",
    "potential": "POTN",
    "A-infinitive": "INFA",
    "E-infinitive": "INFE",
    "MA-infinitive": "INFMA",
}

_TENSE_MAP = {
    "past_imperfective": "PAST",
    "present_simple": "PRESENT",
}

_FEATURE_LABELS = {
    "TENSE": {"PAST": "past tense", "PRESENT": "present tense"},
    "MOOD": {
        "INDV": "indicative mood",
        "COND": "conditional mood",
        "IMPV": "imperative mood",
        "POTN": "potential mood",
        "INFA": "infinitive I (a-infinitive)",
        "INFE": "infinitive II (e-infinitive)",
        "INFMA": "infinitive III (ma-infinitive)",
    },
    "VOICE": {"ACT": "active voice", "PASS": "passive voice"},
    "PERS": {
        "SG1": "1st person singular",
        "SG2": "2nd person singular",
        "SG3": "3rd person singular",
        "PL1": "1st person plural",
        "PL2": "2nd person plural",
        "PL3": "3rd person plural",
        "SG0": "impersonal (0th person)",
    },
    "NUM": {"SG": "singular", "PL": "plural"},
    "CASE": {
        "NOM": "nominative", "GEN": "genitive", "PAR": "partitive",
        "INE": "inessive (in)", "ELA": "elative (out of)", "ILL": "illative (into)",
        "ADE": "adessive (on)", "ABL": "ablative (from)", "ALL": "allative (onto)",
        "ESS": "essive", "TRA": "translative", "INS": "instructive",
        "ABE": "abessive (without)", "COM": "comitative (together with)", "ACC": "accusative",
    },
}

_SIJAMUOTO_TO_CASE = {
    "nimento": "NOM",
    "omanto": "GEN",
    "osanto": "PAR",
    "sisaolento": "INE",
    "sisaeronto": "ELA",
    "sisatulento": "ILL",
    "ulkoolento": "ADE",
    "ulkoeronto": "ABL",
    "ulkotulento": "ALL",
    "olento": "ESS",
    "tulento": "TRA",
    "keinonto": "INS",
    "vajanto": "ABE",
    "seuranto": "COM",
    "kerrontosti": "ADV",
}


def _extract_lemma(raw: dict) -> str | None:
    """Pull the canonical lemma from FSTOUTPUT [Xp]...[X] when present.

    Voikko's BASEFORM sometimes returns a participle surface (e.g. `tehnyt`)
    instead of the underlying verb (`tehdä`). The Xp tag inside FSTOUTPUT
    always carries the real lemma, so prefer that.
    """
    fst = raw.get("FSTOUTPUT", "")
    m = re.search(r"\[Xp\]([^\[]+)\[X\]", fst)
    if m:
        return m.group(1)
    return raw.get("BASEFORM")


def _normalise(raw: dict) -> dict:
    """Convert a single Voikko analysis dict to our internal reading shape."""
    upos = _CLASS_TO_UPOS.get(raw.get("CLASS", ""), None)
    features: dict[str, str] = {}

    mood = _MOOD_MAP.get(raw.get("MOOD", ""))
    if mood:
        features["MOOD"] = mood

    tense = _TENSE_MAP.get(raw.get("TENSE", ""))
    if tense:
        features["TENSE"] = tense

    person = raw.get("PERSON")
    number = raw.get("NUMBER")
    if person in ("1", "2", "3") and number in ("singular", "plural"):
        features["PERS"] = ("SG" if number == "singular" else "PL") + person
        features["VOICE"] = "ACT"
    elif person == "4":
        features["PERS"] = "SG0"
        features["VOICE"] = "PASS"

    if number == "singular":
        features["NUM"] = "SG"
    elif number == "plural":
        features["NUM"] = "PL"

    case = _SIJAMUOTO_TO_CASE.get(raw.get("SIJAMUOTO", ""))
    if case:
        features["CASE"] = case

    return {
        "word_id": _extract_lemma(raw),
        "upos": upos,
        "features": features,
    }


def _humanise_features(features: dict) -> dict:
    out = {}
    for key, val in features.items():
        label = _FEATURE_LABELS.get(key, {}).get(val, val)
        out[key.lower()] = label
    return out


@app.get("/analyse")
def analyse(word: str):
    word = word.strip()[:64]
    lookup = word.lower()

    raw_results = voikko.analyze(lookup)
    if not raw_results:
        logging.debug("analyse %r → unknown", word)
        return {"word": word, "unknown": True}

    logging.debug("analyse %r → %d analysis(es)", word, len(raw_results))
    for r in raw_results:
        logging.debug("  voikko: %s", r.get("FSTOUTPUT"))

    readings = []
    for raw in raw_results:
        norm = _normalise(raw)
        word_id = norm["word_id"]
        upos = norm["upos"]
        features = norm["features"]

        root = get_verb_root(word_id) if upos in ("VERB", "AUX") and word_id else None
        segments = (
            build_segments(lookup, root, upos, features, lemma=word_id)
            if root else None
        )

        reading: dict = {"word_id": word_id}
        if root:
            reading["root"] = root
        if segments:
            reading["segments"] = segments
        if upos:
            reading["upos"] = upos
        if features:
            reading["features"] = _humanise_features(features)

        readings.append(reading)

        logging.debug("  word_id=%s upos=%s root=%s segments=%s",
                      word_id, upos, root, bool(segments))

    # Dedup on (lemma, upos, features). Voikko sometimes returns duplicate
    # analyses (e.g. `tavata` arrives twice with identical fields).
    seen = set()
    unique = []
    for r in readings:
        sig = (
            r.get("word_id"),
            r.get("upos"),
            tuple(sorted((r.get("features") or {}).items())),
        )
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(r)

    # Chained readings first.
    unique.sort(key=lambda r: 0 if r.get("segments") else 1)

    # Drop shadow readings: a chainless sibling of a chained (lemma, upos)
    # reading is almost always a quirky alt-feature parse — hide it.
    chained_keys = {
        (r.get("word_id"), r.get("upos"))
        for r in unique if r.get("segments")
    }
    unique = [
        r for r in unique
        if r.get("segments") or (r.get("word_id"), r.get("upos")) not in chained_keys
    ]

    return {"word": word, "unknown": False, "readings": unique}


static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
