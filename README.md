# Toronto 311 Assistant

A conversational AI agent that helps Toronto residents file non-emergency 311 service requests. It understands the problem, asks clarifying questions when unsure, looks up real City data about the resident's area, and drafts a request that **only the resident can submit**.

Built as an end-to-end agentic AI engagement: use-case definition, build, evaluation against a traditional ML baseline, governance, and a client workshop outline.

> Unofficial portfolio project. Uses [City of Toronto Open Data](https://open.toronto.ca/dataset/311-service-requests-customer-initiated/) (Open Government Licence – Toronto). Nothing is sent to the City.

## What it does

```
Resident: "there's a raccoon lying on the sidewalk at Bloor and Ossington"
Agent:    classify_request -> "Pick up Dead Wildlife" 0.23 vs "Injured - Wildlife" 0.22  (not confident)
          "Is the raccoon alive or dead?"
Resident: "dead"
Agent:    search_city_info -> tips;  draft_service_request -> draft
          "Here's your request: ... Reply yes to submit."
Resident: "yes"
Code:     submits (not Claude) -> DEMO-20261022-231500
```

| Piece | What it is |
|---|---|
| **Agent loop** | Hand-written Claude tool-use loop (`agent311/agent.py`), 5 tools, step limit |
| **Traditional ML** | TF-IDF + logistic regression classifier (`agent311/classifier.py`), used as a tool and as the baseline |
| **Real data** | 500,269 Toronto 311 requests from 2025 (`agent311/data.py`, `agent311/stats.py`) |
| **Retrieval (RAG)** | TF-IDF search over a 20-article knowledge base (`agent311/knowledge.py`) |
| **Human-in-the-loop** | Claude can only *draft*; submission happens in code after the resident types "yes" |
| **Audit log** | Every message, tool call and result as JSON lines (`logs/`) |
| **Evaluation** | Classification (by writing style), retrieval, and scripted agent scenarios (`eval/`) |
| **Governance** | Model card, risk register, human-review policy (`governance/`) |
| **Engagement docs** | Use-case canvas, prerequisites, architecture, workshop outline (`engagement/`) |

## Results (eval run 2026-10-23)

**Classification** (96 test messages, 15 request types + OTHER):

| System | Accuracy | Macro F1 | Cost / message | Time / message |
|---|---|---|---|---|
| Majority baseline | 6% | 0.01 | $0 | 0.000 s |
| TF-IDF + logistic regression | 90% | 0.90 | $0 | 0.001 s |
| Claude Haiku 5.5 | 99% | 0.99 | $0.00007 | 1.1 s |
| Claude Opus 5.5 | 100% | 1.00 | $0.0029 | 1.6 s |

**By writing style** (fairness check):

| System | Plain | Short | Typos | 2nd language | Emotional | Indirect |
|---|---|---|---|---|---|---|
| TF-IDF | 100% | 100% | 94% | 100% | 69% | 75% |
| Haiku 5.5 | 100% | 100% | 100% | 100% | 100% | 94% |
| Opus 5.5 | 100% | 100% | 100% | 100% | 100% | 100% |

**Agent scenarios: 8/8 passed** ($0.22 total, about $0.01–0.04 per conversation): drafts with an address, asks for a location when missing, asks "alive or dead?" for an ambiguous animal, sends a gas smell to 911, escalates property tax, answers an area question from real data, and resists a prompt injection (it drafted the real issue and submitted nothing).

**Knowledge base search:** right article first 85%, in top 3 95%.

### What this means
- The LLMs close the gap exactly where keyword features fail: emotional and indirect messages (TF-IDF 69–75% → Claude 94–100%).
- Haiku reaches 99% at about 1/40th of Opus's cost per message, so it's the sensible default for classification at 311 volume.
- **Big caveat:** the test messages are synthetic and were written by Claude, so Claude scoring 99–100% on them is partly circular. Expect lower numbers on real residents' messages. See [governance/model_card.md](governance/model_card.md).

Full report: `python -m eval.run_eval --llm --agent` (about $0.50 per run).

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # then paste your ANTHROPIC_API_KEY into .env

python -m agent311.data         # download the 2025 data (~7 MB zip, 75 MB CSV)
python -m agent311.classifier   # train the classifier
python -m unittest discover -s tests -t .
python -m eval.run_eval         # free eval
streamlit run app.py            # web chat
python -m agent311.chat         # or terminal chat
```

## Where to start reading

See [LEARNING_GUIDE.md](LEARNING_GUIDE.md) for the reading order and the key ideas behind each file.
