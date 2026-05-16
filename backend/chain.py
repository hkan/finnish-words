from typing import Optional

# Clitic surface variants (vowel-harmony pairs). Back-harmonic listed first;
# match against the actual word so we pick the surface that's present.
_CLITICS = {
    "KO":   ["kö", "ko"],
    "PA":   ["pä", "pa"],
    "KA":   ["kä", "ka"],
    "KAAN": ["kään", "kaan"],
    "KIN":  ["kin"],
    "HAN":  ["hän", "han"],
    "S":    ["s"],
}

# Person endings in past indicative active.
# SG3 has no separate ending — the bare past stem (root + i / root + si) is the form.
_PERSON_PAST_ACTIVE = {
    "SG1": ["n"],
    "SG2": ["t"],
    "SG3": [""],
    "PL1": ["mme"],
    "PL2": ["tte"],
    "PL3": ["vat", "vät"],
}

_PERSON_LABEL = {
    "SG1": "1st person singular (I)",
    "SG2": "2nd person singular (you)",
    "SG3": "3rd person singular (he/she/it)",
    "PL1": "1st person plural (we)",
    "PL2": "2nd person plural (you)",
    "PL3": "3rd person plural (they)",
}

# Past-tense stem overrides for irregular verbs whose past stem differs from
# the dictionary form's root by more than the regular tense-marker addition.
# These are "safe" cases — a clean vowel swap with no further alternation.
# Keyed by lemma (word_id). Value is the past stem the chain should align on.
_PAST_STEM_OVERRIDES = {
    "syödä": "sö",   # söin, söi, söivät
    "juoda": "jo",   # join, joi
    "tuoda": "to",   # toin, toi
    "viedä": "ve",   # vein, veivät
    "myydä": "my",   # myin, myi
    "lyödä": "lö",   # löin, löi
}

_CLITIC_LABEL = {
    "KO":   "question particle",
    "PA":   "emphatic particle",
    "KA":   "emphatic particle",
    "KAAN": "additive negative particle",
    "KIN":  "additive particle",
    "HAN":  "discourse particle",
    "S":    "emphatic particle",
}


def _pop_from_end(word: str, candidates: list[str]) -> Optional[tuple[str, str]]:
    """
    Return (popped_suffix, remaining) if any candidate matches the end of word,
    else None. Empty-string candidate matches zero-length suffix.
    """
    for cand in candidates:
        if cand == "":
            return "", word
        if word.endswith(cand):
            return cand, word[: -len(cand)]
    return None


def build_segments(surface: str, root: str, upos: str, features: dict,
                   lemma: Optional[str] = None) -> Optional[list[dict]]:
    """
    Build an ordered list of morpheme segments for a surface word.
    Returns None when we can't reliably segment (e.g. unsupported tense/mood).

    Currently supports: past indicative active verb forms, with optional clitic.
    """
    if upos not in ("VERB", "AUX"):
        return None
    if features.get("MOOD") != "INDV":
        return None
    if features.get("TENSE") != "PAST":
        return None
    if features.get("VOICE") != "ACT":
        return None

    segments_rev: list[dict] = []
    work = surface

    # Peel clitics off the end greedily. Omorfi's CLIT feature only reports the
    # outermost one, but Finnish allows stacks like -hän-kö, -pa-s, -kin-kö.
    # We keep popping any known clitic surface until none matches.
    while True:
        matched = None
        for clit_key, variants in _CLITICS.items():
            popped = _pop_from_end(work, variants)
            if popped is not None and popped[0] != "":
                matched = (clit_key, popped)
                break
        if matched is None:
            break
        clit_key, (clit_surface, work) = matched
        segments_rev.append({
            "surface": clit_surface,
            "role": "clitic",
            "label": f"{_CLITIC_LABEL.get(clit_key, 'clitic')} (-{clit_surface})",
        })

    pers = features.get("PERS")
    if pers:
        popped = _pop_from_end(work, _PERSON_PAST_ACTIVE.get(pers, []))
        if popped is None:
            return None
        pers_surface, work = popped
        if pers_surface:
            segments_rev.append({
                "surface": pers_surface,
                "role": "person",
                "label": _PERSON_LABEL.get(pers, pers),
            })

    # Try the irregular past-stem override first (e.g. syödä → sö), then
    # fall back to the regular root. The stem we pick is what appears in
    # the surface; we keep the same "root" label since it's still the
    # lemma's root, just in its past-tense form.
    stem_used = root
    if lemma and lemma in _PAST_STEM_OVERRIDES:
        override = _PAST_STEM_OVERRIDES[lemma]
        if work.startswith(override):
            stem_used = override

    if not work.startswith(stem_used):
        return None
    tense_surface = work[len(stem_used):]
    if tense_surface:
        segments_rev.append({
            "surface": tense_surface,
            "role": "tense",
            "label": f"past tense marker (-{tense_surface})",
        })

    segments_rev.append({"surface": stem_used, "role": "stem", "label": "root"})

    return list(reversed(segments_rev))
