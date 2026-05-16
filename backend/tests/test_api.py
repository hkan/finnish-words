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
]

GRADATION = [
    ("kirjoitin",   "kirjoittaa", "kirjoit + i + n"),
    ("kirjoititte", "kirjoittaa", "kirjoit + i + tte"),
    ("opetin",      "opettaa",    "opet + i + n"),
    ("aloitin",     "aloittaa",   "aloit + i + n"),
    ("odotin",      "odottaa",    "odot + i + n"),
    ("lopetin",     "lopettaa",   "lopet + i + n"),
    ("opin",        "oppia",      "op + i + n"),
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
    # Out of scope: present, infinitive, participle
    "tiedän", "menen", "syömään", "tekevä", "luettu", "tietää",
    # Nouns
    "talossa", "talolla", "kirja",
]


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
