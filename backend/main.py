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
from i18n import t, SUPPORTED_LANGS

voikko = Voikko("fi")

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s\t%(message)s")

_TRANSLATIONS: dict[str, str] = {}
_PAST_TRANSLATIONS: dict[str, str] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _TRANSLATIONS, _PAST_TRANSLATIONS
    
    # Load Finnish → English glosses
    data_file = Path(__file__).parent / "data" / "fi_en.json"
    if data_file.exists():
        import json as _json
        _TRANSLATIONS = _json.loads(data_file.read_text(encoding="utf-8"))
        logging.info("Loaded %d translations", len(_TRANSLATIONS))
    else:
        logging.warning("fi_en.json not found — translations disabled")
    
    # Load Finnish → English past tense phrases
    past_file = Path(__file__).parent / "data" / "fi_en_past.json"
    if past_file.exists():
        _PAST_TRANSLATIONS = _json.loads(past_file.read_text(encoding="utf-8"))
        logging.info("Loaded %d past translations", len(_PAST_TRANSLATIONS))
    else:
        logging.warning("fi_en_past.json not found — past tense translations disabled")
    
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

_FEATURE_KEY_MAP = {
    "TENSE": {"PAST": "feature.tense.PAST", "PRESENT": "feature.tense.PRESENT"},
    "MOOD": {
        "INDV": "feature.mood.INDV", "COND": "feature.mood.COND",
        "IMPV": "feature.mood.IMPV", "POTN": "feature.mood.POTN",
        "INFA": "feature.mood.INFA", "INFE": "feature.mood.INFE",
        "INFMA": "feature.mood.INFMA",
    },
    "VOICE": {"ACT": "feature.voice.ACT", "PASS": "feature.voice.PASS"},
    "PERS": {
        "SG1": "feature.pers.SG1", "SG2": "feature.pers.SG2", "SG3": "feature.pers.SG3",
        "PL1": "feature.pers.PL1", "PL2": "feature.pers.PL2", "PL3": "feature.pers.PL3",
        "SG0": "feature.pers.SG0",
    },
    "NUM": {"SG": "feature.num.SG", "PL": "feature.num.PL"},
    "CASE": {
        "NOM": "feature.case.NOM", "GEN": "feature.case.GEN", "PAR": "feature.case.PAR",
        "INE": "feature.case.INE", "ELA": "feature.case.ELA", "ILL": "feature.case.ILL",
        "ADE": "feature.case.ADE", "ABL": "feature.case.ABL", "ALL": "feature.case.ALL",
        "ESS": "feature.case.ESS", "TRA": "feature.case.TRA", "INS": "feature.case.INS",
        "ABE": "feature.case.ABE", "COM": "feature.case.COM", "ACC": "feature.case.ACC",
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


def _humanise_features(features: dict, lang: str = "en") -> dict:
    out = {}
    for key, val in features.items():
        i18n_key = _FEATURE_KEY_MAP.get(key, {}).get(val)
        out[key.lower()] = t(i18n_key, lang) if i18n_key else val
    return out


@app.get("/analyse")
def analyse(word: str, lang: str = "en"):
    word = word.strip()[:64]
    lookup = word.lower()
    if lang not in SUPPORTED_LANGS:
        lang = "en"

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
            build_segments(lookup, root, upos, features, lemma=word_id, lang=lang,
                         translations=_TRANSLATIONS, past_translations=_PAST_TRANSLATIONS)
            if root else None
        )

        reading: dict = {"word_id": word_id}
        if word_id and word_id in _TRANSLATIONS:
            reading["translation"] = _TRANSLATIONS[word_id]
        if root:
            reading["root"] = root
        if segments:
            reading["segments"] = segments
        if upos:
            reading["upos"] = upos
        if features:
            reading["features"] = _humanise_features(features, lang)

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
