# Model Card: Supplier Document Compliance Agent

*Fill in during Week 4 using numbers from `eval/reports/`. Every claim here should point to a report.*

## Intended use
- **Users:** compliance analysts reviewing supplier documentation.
- **Task:** extract document type, vendor, and issue date; flag documents older than the policy limit.
- **Decision authority:** the agent *recommends*; a human approves every non-compliant flag and every low-confidence case.

## Out of scope
- Legal judgement on document validity or authenticity.
- Non-English documents, handwritten documents (unless evaluated, see below).
- Any document type not in the label set.

## Models and components
| Component | Model / method | Version | Why |
|---|---|---|---|
| Extraction | | | |
| Doc-type fallback | TF-IDF + LR | | |
| Compliance decision | Deterministic rule (`rules.py`) | | Auditable, no model drift |

## Evaluation data
- N documents, sources, date range, share scanned vs digital, share non-compliant.
- Labelling: who labelled, how disagreements were resolved.

## Results
Paste the summary table from the final eval report.

## Known failure modes
List at least 5 concrete failures you saw in error analysis, with doc IDs.

## Ethical and operational considerations
- Vendors could be wrongly flagged: impact and mitigation.
- PII in documents (signatures, names, addresses): how it is handled.
- Cost and latency at production volume.
