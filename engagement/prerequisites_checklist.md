# Customer Environment Prerequisites

*The checklist you'd walk through with a client before committing to a build.*

## Data
- [ ] Sample of ≥ 50 representative documents available
- [ ] Share of scanned vs digital PDFs known
- [ ] Written compliance policy (age limits, document types that count)
- [ ] Someone who can label ground truth and settle disagreements

## Platform and access
- [ ] Approved LLM provider(s) and region (data residency)
- [ ] Policy on sending documents to an external API, or need for a self-hosted model
- [ ] Where documents live (SharePoint, S3, file share) and how the agent gets read access
- [ ] Identity and auth model (SSO / OAuth)

## Operations
- [ ] Owner for the human review queue
- [ ] Where audit logs must be kept, and for how long
- [ ] Expected volume (docs/month) for cost estimate
- [ ] Change process for model or prompt updates

## Go / no-go
| Item | Status | Blocker? |
|---|---|---|
| | | |
