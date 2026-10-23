# Model Card: Toronto 311 Assistant

## Intended use
- **Users:** Toronto residents reporting non-emergency City service problems.
- **Task:** understand the problem, identify one of 15 supported request types, collect a location, and draft a service request.
- **Decision authority:** the agent **drafts only**. The resident must reply "yes" before anything is submitted, and that check is plain code, not a model decision.

## Out of scope
- Emergencies (the agent directs to 911).
- The roughly 520 other 311 request types in the City data (escalated to a human).
- Non-English conversations (not evaluated).
- Real submission to the City (demo writes to a local `outbox/` file).

## Components
| Component | Method | Why |
|---|---|---|
| Conversation and tool choice | Claude (`claude-opus-5-5`), hand-written tool-use loop | Handles open-ended conversation and clarifying questions |
| Request-type classifier | TF-IDF (char 3–5 grams) + logistic regression | Free, fast, offline, explainable; called first as a tool |
| Area statistics | Counts over 500,269 real 2025 311 requests | Grounds answers in real data |
| Knowledge base search | TF-IDF + cosine similarity over 20 articles | Advice comes from a known source, not model memory |
| Submission | Deterministic code after explicit "yes" | Removes the model from the irreversible step |

## Data
- **311 open data:** City of Toronto, *311 Service Requests – Customer Initiated*, 2025 file (500,269 rows). Contains request type, date, status, ward, FSA or intersection, division. **No resident text, no closing date.**
- **Resident messages:** 160 training and 96 test messages, **synthetic**, written for this project because the open data has no free text. The test set has 6 messages per class across 6 writing styles: plain, short, typos, second-language English, emotional, indirect.
- **Knowledge base:** 20 short articles written for this project. Not official City guidance.

## Results (see `eval/reports/` for the latest run)
| System | Accuracy | Macro F1 |
|---|---|---|
| Majority baseline | 6% | 0.01 |
| TF-IDF + logistic regression | 90% | 0.90 |

TF-IDF accuracy by style: plain 100%, short 100%, typos 94%, second-language 100%, **emotional 69%, indirect 75%**.
Knowledge base retrieval: right article first 85%, in top 3 95%.
Claude classification and agent scenario results: run `python -m eval.run_eval --llm --agent`.

## Known failure modes
1. **Keyword hijacking:** "a raccoon is on the sidewalk" is classified as *Sidewalk Snow Clearing Required* with 0.40 confidence, above the clarifying-question threshold. The word "sidewalk" outweighs "raccoon". Mitigation: Claude sees the top 3 guesses plus the full message and can override, which the scenario eval checks.
2. **Dead vs injured wildlife** is the most common confusion. By design the agent asks "is it alive?" when the scores are close.
3. **Emotional and indirect messages** describe the problem by its effects ("kids walking on the road because the path is buried"), which keyword features miss.
4. **Synthetic test data** was written by the same author as the training data, so real resident messages will likely score lower. Real-world accuracy is unknown until tested on real messages.
5. **Tuned on the test set:** the 0.3 confidence threshold and the char-gram retrieval setting were chosen by looking at test results, which inflates those numbers. A proper fix is a separate validation set.

## Fairness
- Accuracy is reported separately for each writing style so that residents who write with typos, in second-language English, or while upset are not quietly served worse. Second-language messages scored 100% for TF-IDF, but emotional (69%) and indirect (75%) messages are weaker. The agent's clarifying questions are the main mitigation.
- **Area statistics count reports, not problems.** Reporting rates differ between neighbourhoods (awareness, language, trust in the City), so low counts must not be read as low need. The tool output says this every time.

## Privacy
- The agent never asks for name, phone or email. Only the problem and location are collected.
- Conversations are sent to the Anthropic API. A real deployment would need a data-processing agreement and a retention policy.
- Audit logs contain conversation text. They are local and git-ignored, and a real deployment would need a retention period.
