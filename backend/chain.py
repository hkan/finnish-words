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
    "käydä": "käv",  # kävin, kävi (irregular v-stem)
    "saada": "sa",   # sain, sai, saimme (vowel-shortened past stem)
}

# Verbs with strong/weak stem alternation in both present and past tense.
# Weak stem appears with SG1/SG2/PL1/PL2 (1st/2nd-person endings),
# strong stem with SG3/PL3 (3rd-person endings). Behaves type-3-like in
# present tense (uses the `e` tense marker) despite the -dä infinitive.
#   tehdä  present: te+e+n  / tek+ee   past: te+i+n  / tek+i
#   nähdä  present: nä+e+n  / näk+ee   past: nä+i+n  / näk+i
_ALT_STEMS = {
    "tehdä": {"weak": "te", "strong": "tek"},
    "nähdä": {"weak": "nä", "strong": "näk"},
}


def _alt_stem(lemma: str, pers: str) -> Optional[str]:
    entry = _ALT_STEMS.get(lemma)
    if entry is None:
        return None
    return entry["strong"] if pers in ("SG3", "PL3") else entry["weak"]

# Consonant gradation patterns applied at the END of a stem when forming the
# past tense. Many type-1 verbs (e.g. -ttaa, -taa) close their syllable in
# past tense forms, triggering weak-grade alternation. We try the strong-grade
# root first and only fall back to gradated candidates when it fails to align.
_GRADATION = [
    ("tt", "t"),    # kirjoitta- → kirjoit-  (kirjoitin)
    ("kk", "k"),    # leikka-    → leika-    (leikin)
    ("pp", "p"),    # oppi-      → opi-      (opin)
    ("nt", "nn"),   # anta-      → ann-      (annoin)
    ("mp", "mm"),
    ("lt", "ll"),
    ("rt", "rr"),
    ("nk", "ng"),
]

_VOWELS = "aeiouyäö"

# Inflection class detection from infinitive ending. Drives the present-tense
# stem shape.
#   TYPE-3 (-lla/-nna/-rra/-sta): present tense inserts an `e` between the
#     (weak-grade) root and the person ending, e.g. men + e + n → menen.
#   TYPE-2 (-da/-dä after a long vowel/diphthong): present uses the bare root
#     plus person ending, e.g. syö + n → syön.
#   TYPE-1 (-Va/-Vä, default): present uses the bare root + person ending,
#     e.g. puhu + n → puhun.
# Gradation alternation in type-1 (tietää → tiedän, antaa → annan) is not yet
# supported — those forms fall back to no-chain.
_TYPE3_ENDINGS = ("lla", "llä", "nna", "nnä", "rra", "rrä", "sta", "stä")

# Type-4 (-Vta/-Vtä): pelata, haluta, hypätä, siivota, tavata, kerätä, levätä.
# Lemma is weak grade, present and past stems are strong grade. Past uses
# the `si` tense marker; present marker is the harmony vowel a/ä (lengthens
# the stem's final vowel; doubles as SG3 person marker).
_TYPE4_ENDINGS = (
    "ata", "ota", "uta", "ita", "eta",
    "ätä", "ötä", "ytä", "itä", "etä",
)


def _inflection_class(lemma: str) -> str:
    if lemma.endswith(_TYPE3_ENDINGS):
        return "TYPE3"
    if lemma.endswith(_TYPE4_ENDINGS):
        return "TYPE4"
    if lemma.endswith(("da", "dä")):
        return "TYPE2"
    return "TYPE1"


def _type4_strong(weak: str) -> str:
    """Reverse-gradate a type-4 weak stem to derive its strong-grade form.
    Type-4 infinitives are weak; both present and past stems use strong.
    Handles single-consonant doubling (p/t/k → pp/tt/kk) and softening
    reversals (v→p, d→t) between vowels. Returns the weak stem unchanged
    when no rule applies (no-gradation verbs like pelata, kerätä)."""
    if len(weak) < 3:
        return weak
    last_v = weak[-1]
    body = weak[:-1]
    last = body[-1]
    prev = body[-2] if len(body) >= 2 else ""
    if last in "ptk" and prev in _VOWELS:
        return body + last + last_v
    if last == "v" and prev in _VOWELS:
        return body[:-1] + "p" + last_v
    if last == "d" and prev in _VOWELS:
        return body[:-1] + "t" + last_v
    return weak


def _type4_stems(lemma: str) -> Optional[tuple[list[str], str]]:
    """Return (stem_candidates, harmony_vowel) for a type-4 verb.

    Candidates are tried in order — weak (no-gradation) first since most
    type-4 verbs don't gradate (pelata, siivota, kerätä, haluta). Strong
    is appended when the reverse-gradation rule produces a different
    string, covering hypätä (p→pp), tavata (v→p), etc. The over-eager
    rule occasionally produces a wrong strong candidate (siipo from
    siivo) but it just sits unused — the weak candidate matches first.

    Harmony is `ä` if the stem contains any front vowel, else `a`.
    """
    if len(lemma) < 3:
        return None
    weak = lemma[:-2]
    if not weak:
        return None
    harmony = "ä" if any(c in "äöy" for c in weak) else "a"
    strong = _type4_strong(weak)
    candidates = [weak]
    if strong != weak:
        candidates.append(strong)
    return candidates, harmony


_PERSON_PRES_ACTIVE = {
    "SG1": ["n"],
    "SG2": ["t"],
    "SG3": [""],   # handled specially per inflection class (vowel lengthening)
    "PL1": ["mme"],
    "PL2": ["tte"],
    "PL3": ["vat", "vät"],
}


# Lemmas whose present-tense forms are fully irregular for some person.
# These are not segmentable; we emit them as a single opaque stem chunk
# labelled as an irregular form. The map is (lemma, pers) → surface.
_PRESENT_FULL_FORMS = {
    ("olla", "SG3"): "on",
    ("olla", "PL3"): "ovat",
}


# Type-1 present-tense gradation: cluster rules (longer match wins) then
# single-consonant softenings (only between vowels). Used to derive the
# weak-grade present stem (SG1/SG2/PL1/PL2) from the strong-grade stem.
_PRESENT_CLUSTER_GRADATION = [
    ("tt", "t"),
    ("kk", "k"),
    ("pp", "p"),
    ("nt", "nn"),
    ("mp", "mm"),
    ("lt", "ll"),
    ("rt", "rr"),
    ("nk", "ng"),
]
_PRESENT_SINGLE_GRADATION = {"t": "d", "p": "v", "k": ""}


def _weak_grade(strong: str) -> Optional[str]:
    """
    Given a strong-grade present stem (e.g. 'ymmärtä'), return the weak
    counterpart (e.g. 'ymmärrä'). Returns None if no rule matches — for
    no-gradation verbs like puhua/sanoa, the strong stem is also used in
    weak-grade person forms.
    """
    if len(strong) < 2 or strong[-1] not in _VOWELS:
        return None
    final_v = strong[-1]
    body = strong[:-1]
    for s, w in _PRESENT_CLUSTER_GRADATION:
        if body.endswith(s):
            return body[: -len(s)] + w + final_v
    # Single-consonant rule: requires a vowel before the gradating consonant.
    if len(body) >= 2 and body[-2] in _VOWELS:
        c = body[-1]
        if c in _PRESENT_SINGLE_GRADATION:
            return body[:-1] + _PRESENT_SINGLE_GRADATION[c] + final_v
    return None


def _past_stem_candidates(root: str) -> list[str]:
    """
    Yield plausible past-tense stems for a given root.

    Ordered most-conservative first: the root unchanged, then with its
    final vowel dropped, then with end-cluster gradation applied. The
    chain builder takes the first candidate whose prefix appears in the
    surface form, so regular roots ("sano", "men", "tul") always win
    over their alternatives.
    """
    candidates = [root]
    if len(root) > 1 and root[-1] in _VOWELS:
        without_v = root[:-1]
        candidates.append(without_v)
        for strong, weak in _GRADATION:
            if without_v.endswith(strong):
                candidates.append(without_v[: -len(strong)] + weak)
    return candidates

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
    if features.get("VOICE") != "ACT":
        return None
    tense = features.get("TENSE")
    if tense not in ("PAST", "PRES", "PRESENT"):
        return None

    segments_rev: list[dict] = []
    work = surface

    # Peel clitics off the end greedily. Finnish allows stacks like -hän-kö,
    # -pa-s, -kin-kö. We keep popping any known clitic surface until none matches.
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

    if tense == "PAST":
        return _build_past(work, root, features, lemma, segments_rev)
    if tense in ("PRES", "PRESENT"):
        return _build_present(work, root, features, lemma, segments_rev)
    return None


def _build_past(work, root, features, lemma, segments_rev):
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

    # Pick the stem that actually appears in the surface. Priority:
    # 1. Irregular past-stem override (e.g. syödä → sö)
    # 2. The root unchanged (regular verbs)
    # 3. Gradation candidates (drop final vowel + weak-grade cluster) for
    #    type-1 verbs like kirjoitta → kirjoit, anta → ann.
    stem_used = None
    if lemma and pers:
        alt = _alt_stem(lemma, pers)
        if alt is not None and work.startswith(alt):
            stem_used = alt
    if stem_used is None and lemma and lemma in _PAST_STEM_OVERRIDES:
        override = _PAST_STEM_OVERRIDES[lemma]
        if work.startswith(override):
            stem_used = override
    # Type-4 past stem (strong, derived from lemma) takes priority over the
    # voikko-root-based candidates since voikko returns the consonant stem
    # (`pelat`, `hypät`) for these verbs.
    if stem_used is None and lemma and _inflection_class(lemma) == "TYPE4":
        result = _type4_stems(lemma)
        if result:
            candidates, _ = result
            for cand in candidates:
                if work.startswith(cand):
                    stem_used = cand
                    break
    if stem_used is None:
        for cand in _past_stem_candidates(root):
            if work.startswith(cand):
                stem_used = cand
                break
    if stem_used is None:
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


def _build_present(work, root, features, lemma, segments_rev):
    """
    Present indicative active. After clitics are already peeled, `work` is
    the bare verb form.

    Stem shapes by inflection class:
        TYPE-1 (-Va, -aa/-ää, ...): present stem is lemma[:-1] (strong grade).
            Gradation alternation: SG1/SG2/PL1/PL2 use the weak-grade
            counterpart (ymmärrä), SG3/PL3 use strong (ymmärtä). SG3 marker
            is final-vowel lengthening.
        TYPE-2 (-da/-dä): bare root + person ending. SG3 coincides with root.
        TYPE-3 (-lla/-nna/-rra/-sta): root + 'e' + person ending.
            SG3 marker is the lengthening of the inserted e (men + e + e).

    Irregular forms in `_PRESENT_IRREGULAR` (olla SG3/PL3) and unsupported
    cases (tehdä, nähdä) return None.
    """
    if not lemma:
        return None
    pers = features.get("PERS")
    if not pers:
        return None
    full = _PRESENT_FULL_FORMS.get((lemma, pers))
    if full is not None:
        if work != full:
            return None
        segments_rev.append({
            "surface": full, "role": "stem",
            "label": f"irregular present-tense form of {lemma}",
        })
        return list(reversed(segments_rev))

    if lemma in _ALT_STEMS:
        return _present_alt(work, lemma, pers, segments_rev)

    klass = _inflection_class(lemma)

    if klass == "TYPE1":
        return _present_type1(work, lemma, pers, segments_rev)
    if klass == "TYPE2":
        return _present_type2(work, root, pers, segments_rev)
    if klass == "TYPE4":
        return _present_type4(work, lemma, pers, segments_rev)
    return _present_type3(work, root, pers, segments_rev)


def _present_type1(work, lemma, pers, segments_rev):
    if len(lemma) < 2:
        return None
    strong = lemma[:-1]
    if not strong or strong[-1] not in _VOWELS:
        return None
    weak = _weak_grade(strong)

    if pers == "SG3":
        # Strong stem + final-vowel lengthening: puhu → puhuu, tietä → tietää.
        if work != strong + strong[-1]:
            return None
        segments_rev.append({
            "surface": strong[-1], "role": "person",
            "label": _PERSON_LABEL["SG3"],
        })
        segments_rev.append({"surface": strong, "role": "stem", "label": "root"})
        return list(reversed(segments_rev))

    popped = _pop_from_end(work, _PERSON_PRES_ACTIVE.get(pers, []))
    if popped is None:
        return None
    pers_surface, work = popped
    if not pers_surface:
        return None
    segments_rev.append({
        "surface": pers_surface, "role": "person",
        "label": _PERSON_LABEL.get(pers, pers),
    })

    # PL3 stays strong (tietävät, antavat). Other persons prefer weak grade,
    # falling back to strong for verbs without gradation.
    if pers == "PL3":
        candidates = [strong]
    else:
        candidates = []
        if weak:
            candidates.append(weak)
        candidates.append(strong)

    for cand in candidates:
        if cand and work == cand:
            segments_rev.append({"surface": cand, "role": "stem", "label": "root"})
            return list(reversed(segments_rev))
    return None


def _present_type2(work, root, pers, segments_rev):
    if pers == "SG3":
        if work != root:
            return None
        segments_rev.append({"surface": root, "role": "stem", "label": "root"})
        return list(reversed(segments_rev))

    popped = _pop_from_end(work, _PERSON_PRES_ACTIVE.get(pers, []))
    if popped is None:
        return None
    pers_surface, work = popped
    if not pers_surface or work != root:
        return None
    segments_rev.append({
        "surface": pers_surface, "role": "person",
        "label": _PERSON_LABEL.get(pers, pers),
    })
    segments_rev.append({"surface": root, "role": "stem", "label": "root"})
    return list(reversed(segments_rev))


def _present_alt(work, lemma, pers, segments_rev):
    """
    Present tense for tehdä/nähdä-style verbs: type-3-like mechanics with
    explicit weak/strong stem alternation per person.
    """
    stem = _alt_stem(lemma, pers)
    if stem is None:
        return None

    if pers == "SG3":
        if work != stem + "ee":
            return None
        segments_rev.append({
            "surface": "e", "role": "person",
            "label": _PERSON_LABEL["SG3"],
        })
        segments_rev.append({
            "surface": "e", "role": "tense",
            "label": "present tense marker (-e)",
        })
        segments_rev.append({"surface": stem, "role": "stem", "label": "root"})
        return list(reversed(segments_rev))

    popped = _pop_from_end(work, _PERSON_PRES_ACTIVE.get(pers, []))
    if popped is None:
        return None
    pers_surface, work = popped
    if not pers_surface or work != stem + "e":
        return None
    segments_rev.append({
        "surface": pers_surface, "role": "person",
        "label": _PERSON_LABEL.get(pers, pers),
    })
    segments_rev.append({
        "surface": "e", "role": "tense",
        "label": "present tense marker (-e)",
    })
    segments_rev.append({"surface": stem, "role": "stem", "label": "root"})
    return list(reversed(segments_rev))


def _present_type4(work, lemma, pers, segments_rev):
    """
    Type-4 present: strong stem + harmony vowel (lengthening) + person.
    pelata → pela + a + n → pelaan. SG3: pela + a → pelaa (the harmony
    vowel doubles as the person marker, same shape as TYPE-1 SG3).
    """
    result = _type4_stems(lemma)
    if result is None:
        return None
    candidates, harmony = result

    if pers == "SG3":
        for stem in candidates:
            if work == stem + harmony:
                segments_rev.append({
                    "surface": harmony, "role": "person",
                    "label": _PERSON_LABEL["SG3"],
                })
                segments_rev.append({"surface": stem, "role": "stem", "label": "root"})
                return list(reversed(segments_rev))
        return None

    popped = _pop_from_end(work, _PERSON_PRES_ACTIVE.get(pers, []))
    if popped is None:
        return None
    pers_surface, work = popped
    if not pers_surface:
        return None
    for stem in candidates:
        if work == stem + harmony:
            segments_rev.append({
                "surface": pers_surface, "role": "person",
                "label": _PERSON_LABEL.get(pers, pers),
            })
            segments_rev.append({
                "surface": harmony, "role": "tense",
                "label": f"present tense marker (-{harmony})",
            })
            segments_rev.append({"surface": stem, "role": "stem", "label": "root"})
            return list(reversed(segments_rev))
    return None


def _present_type3(work, root, pers, segments_rev):
    if pers == "SG3":
        # men + e + e → menee. The trailing e acts as the SG3 marker.
        if work != root + "ee":
            return None
        segments_rev.append({
            "surface": "e", "role": "person",
            "label": _PERSON_LABEL["SG3"],
        })
        segments_rev.append({
            "surface": "e", "role": "tense",
            "label": "present tense marker (-e)",
        })
        segments_rev.append({"surface": root, "role": "stem", "label": "root"})
        return list(reversed(segments_rev))

    popped = _pop_from_end(work, _PERSON_PRES_ACTIVE.get(pers, []))
    if popped is None:
        return None
    pers_surface, work = popped
    if not pers_surface or work != root + "e":
        return None
    segments_rev.append({
        "surface": pers_surface, "role": "person",
        "label": _PERSON_LABEL.get(pers, pers),
    })
    segments_rev.append({
        "surface": "e", "role": "tense",
        "label": "present tense marker (-e)",
    })
    segments_rev.append({"surface": root, "role": "stem", "label": "root"})
    return list(reversed(segments_rev))
