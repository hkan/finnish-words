import re
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from omorfi import Omorfi, Token
from stem import get_verb_root
from chain import build_segments

omorfi = Omorfi()
ready = False

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s\t%(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ready
    logging.debug("Loading omorfi files")
    omorfi.load_analyser("/app/src/generated/omorfi.describe.hfst")
    logging.debug("Loaded omorfi.describe.hfst")
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
    # Tense
    "PAST": "past tense",
    "PRES": "present tense",
    "PRESENT": "present tense",
    
    # Person
    "SG1": "1st person singular",
    "SG2": "2nd person singular",
    "SG3": "3rd person singular",
    "PL1": "1st person plural",
    "PL2": "2nd person plural",
    "PL3": "3rd person plural",
    "SG0": "impersonal (0th person)",
    
    # Clitics
    "KO": "question particle (-ko)",
    "PA": "mood particle (-pa)",
    "KA": "mood particle (-ka)",
    "KIN": "additive particle (-kin)",
    "KAAN": "negative additive particle (-kaan)",
    "HAN": "discourse particle (-han)",
    "S": "clitic -s",
    
    # Voice
    "ACTV": "active voice",
    "ACT": "active voice",
    "PASV": "passive voice",
    "PASS": "passive voice",
    
    # Mood
    "INDV": "indicative mood",
    "COND": "conditional mood",
    "IMPV": "imperative mood",
    "POTN": "potential mood",
    
    # Infinitive forms
    "INF1": "infinitive I (a-infinitive)",
    "INFA": "infinitive I (a-infinitive)",
    "INF2": "infinitive II (e-infinitive)",
    "INFE": "infinitive II (e-infinitive)",
    "INF3": "infinitive III (ma-infinitive)",
    "INFMA": "infinitive III (ma-infinitive)",
    "MINEN": "4th infinitive / gerund (-minen)",
    
    # Participle forms
    "PCP1": "present participle (-va)",
    "PCP2": "past participle (-nut)",
    "VA": "present participle (-va)",
    "NUT": "past participle (-nut)",
    "AGENT": "agent participle (-ma)",
    "NEG": "negation (-ton)",
    
    # Cases
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
    
    # Number
    "SG": "singular",
    "PL": "plural",
    
    # Comparison
    "POS": "positive degree",
    "CMP": "comparative degree",
    "SUP": "superlative degree",
    
    # Possessives (from analyser)
    "POSSG1": "my (possessive)",
    "POSSG2": "your (possessive)",
    "POSSP3": "his / her / their (possessive)",
    "POSPL1": "our (possessive)",
    "POSPL2": "your plural (possessive)",
    
    # Derivational features (DRV tags)
    # Agent/actor nominals
    "JA": "agent noun suffix (-ja)",
    # Gerunds and deverbal nouns
    "MINEN": "gerund / 4th infinitive (-minen)",
    "MA": "infinitive / gerundial form (-ma)",
    "TU": "passive participle (-tu)",
    "VA": "active participle / infinitive (-va)",
    "TAVA": "infinitive / resultative (-tava)",
    "NUT": "resultative / past participle (-nut)",
    # Deadjectival and other nominals
    "US": "noun-forming suffix (-us/-yys)",
    "UUS": "noun-forming suffix (-uus)",
    # Adjectival
    "INEN": "adjective-forming suffix (-inen)",
    # Adverbial
    "STI": "adverb-forming suffix (-sti)",
    # Causative/desiderative
    "TATTAA": "causative suffix (-tattaa)",
    "TATUTTAA": "passive causative (-tatuttaa)",
    "TTAA": "iterative suffix (-ttaa)",
    # Other derivational
    "MATON": "privative suffix (-maton)",
    "MAISILLA": "adverbial suffix (-maisilla)",
    "MAINEN": "quasi-adjective (-mainen)",
    "TAR": "agent noun suffix (-tar/-tär)",
    "TON": "privative adjective (-ton/-tön)",
    "IN": "adjective suffix (-in)",
    "U": "noun suffix (-u/-y)",
    "KO": "interrogative / nominal suffix (-ko)",
    "ISA": "adjective suffix (-isa)",
    "ISÄ": "adjective suffix (-isä)",
    "LLINEN": "adjective suffix (-llinen)",
    "MÄINEN": "quasi-adjective (-mäinen)",
    "MPI": "comparative suffix (-mpi)",
    "ITTAIN": "adverbial / distributive (-ittain)",
    "NEN": "nominal / attributive suffix (-nen)",
    
    # Lexicalized derivations (LEX tags)
    "LEX_STI": "lexicalized adverb (-sti)",
    
    # Pronoun type
    "PRONTYPE_PRS": "personal pronoun",
    "PRONTYPE_REL": "relative pronoun",
    "PRONTYPE_INT": "interrogative pronoun",
    "PRONTYPE_DEM": "demonstrative pronoun",
    "PRONTYPE_IND": "indefinite pronoun",
    "PRONTYPE_REC": "reciprocal pronoun",
    "PRONTYPE_REFL": "reflexive pronoun",
    
    # Number type
    "NUMTYPE_CARD": "cardinal number",
    "NUMTYPE_ORD": "ordinal number",
    "NUMTYPE_FRAC": "fractional number",
    
    # Adposition type
    "ADPTYPE_PREP": "preposition",
    "ADPTYPE_POST": "postposition",
    
    # Semantic features
    "SEM_TITLE": "occupational or title noun",
    
    # Style
    "STYLE_ARCHAIC": "archaic form",
    "STYLE_DIALECTAL": "dialectal form",
    "STYLE_NONSTANDARD": "non-standard form",
    
    # Boundary and structure
    "BOUNDARY_COMPOUND": "compound boundary",
    "BOUNDARY_CLAUSE": "clause boundary",
    
    # Other
    "SUBCAT_QUANTIFIER": "quantifier",
    "BLACKLIST_TOOSHORTFORCOMPOUND": "too short for compound formation",
}

def parse_analysis(raw: str) -> dict:
    """
    Extract morphological features from a raw Omorfi analyser output.
    
    Example input:
        [WORD_ID=opettaa][UPOS=VERB][DRV=JA][NUM=SG][CASE=NOM][WEIGHT=0.000000]
    
    Returns dict with:
        word_id: str
        upos: str (VERB, NOUN, ADJ, etc.)
        features: dict of extracted features (NUM, CASE, TENSE, etc.)
        derivation_type: str or None (if DRV tag present)
        infinitive_form: str or None (if INF tag present)
        participle_form: str or None (if PCP tag present)
        semantic_class: str or None (if SEM tag present)
        pronoun_type: str or None (if PRONTYPE tag present)
        number_type: str or None (if NUMTYPE tag present)
        adposition_type: str or None (if ADPTYPE tag present)
    """
    # Omorfi occasionally emits a malformed tag like `[HOMONYM=2[UPOS=VERB]`
    # where the HOMONYM tag is missing its closing bracket and the next
    # tag begins inside it. Repair before regex tokenisation so UPOS and
    # subsequent features still parse.
    raw = re.sub(r"\[HOMONYM=(\d+)\[", r"[HOMONYM=\1][", raw)
    tags = re.findall(r"\[([^\]]+)\]", raw)
    
    result = {
        "word_id": None,
        "upos": None,
        "features": {},
        "derivation_type": None,
        "infinitive_form": None,
        "participle_form": None,
        "semantic_class": None,
        "pronoun_type": None,
        "number_type": None,
        "adposition_type": None,
    }
    
    for tag in tags:
        if "=" not in tag:
            continue
            
        key, val = tag.split("=", 1)
        
        if key == "WORD_ID":
            result["word_id"] = val
        elif key == "UPOS":
            result["upos"] = val
        elif key == "DRV":
            result["derivation_type"] = val
        elif key == "LEX":
            result["derivation_type"] = f"{val} (lexicalized)"
        elif key == "INF":
            result["infinitive_form"] = val
        elif key == "PCP":
            result["participle_form"] = val
        elif key == "SEM":
            result["semantic_class"] = val
        elif key == "PRONTYPE":
            result["pronoun_type"] = val
        elif key == "NUMTYPE":
            result["number_type"] = val
        elif key == "ADPTYPE":
            result["adposition_type"] = val
        elif key not in ["WEIGHT"]:
            # Collect all other features
            result["features"][key] = val
    
    return result


def humanize_analysis(parsed: dict) -> dict:
    """
    Convert raw analysis codes to human-readable labels using LABEL_MAP.
    
    Transforms:
    - derivation_type: "JA" → "agent noun suffix (-ja)"
    - infinitive_form: "MINEN" → "gerund / 4th infinitive (-minen)"
    - participle_form: "VA" → "active participle / infinitive (-va)"
    - semantic_class: "TITLE" → "occupational or title noun"
    - features: {"TENSE": "PAST"} → {"tense": "past tense"}
    
    This makes the API response human-readable without changing the structure.
    """
    result = parsed.copy()
    
    # Map single-value features
    if result["derivation_type"]:
        # Handle both raw codes and lexicalized format
        code = result["derivation_type"].split(" ")[0] if " " in result["derivation_type"] else result["derivation_type"]
        if code in LABEL_MAP:
            result["derivation_type"] = LABEL_MAP[code]
    
    if result["infinitive_form"] and result["infinitive_form"] in LABEL_MAP:
        result["infinitive_form"] = LABEL_MAP[result["infinitive_form"]]
    
    if result["participle_form"] and result["participle_form"] in LABEL_MAP:
        result["participle_form"] = LABEL_MAP[result["participle_form"]]
    
    if result["semantic_class"]:
        lookup_key = f"SEM_{result['semantic_class']}"
        if lookup_key in LABEL_MAP:
            result["semantic_class"] = LABEL_MAP[lookup_key]
        elif result["semantic_class"] in LABEL_MAP:
            result["semantic_class"] = LABEL_MAP[result["semantic_class"]]
    
    if result["pronoun_type"]:
        lookup_key = f"PRONTYPE_{result['pronoun_type']}"
        if lookup_key in LABEL_MAP:
            result["pronoun_type"] = LABEL_MAP[lookup_key]
    
    if result["number_type"]:
        lookup_key = f"NUMTYPE_{result['number_type']}"
        if lookup_key in LABEL_MAP:
            result["number_type"] = LABEL_MAP[lookup_key]
    
    if result["adposition_type"]:
        lookup_key = f"ADPTYPE_{result['adposition_type']}"
        if lookup_key in LABEL_MAP:
            result["adposition_type"] = LABEL_MAP[lookup_key]
    
    # Map feature codes to labels
    if result["features"]:
        humanized_features = {}
        for key, val in result["features"].items():
            # Try both key=val and just val
            label_key = f"{key}_{val}" if f"{key}_{val}" in LABEL_MAP else val
            label_val = LABEL_MAP.get(label_key, f"{key}={val}")
            # Use lowercase key with underscores
            feature_name = key.lower()
            humanized_features[feature_name] = label_val
        result["features"] = humanized_features
    
    return result


@app.get("/analyse")
def analyse(word: str):
    word = word.strip()[:64]

    # Omorfi is case-sensitive; analyse the lowercased form so that
    # sentence-initial capitalisation (e.g. "Tiesitkö") doesn't fall through
    # to UNKNOWN. The original `word` is still echoed back for display.
    lookup = word.lower()

    token = Token(lookup)
    omorfi.analyse(token)

    analyses = [
        a for a in token.analyses
        if "[GUESS=UNKNOWN]" not in a.raw
        and "[BLACKLIST=TOOSHORTFORCOMPOUND]" not in a.raw
    ]
    if not analyses:
        logging.debug("analyse %r → unknown", word)
        return {"word": word, "unknown": True}

    logging.debug("analyse %r → %d analysis(es)", word, len(analyses))
    for a in token.analyses:
        logging.debug("  analyser raw: %s", a.raw)

    readings = []
    for analysis in analyses:
        parsed = parse_analysis(analysis.raw)
        raw_features = dict(parsed["features"])
        upos = parsed["upos"]
        lemmas = analysis.get_lemmas()
        word_id = lemmas[0] if lemmas else None

        root = get_verb_root(word_id) if upos in ("VERB", "AUX") and word_id else None
        segments = build_segments(lookup, root, upos, raw_features, lemma=word_id) if root else None

        parsed = humanize_analysis(parsed)

        reading = {"word_id": word_id}
        if root:
            reading["root"] = root
        if segments:
            reading["segments"] = segments
        if upos:
            reading["upos"] = upos
        if parsed["derivation_type"]:
            reading["derivation_type"] = parsed["derivation_type"]
        if parsed["infinitive_form"]:
            reading["infinitive_form"] = parsed["infinitive_form"]
        if parsed["participle_form"]:
            reading["participle_form"] = parsed["participle_form"]
        if parsed["semantic_class"]:
            reading["semantic_class"] = parsed["semantic_class"]
        if parsed["pronoun_type"]:
            reading["pronoun_type"] = parsed["pronoun_type"]
        if parsed["number_type"]:
            reading["number_type"] = parsed["number_type"]
        if parsed["adposition_type"]:
            reading["adposition_type"] = parsed["adposition_type"]
        if parsed["features"]:
            reading["features"] = parsed["features"]

        readings.append(reading)

        logging.debug("  word_id=%s upos=%s root=%s segments=%s",
                      word_id, upos, root, bool(segments))

    # Deduplicate readings: Omorfi can yield the same (lemma, pos, features)
    # via different internal paths. Collapse to unique on a stable signature.
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

    # Sort: readings with a built morpheme chain come first. Stable otherwise.
    unique.sort(key=lambda r: 0 if r.get("segments") else 1)

    # Collapse identical chains across POS. Omorfi emits `olla` as both AUX
    # and VERB; the two readings produce the same `ol + i + n` chain and the
    # user shouldn't see it twice. Key on (word_id, chain surfaces).
    seen_chain = set()
    deduped = []
    for r in unique:
        segs = r.get("segments")
        if segs:
            key = (r.get("word_id"), tuple(s["surface"] for s in segs))
            if key in seen_chain:
                continue
            seen_chain.add(key)
        deduped.append(r)
    unique = deduped

    # Drop shadow readings: if a (word_id, upos) already has a chain reading,
    # hide its chainless siblings (usually Omorfi's quirky alt-feature parses
    # like PERS=SG0 mirroring SG3).
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
