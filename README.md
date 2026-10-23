# Supplier Document Compliance Agent

An agentic assistant that reviews supplier documents (certificates, letters, attestations), extracts key fields, and flags documents that are out of compliance. Low-confidence decisions go to a human reviewer.

The project is set up like a client engagement: use-case definition → prerequisites → build → evaluation → governance → workshop.

## Repo map

| Folder | What lives there |
|---|---|
| `src/compliance_agent/` | The agent: extraction, tools, LangGraph graph, audit log |
| `eval/` | Evaluation harness: labelled set, predictors (baseline vs LLMs), metrics, reports |
| `data/` | Public source documents (`raw/`), extracted text (`processed/`), ground-truth labels (`labels/`) |
| `governance/` | Model card, NIST AI RMF risk register, human-review policy |
| `engagement/` | Use-case canvas, prerequisites checklist, solution architecture, workshop outline |
| `tests/` | Unit tests |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[baseline,dev]"
copy .env.example .env
python -m unittest discover -s tests -t .
python -m eval.run_eval --predictors dummy
```

## Data rule

**Only public documents.** No externship, employer, or client material. Write down where each document came from in `data/README.md`.

See [PLAN.md](PLAN.md) for the 4-week milestones.
