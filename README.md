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

## Results (free eval, no API calls)

| System | Accuracy | Notes |
|---|---|---|
| Majority baseline | 6% | Always guesses one type |
| TF-IDF + logistic regression | 90% | 100% on plain, short and second-language messages; 69% emotional, 75% indirect |
| Knowledge base search | 85% right article first, 95% in top 3 | |

Claude's classification scores, cost per message, and the agent scenario pass rate come from `python -m eval.run_eval --llm --agent` (needs an API key, costs about a dollar).

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
