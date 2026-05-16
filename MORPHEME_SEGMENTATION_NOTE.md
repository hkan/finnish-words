# Morpheme Segmentation Limitation in Omorfi

## Problem

The labelsegment.hfst component produces linguistically non-standard morpheme breakdowns for certain verbs.

**Example: "tiesitkö" (did you know?)**
- Current output: `ti + es + i + t + kö`
- Correct breakdown: `tie + si + t + kö`

## Root Cause

According to standard Finnish morphology and confirmed sources:
- Root: **tie** (derived from Proto-Finnic *tee, meaning "road/way")
- Past tense marker: **-si**
- Person/number: **-t** (2nd person singular)
- Clitic: **-kö** (question particle)

The labelsegmenter breaks this down as atomic units (`ti`, `es`, `i`) rather than recognizing the tense marker (`si`) as a coherent morpheme.

## Sources

1. **Wiktionary (etymology)**: "Equivalent to tie + -tää"
2. **Finnish Grammar Resource (uusikielemme.fi)**: Shows imperfect conjugation as:
   - Present: tiedän
   - Imperfect: **tiesin** (tie + si + n)

## Current Implementation

We expose both pieces of information separately:
- **morphemes array**: Raw segmenter output (as Omorfi produces it)
- **features object**: Analyser output (correct grammatical tags like TENSE=PAST)

This allows users/developers to:
1. See what Omorfi segments
2. See the correct grammatical interpretation from the analyser
3. Form their own conclusions about alignment

We do **NOT** attempt to map or reconstruct segmentation, as that would introduce unsupported linguistic claims.

## Recommendation

This is a **known limitation of Omorfi's labelsegmenter**, not a bug in word-breakdown. The analyser data is correct; only the visual segmentation differs from standard morphology.

If higher linguistic accuracy is needed, consider:
- Post-processing segmenter output for known verb patterns
- Documenting this discrepancy in frontend UI
- Reporting to Omorfi maintainers if interested in upstream fix
