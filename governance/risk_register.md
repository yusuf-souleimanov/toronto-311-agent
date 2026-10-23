# AI Risk Register (mapped to NIST AI RMF 1.0)

NIST AI RMF functions: **Govern** (policies, roles), **Map** (context, risks), **Measure** (test and track), **Manage** (respond and control).
Likelihood (L) and impact (I): 1 = low, 3 = high. Score = L × I.

| ID | Risk | RMF | L | I | Score | Control | Evidence |
|---|---|---|---|---|---|---|---|
| R1 | Request filed under the wrong type, so it goes to the wrong division | Measure, Manage | 2 | 2 | 4 | Classifier confidence threshold triggers clarifying questions; resident reviews the draft before submitting | Eval threshold table; `tests/test_agent.py` |
| R2 | Agent submits a request the resident didn't approve | Manage | 1 | 3 | 3 | No submit tool exists; submission is code that runs only on an explicit "yes" | `agent.py` yes-check; `test_nothing_is_submitted_without_yes`; injection scenario |
| R3 | Prompt injection in resident text changes agent behaviour | Map, Manage | 2 | 2 | 4 | System prompt treats resident text as information; tools validate inputs; no tool can act outside the draft | `eval/scenarios.json` injection case |
| R4 | Emergency handled as a routine 311 request | Map, Manage | 1 | 3 | 3 | System prompt sends emergencies to 911; knowledge base emergency article; scenario test | Gas-smell scenario |
| R5 | Advice not backed by City policy (hallucination) | Measure | 2 | 2 | 4 | Advice must come from `search_city_info`; KB marked as demo content | Retrieval eval; system prompt rule 4 |
| R6 | Some residents served worse: typos, second-language English, emotional writing | Measure | 2 | 2 | 4 | Accuracy reported per writing style; clarifying questions | Style table in eval report |
| R7 | Area stats misread as need ("few reports = no problem") | Map | 2 | 2 | 4 | Every stats result carries a "reports, not problems" note; agent told to explain it | `tools.get_area_stats`; system prompt rule 5 |
| R8 | Personal information collected or exposed | Govern, Manage | 1 | 2 | 2 | Agent told not to ask for name/phone/email; logs local and git-ignored | System prompt; `.gitignore` |
| R9 | Runaway tool loop drives up cost | Manage | 1 | 1 | 1 | `MAX_TOOL_STEPS = 8`; cost tracked per session | `test_tool_step_limit`; sidebar cost |
| R10 | Model or provider change silently shifts behaviour | Govern, Measure | 2 | 2 | 4 | Model name pinned in `config.py`; rerun the eval before any change | `eval/run_eval.py` |
| R11 | Synthetic test data overstates real accuracy | Measure | 3 | 2 | 6 | Disclosed in model card; next step is testing on real messages | `governance/model_card.md` |

**Highest residual risk: R11.** Every accuracy number comes from synthetic messages. Before any pilot, collect and label real resident messages (with consent) and re-run the eval.
