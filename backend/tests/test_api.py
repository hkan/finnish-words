"""
End-to-end tests for /analyse.

Each test parameterises over (input, expected_chain) — a string like
"tie + si + t + kö" that we compare against the joined surfaces of the
first reading that has a built morpheme chain.

Add new cases by editing the lists below. To temporarily ignore a case
(known limitation, future work), prefix the input with a `#` comment in
the expected string or drop it from the list.
"""
import pytest


def _first_chain(payload):
    """Return the chain string ('a + b + c') of the first chained reading,
    or None if no reading has segments."""
    for r in payload.get("readings", []):
        if r.get("segments"):
            return " + ".join(s["surface"] for s in r["segments"])
    return None


def _first_lemma(payload):
    for r in payload.get("readings", []):
        if r.get("segments"):
            return r.get("word_id")
    return None


# --- Chain cases: (input, expected_lemma, expected_chain) ---------------

CORE_TARGET = [
    ("tiesitkö",  "tietää", "tie + si + t + kö"),
    ("tiesin",    "tietää", "tie + si + n"),
    ("tiesit",    "tietää", "tie + si + t"),
    ("tiesi",     "tietää", "tie + si"),
    ("tiesimme",  "tietää", "tie + si + mme"),
    ("tiesitte",  "tietää", "tie + si + tte"),
    ("tiesivät",  "tietää", "tie + si + vät"),
]

REGULAR_PAST = [
    ("menin",    "mennä",  "men + i + n"),
    ("tulivat",  "tulla",  "tul + i + vat"),
    ("purin",    "purra",  "pur + i + n"),
    ("juoksin",  "juosta", "juoks + i + n"),
    ("nousin",   "nousta", "nous + i + n"),
    ("sanoin",   "sanoa",  "sano + i + n"),
    ("puhuin",   "puhua",  "puhu + i + n"),
]

STACKED_CLITICS = [
    ("menithänkö",     "mennä",     "men + i + t + hän + kö"),
    ("tiesikinkö",     "tietää",    "tie + si + kin + kö"),
    ("tiesitkös",      "tietää",    "tie + si + t + kö + s"),
    ("menipäs",        "mennä",     "men + i + pä + s"),
    ("kirjoitinkohan", "kirjoittaa","kirjoit + i + n + ko + han"),
]

CAPITALISATION = [
    ("Tiesitkö",   "tietää",     "tie + si + t + kö"),
    ("TIESITKÖ",   "tietää",     "tie + si + t + kö"),
    ("Menithänkö", "mennä",      "men + i + t + hän + kö"),
    ("Söin",       "syödä",      "sö + i + n"),
    ("Kirjoitin",  "kirjoittaa", "kirjoit + i + n"),
    ("Annoin",     "antaa",      "ann + oi + n"),
]

# `olla` is AUX in some readings, VERB in others. We don't pin the lemma's
# upos, just that *some* reading produces this chain.
AUX_OLLA = [
    ("olin",     "olla", "ol + i + n"),
    ("olit",     "olla", "ol + i + t"),
    ("oli",      "olla", "ol + i"),
    ("olimme",   "olla", "ol + i + mme"),
    ("olivat",   "olla", "ol + i + vat"),
    ("olikaan",  "olla", "ol + i + kaan"),
    ("olihan",   "olla", "ol + i + han"),
    ("olikohan", "olla", "ol + i + ko + han"),
]

IRREGULAR_SAFE_6 = [
    ("söin",   "syödä", "sö + i + n"),
    ("söi",    "syödä", "sö + i"),
    ("söivät", "syödä", "sö + i + vät"),
    ("join",   "juoda", "jo + i + n"),
    ("joi",    "juoda", "jo + i"),
    ("toin",   "tuoda", "to + i + n"),
    ("vein",   "viedä", "ve + i + n"),
    ("myin",   "myydä", "my + i + n"),
    ("löin",   "lyödä", "lö + i + n"),
    ("kävin",  "käydä", "käv + i + n"),
    ("kävi",   "käydä", "käv + i"),
    ("kävimme","käydä", "käv + i + mme"),
]

# Fully irregular present-tense forms emitted as a single opaque chunk.
PRESENT_IRREGULAR_FORMS = [
    ("on",       "olla", "on"),
    ("ovat",     "olla", "ovat"),
    ("onko",     "olla", "on + ko"),
    ("onkohan",  "olla", "on + ko + han"),
    ("ovatko",   "olla", "ovat + ko"),
]

PRESENT_TENSE = [
    # TYPE-3 (-lla/-nna/-rra/-sta): root + e + person
    ("olen",     "olla",   "ol + e + n"),
    ("olet",     "olla",   "ol + e + t"),
    ("olemme",   "olla",   "ol + e + mme"),
    ("olette",   "olla",   "ol + e + tte"),
    ("menen",    "mennä",  "men + e + n"),
    ("menet",    "mennä",  "men + e + t"),
    ("menee",    "mennä",  "men + e + e"),
    ("menemme",  "mennä",  "men + e + mme"),
    ("menette",  "mennä",  "men + e + tte"),
    ("menevät",  "mennä",  "men + e + vät"),
    ("tulen",    "tulla",  "tul + e + n"),
    ("tulemme",  "tulla",  "tul + e + mme"),
    ("tulevat",  "tulla",  "tul + e + vat"),
    ("puren",    "purra",  "pur + e + n"),
    ("juoksen",  "juosta", "juoks + e + n"),
    ("juoksee",  "juosta", "juoks + e + e"),
    ("nousen",   "nousta", "nous + e + n"),
    # TYPE-2 (-da/-dä after long vowel): root + person
    ("syön",     "syödä",  "syö + n"),
    ("syöt",     "syödä",  "syö + t"),
    ("syömme",   "syödä",  "syö + mme"),
    ("syövät",   "syödä",  "syö + vät"),
    ("juon",     "juoda",  "juo + n"),
    # TYPE-1 (-Va/-Vä, no gradation): root + person
    ("puhun",    "puhua",  "puhu + n"),
    ("puhut",    "puhua",  "puhu + t"),
    ("puhuu",    "puhua",  "puhu + u"),
    ("puhumme",  "puhua",  "puhu + mme"),
    ("puhutte",  "puhua",  "puhu + tte"),
    ("puhuvat",  "puhua",  "puhu + vat"),
    ("sanon",    "sanoa",  "sano + n"),
    ("sanoo",    "sanoa",  "sano + o"),
    ("sanomme",  "sanoa",  "sano + mme"),
    # Clitics on present tense
    ("olenko",   "olla",   "ol + e + n + ko"),
    ("menetkö",  "mennä",  "men + e + t + kö"),
    ("syönkö",   "syödä",  "syö + n + kö"),
]

# Type-1 present-tense gradation: SG1/SG2/PL1/PL2 use weak grade,
# SG3/PL3 use strong grade.
PRESENT_GRADATION = [
    # rt → rr (ymmärtää)
    ("ymmärrän",   "ymmärtää",   "ymmärrä + n"),
    ("ymmärrät",   "ymmärtää",   "ymmärrä + t"),
    ("ymmärtää",   "ymmärtää",   "ymmärtä + ä"),
    ("ymmärrämme", "ymmärtää",   "ymmärrä + mme"),
    ("ymmärrätte", "ymmärtää",   "ymmärrä + tte"),
    ("ymmärtävät", "ymmärtää",   "ymmärtä + vät"),
    # t → d (tietää)
    ("tiedän",     "tietää",     "tiedä + n"),
    ("tiedät",     "tietää",     "tiedä + t"),
    ("tietää",     "tietää",     "tietä + ä"),
    ("tiedämme",   "tietää",     "tiedä + mme"),
    ("tietävät",   "tietää",     "tietä + vät"),
    # nt → nn (antaa)
    ("annan",      "antaa",      "anna + n"),
    ("annat",      "antaa",      "anna + t"),
    ("antaa",      "antaa",      "anta + a"),
    ("annamme",    "antaa",      "anna + mme"),
    ("antavat",    "antaa",      "anta + vat"),
    # tt → t (kirjoittaa)
    ("kirjoitan",   "kirjoittaa", "kirjoita + n"),
    ("kirjoitat",   "kirjoittaa", "kirjoita + t"),
    ("kirjoittaa",  "kirjoittaa", "kirjoitta + a"),
    ("kirjoittavat","kirjoittaa", "kirjoitta + vat"),
    # pp → p (oppia). "opin" handled separately (ambiguous past/present).
    ("oppii",      "oppia",      "oppi + i"),
    # k → ∅ (lukea)
    ("luen",       "lukea",      "lue + n"),
    ("lukee",      "lukea",      "luke + e"),
    # No gradation (sanity): puhua, sanoa still work via fallback to strong
    ("puhun",      "puhua",      "puhu + n"),
    ("sanon",      "sanoa",      "sano + n"),
]

GRADATION = [
    ("kirjoitin",   "kirjoittaa", "kirjoit + i + n"),
    ("kirjoititte", "kirjoittaa", "kirjoit + i + tte"),
    ("opetin",      "opettaa",    "opet + i + n"),
    ("aloitin",     "aloittaa",   "aloit + i + n"),
    ("odotin",      "odottaa",    "odot + i + n"),
    ("lopetin",     "lopettaa",   "lopet + i + n"),
    # "opin" is ambiguous (oppia present 1sg AND past 1sg). See
    # test_opin_has_both_readings for explicit two-chain coverage.
    ("annoin",      "antaa",      "ann + oi + n"),
    ("antoi",       "antaa",      "ant + oi"),
    ("kannoin",     "kantaa",     "kann + oi + n"),
    ("ymmärsin",    "ymmärtää",   "ymmär + si + n"),
    ("alkoi",       "alkaa",      "alk + oi"),
]


ALL_CHAIN_CASES = (
    CORE_TARGET
    + REGULAR_PAST
    + STACKED_CLITICS
    + CAPITALISATION
    + AUX_OLLA
    + IRREGULAR_SAFE_6
    + GRADATION
    + PRESENT_TENSE
    + PRESENT_GRADATION
    + PRESENT_IRREGULAR_FORMS
)


@pytest.mark.parametrize("word, expected_lemma, expected_chain", ALL_CHAIN_CASES)
def test_chain(client, word, expected_lemma, expected_chain):
    r = client.get("/analyse", params={"word": word})
    assert r.status_code == 200
    payload = r.json()
    assert not payload.get("unknown"), f"{word!r} returned UNKNOWN"
    assert _first_chain(payload) == expected_chain, (
        f"{word!r}: got {_first_chain(payload)!r}, expected {expected_chain!r}"
    )
    assert _first_lemma(payload) == expected_lemma, (
        f"{word!r}: lemma {_first_lemma(payload)!r}, expected {expected_lemma!r}"
    )


# --- Cases that should fall back (chain not built) ----------------------

FALLBACK = [
    # Tricky irregulars we haven't tabled yet
    "näin", "tein",
    # Present tense forms we don't support yet:
    # - tehdä / nähdä irregular present stems
    "teen", "näen",
    # Out of scope: infinitive (non-coinciding), participle, ma-infinitive
    "syömään", "tekevä", "luettu",
    # Nouns
    "talossa", "talolla", "kirja",
]


def test_olla_present_not_duplicated(client):
    """olla is tagged as both AUX and VERB by Omorfi; the chain reading
    should appear once, not twice."""
    r = client.get("/analyse", params={"word": "olen"})
    payload = r.json()
    chains = [
        " + ".join(s["surface"] for s in reading["segments"])
        for reading in payload.get("readings", [])
        if reading.get("segments")
    ]
    assert chains == ["ol + e + n"], f"expected single chain, got {chains}"


def test_opin_has_both_readings(client):
    """`opin` is genuinely ambiguous: oppia present 1sg (`opi + n`) AND
    past 1sg (`op + i + n`). Both chains should be produced."""
    r = client.get("/analyse", params={"word": "opin"})
    payload = r.json()
    chains = {
        " + ".join(s["surface"] for s in reading["segments"])
        for reading in payload.get("readings", [])
        if reading.get("segments")
    }
    assert "opi + n" in chains, f"missing present chain in {chains}"
    assert "op + i + n" in chains, f"missing past chain in {chains}"


def test_olla_past_not_duplicated(client):
    r = client.get("/analyse", params={"word": "olin"})
    payload = r.json()
    chains = [
        " + ".join(s["surface"] for s in reading["segments"])
        for reading in payload.get("readings", [])
        if reading.get("segments")
    ]
    assert chains == ["ol + i + n"], f"expected single chain, got {chains}"


@pytest.mark.parametrize("word", FALLBACK)
def test_no_chain_built(client, word):
    r = client.get("/analyse", params={"word": word})
    assert r.status_code == 200
    payload = r.json()
    assert not payload.get("unknown"), f"{word!r} unexpectedly UNKNOWN"
    assert _first_chain(payload) is None, (
        f"{word!r}: unexpected chain {_first_chain(payload)!r}"
    )


# --- Unknown / edge cases -----------------------------------------------

UNKNOWN = ["", "  ", "xyzabc", "tiesitkö!", "###"]


@pytest.mark.parametrize("word", UNKNOWN)
def test_unknown(client, word):
    r = client.get("/analyse", params={"word": word})
    assert r.status_code == 200
    payload = r.json()
    assert payload.get("unknown") is True, (
        f"{word!r}: expected UNKNOWN, got {payload}"
    )
