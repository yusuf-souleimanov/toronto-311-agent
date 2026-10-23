# Human Review Policy

## A document goes to human review when any of these hold
1. The compliance rule returns "undecided" (no date found, or a future date).
2. Extraction confidence < `REVIEW_CONFIDENCE_THRESHOLD`.
3. The LLM and the deterministic date parser disagree on the issue date.
4. The agent recommends **non-compliant** (every flag gets human sign-off before action).

## What the reviewer sees
- The recommendation and the rule that produced it.
- The exact text span each field came from.
- Confidence and which check triggered review.

## What gets logged
Reviewer decision (approve / override), override reason, timestamp. Overrides are fed back into the labelled set for the next eval run.

## Choosing the threshold
TODO (Week 3): plot flag recall and review rate against threshold from the eval data, then pick the point you would defend to a compliance manager. Put the chart here.
