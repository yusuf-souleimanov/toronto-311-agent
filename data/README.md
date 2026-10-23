# Data

- `raw/`: original public PDFs, named `<doc_id>.pdf` (for example `D001.pdf`). Not committed.
- `processed/`: extracted text, `<doc_id>.txt`, written by `compliance_agent.extraction`. Not committed.
- `labels/labels.csv`: hand-labelled ground truth, one row per document. **Committed.**

## Label schema (`labels/labels.csv`)

| Column | Format | Notes |
|---|---|---|
| `doc_id` | `D001` | Matches the file name in `raw/` |
| `doc_type` | one of `certificate`, `letter`, `attestation`, `audit_report`, `other` | Edit `DOC_TYPES` in `src/compliance_agent/schema.py` if you change this list |
| `vendor_name` | free text | Legal name as printed |
| `issue_date` | `YYYY-MM-DD` or blank | Blank if the document has no date |
| `is_compliant` | `true` / `false` | Ground truth from the rule in `compliance_agent.rules` |
| `source_url` | URL | Where you got the public document |
| `notes` | free text | Anything odd: scan quality, two dates, handwriting |

## Sourcing log

Fill this in as you collect documents. Aim for about 100, with a deliberate mix of clean, scanned, and tricky ones.

| doc_id | Source | Why it's in the set |
|---|---|---|
| | | |
