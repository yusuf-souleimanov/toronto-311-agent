# AI Risk Register (mapped to NIST AI RMF 1.0)

The RMF has four functions: **Govern** (policies, roles), **Map** (context, risks), **Measure** (test and track), **Manage** (prioritise and respond). Each risk names the function(s) its controls live under.

Likelihood and impact: 1 (low) to 3 (high). Score = L × I.

| ID | Risk | RMF function | L | I | Score | Control in this project | Evidence |
|---|---|---|---|---|---|---|---|
| R1 | Stale document marked compliant (false negative) | Measure, Manage | | 3 | | Flag recall tracked in every eval; undated docs default to review | `eval/reports/` |
| R2 | Wrong date extracted (OCR or ambiguous format) | Measure | | | | Deterministic date parser cross-checks the LLM; disagreement → review | |
| R3 | Model hallucinates a vendor or date not in the text | Measure, Manage | | | | Require a quoted span for each extracted field; reject if not found in text | |
| R4 | Over-reliance: reviewers rubber-stamp agent output | Govern | | | | Human-review policy; show source span next to every flag | `human_review_policy.md` |
| R5 | PII from documents sent to third-party LLM API | Map, Manage | | | | Redact before sending; data-processing note in model card | |
| R6 | Provider model change shifts behaviour silently | Govern, Measure | | | | Pin model versions; rerun eval before any version change | |
| R7 | Prompt injection via document text | Map, Manage | | | | Document text passed as data, never as instructions; tools have no write access beyond the review queue | |
| R8 | | | | | | | |
