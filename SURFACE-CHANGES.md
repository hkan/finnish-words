# Surface Change Explanations — Future Feature

## What This Is

Currently the tool shows the stem, unlabeled morphemes, and labeled morphemes:

```
tiesitkö  (tietää)

  ties    stem
  i       
  t       active voice, past tense, 2nd person singular
  kö      question particle
```

A deeper level would also explain *why the surface form looks the way it does* — the phonological and morphological changes that happened between the dictionary root and what you see on the page:

```
tiesitkö  (tietää)

  ties    stem  (tietä-: diphthong ie→e, stem-final ä drops)
  i       past tense vowel
  t       2nd person singular
  kö      question particle  (front vowel harmony: -kö not -ko)
```

## Known Limitation: Omorfi Bundles Labels onto Final Segments

Omorfi's labelsegment output attaches all labels for a morphological slot to the *last* surface segment, leaving intermediate phonological material unlabeled. For example:

```
ti{STUB}[VERB]es{MB}i{MB}t[ACTV][PAST][SG2]{MB}kö[KO]
```

Here, `i` (the past tense theme vowel) has no label — all the information `[ACTV][PAST][SG2]` is on `t`. We surface `i` as an unlabeled row rather than hiding it, but we can't tell the user what it means without hand-written rules.

This is the most visible gap in v1. A learner sees `i` with no explanation and may be confused.

## Why It's Not in v1

Fixing this requires hand-written descriptions for every significant phonological pattern in Finnish:

- Vowel harmony (back vs. front vowel selection in suffixes: -ko/-kö, -ssa/-ssä)
- Consonant gradation (k/p/t weakening: e.g. tupa → tuvan)
- Stem vowel changes (diphthong reduction, vowel deletion)
- Past tense theme vowel `-i-` and its stem interactions
- Epenthetic vowels

Omorfi gives us the surface segments — it does not explain *why* those forms came out the way they did. We would need to author these descriptions ourselves, mapping from morpheme labels and phonological contexts to plain-language strings. This is a content authoring problem as much as an engineering one.

## How to Approach It Later

Two parts: labeling the unlabeled segments, and explaining stem changes.

**Labeling unlabeled segments** (e.g. the `i` past theme vowel):
Omorfi consistently leaves certain phonological elements unlabeled. These follow predictable patterns — a lookup table keyed on position + surrounding labels could cover most cases:

```python
# if unlabeled segment sits between verb stem and [PAST], it's the past theme vowel
("after_stub", "before_PAST") → "past tense vowel"
```

**Explaining stem changes** (e.g. tietää → ties):
Compare the `word_id` root form against the surface stem segment and infer the change programmatically. For the UI, a "show me why" toggle or expandable row would keep the default view clean.
