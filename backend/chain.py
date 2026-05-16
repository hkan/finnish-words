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


def build_segments(surface: str, root: str, upos: str, features: dict) -> Optional[list[dict]]:
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

    if not work.startswith(root):
        return None
    tense_surface = work[len(root):]
    if tense_surface:
        segments_rev.append({
            "surface": tense_surface,
            "role": "tense",
            "label": f"past tense marker (-{tense_surface})",
        })

    segments_rev.append({"surface": root, "role": "stem", "label": "root"})

    return list(reversed(segments_rev))
