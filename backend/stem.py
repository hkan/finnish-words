import re
import libvoikko

_voikko = libvoikko.Voikko("fi")

# Exceptions for verbs whose root cannot be derived by rule.
# The -sta/-stä infinitive class has non-uniform stem alternations,
# so each verb needs its own entry.
# Sources: VISK §§72-73; Wiktionary Finnish conjugation tables.
_VERB_EXCEPTIONS: dict[str, str] = {
    "juosta": "juoks",  # juoksen, juoksin
    "nousta": "nous",   # nousen, nousin
}


def _voikko_stem(lemma: str) -> str | None:
    results = _voikko.analyze(lemma)
    if not results:
        return None
    for r in results:
        if "infinitive" in r.get("MOOD", ""):
            m = re.search(r"\[X\]([^[]+)", r["FSTOUTPUT"])
            if m:
                return m.group(1)
    m = re.search(r"\[X\]([^[]+)", results[0]["FSTOUTPUT"])
    return m.group(1) if m else None


def get_verb_root(lemma: str) -> str | None:
    """
    Return the morphological root of a Finnish verb lemma.

    Rules applied in order:
    1. Exceptions table — for -sta/-stä verbs (juosta, nousta) whose stem
       alternation (t→ks, t→s) is not derivable from a general rule.
    2. Voikko FST stem — the part between [X] and the first tag in FSTOUTPUT,
       extracted from the infinitive analysis (libvoikko, backed by Kotus).
    3. -da/-dä rule — strip trailing 'd': the d belongs to the infinitive suffix,
       not the root (tehdä→teh, juoda→juo, syödä→syö, ...).
       Grounded in VISK §72.
    4. Degemination — strip one consonant from a trailing geminate (nn, ll, rr):
       type-3 verbs use strong grade in the infinitive but weak grade in
       conjugation (mennä→men, tulla→tul, purra→pur, olla→ol).
       Grounded in VISK §43-44.

    Returns None if the root cannot be determined.
    """
    if lemma in _VERB_EXCEPTIONS:
        return _VERB_EXCEPTIONS[lemma]

    stem = _voikko_stem(lemma)
    if not stem:
        return None

    if (lemma.endswith("da") or lemma.endswith("dä")) and stem.endswith("d"):
        stem = stem[:-1]
    else:
        for geminate in ("nn", "ll", "rr"):
            if stem.endswith(geminate):
                stem = stem[:-1]
                break

    return stem or None
