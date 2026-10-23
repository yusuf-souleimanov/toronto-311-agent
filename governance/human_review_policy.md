# Human-in-the-Loop Policy

## What the AI may do on its own
- Ask questions, explain, and share knowledge base guidance.
- Run read-only tools: classify, look up area statistics, search the knowledge base.
- Prepare a **draft** request.

## What needs a human
| Action | Who approves | How it's enforced |
|---|---|---|
| Submitting a request | The resident, by replying "yes" | Plain code in `Agent.send`; Claude has no submit tool |
| Anything outside the 15 supported types | A human 311 agent | `escalate_to_human` tool writes to the escalation queue |
| Emergencies | 911 | System prompt; agent drafts nothing |
| Resident asks for a person | A human 311 agent | `escalate_to_human` |

## When the agent must ask instead of assuming
- Classifier confidence below `CONFIDENCE_THRESHOLD` (0.3), or the top guess is "OTHER".
- Location is not specific (a vague location is rejected by `draft_service_request`).

## Choosing the threshold
From the eval's threshold table (TF-IDF, 96 test messages):

| Threshold | Agent asks a question | Accuracy when it doesn't ask |
|---|---|---|
| 0.2 | 12% | 94% |
| 0.25 | 21% | 100% |
| 0.3 | 27% | 100% |
| 0.4 | 43% | 100% |
| 0.5 | 54% | 100% |

Below 0.25, wrong guesses start getting through. 0.25 and 0.3 were both perfect on the test set; 0.3 was chosen as a safety margin because the test set is small (96 messages). Higher thresholds only add questions. Caveat: this was chosen on the test set; confirm on real messages.

## Audit
Every message, tool call, tool result, submission and escalation is logged as JSON lines in `logs/session-<id>.jsonl`. A reviewer can rebuild any conversation and see why the agent did what it did.
