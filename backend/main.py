import re
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from omorfi import Omorfi, Token

omorfi = Omorfi()
ready = False

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s\t%(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ready
    logging.debug("Loading omorfi files")
    omorfi.load_analyser("/app/src/generated/omorfi.describe.hfst")
    logging.debug("Loaded omorfi.describe.hfst")
    omorfi.load_labelsegmenter("/app/src/generated/omorfi.labelsegment.hfst")
    logging.debug("Loaded omorfi.labelsegment.hfst")
    ready = True
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
)


@app.get("/health")
def health():
    return {"ready": ready}

LABEL_MAP = {
    "PAST": "past tense",
    "PRES": "present tense",
    "SG1": "1st person singular",
    "SG2": "2nd person singular",
    "SG3": "3rd person singular",
    "PL1": "1st person plural",
    "PL2": "2nd person plural",
    "PL3": "3rd person plural",
    "KO": "question particle",
    "PA": "question particle",
    "ACTV": "active voice",
    "PASV": "passive voice",
    "INDV": "indicative mood",
    "COND": "conditional mood",
    "IMPV": "imperative mood",
    "POTN": "potential mood",
    "INF1": "infinitive",
    "INF2": "infinitive II",
    "INF3": "infinitive III",
    "NOM": "nominative",
    "GEN": "genitive",
    "ACC": "accusative",
    "PAR": "partitive",
    "INE": "inessive (in)",
    "ELA": "elative (out of)",
    "ILL": "illative (into)",
    "ADE": "adessive (on)",
    "ABL": "ablative (from)",
    "ALL": "allative (onto)",
    "ESS": "essive",
    "TRA": "translative",
    "INS": "instructive",
    "ABE": "abessive (without)",
    "COM": "comitative (together with)",
    "SG": "singular",
    "PL": "plural",
    "PCP1": "present participle",
    "PCP2": "past participle",
    "NEG": "negation",
    "POSSG1": "my (possessive)",
    "POSSG2": "your (possessive)",
    "POSSP3": "his / her / their (possessive)",
    "POSPL1": "our (possessive)",
    "POSPL2": "your plural (possessive)",
    "KIN": "also / even",
    "KAAN": "either / not even",
}

UPOS_LABELS = {"VERB", "NOUN", "ADJ", "ADV", "NUM", "PRON", "PROPN", "ADP",
               "CCONJ", "SCONJ", "INTJ", "PUNCT", "SYM", "X"}

def parse_labelsegment(raw: str) -> list[dict]:
    parts = re.split(r"(\{[^}]+\}|\[[^\]]+\])", raw)
    segments = []
    current_surface = ""
    current_labels = []
    is_stub = False

    for part in parts:
        if part.startswith("{"):
            tag = part[1:-1]
            if tag == "STUB":
                segments.append({"surface": current_surface, "labels": current_labels, "stub": True})
                current_surface = ""
                current_labels = []
            elif tag == "MB":
                segments.append({"surface": current_surface, "labels": current_labels, "stub": is_stub})
                current_surface = ""
                current_labels = []
                is_stub = False
        elif part.startswith("["):
            label = part[1:-1]
            if label not in UPOS_LABELS:
                current_labels.append(label)
        else:
            current_surface += part

    if current_surface or current_labels:
        segments.append({"surface": current_surface, "labels": current_labels, "stub": is_stub})

    result = [
        {
            "surface": seg["surface"],
            "roles": ["stem"] if seg["stub"] else [LABEL_MAP.get(l, l) for l in seg["labels"]],
        }
        for seg in segments
        if seg["surface"]
    ]

    for seg in result:
        raw_labels = [r for r in seg["roles"] if r not in LABEL_MAP.values() and r != "stem"]
        if raw_labels:
            logging.warning("unmapped label(s) in output: %s (surface=%r)", raw_labels, seg["surface"])

    return result


@app.get("/analyse")
def analyse(word: str):
    word = word.strip()[:64]

    token = Token(word)
    omorfi.analyse(token)

    analyses = [a for a in token.analyses if "[GUESS=UNKNOWN]" not in a.raw]
    if not analyses:
        logging.debug("analyse %r → unknown", word)
        return {"word": word, "unknown": True}

    seg_token = Token(word)
    omorfi.labelsegment(seg_token)

    logging.debug("analyse %r → %d analysis(es), %d segmentation(s)",
                  word, len(analyses), len(seg_token.labelsegmentations))
    for a in token.analyses:
        logging.debug("  analyser raw: %s", a.raw)
    for s in seg_token.labelsegmentations:
        logging.debug("  segmenter raw: %s", s.raw)

    morphemes = []
    if seg_token.labelsegmentations:
        morphemes = parse_labelsegment(seg_token.labelsegmentations[0].raw)

    readings = []
    for analysis in analyses:
        lemmas = analysis.get_lemmas()
        readings.append({
            "word_id": lemmas[0] if lemmas else None,
            "morphemes": morphemes,
        })

    return {"word": word, "unknown": False, "readings": readings}


static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
