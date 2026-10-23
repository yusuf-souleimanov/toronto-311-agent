# Client Environment Prerequisites

The checklist to walk through with the client before committing to a pilot. Status shows where this demo stands.

## Data
| Item | Demo status | Needed for a pilot |
|---|---|---|
| Historical request data with types and divisions | ✅ 2025 open data | Same, plus closing dates for SLA insights |
| Real resident messages labelled with the correct type | ❌ synthetic | 500+ consented, de-identified messages |
| Official service guidance per request type | ❌ demo articles | Approved content from the City's 311 knowledge base |
| Full list of request types and routing rules | Partial (15 of ~539) | Complete mapping from the City |

## Platform and access
| Item | Demo status | Needed for a pilot |
|---|---|---|
| Approved LLM provider and data residency | Anthropic API, default region | Confirm Canadian data residency requirements |
| Integration with the work management system | ❌ writes to local file | API access to create service requests |
| Authentication | None | Resident auth optional; staff SSO for the escalation queue |

## Operations
| Item | Demo status | Needed for a pilot |
|---|---|---|
| Owner of the escalation queue | n/a | Named 311 team |
| Audit log retention | Local files | Records retention policy |
| Accessibility (AODA) review of the chat interface | ❌ | Required |
| French and other languages | ❌ | Decide scope |
| Budget per conversation | Measured in eval | Approve monthly cap |

## Go / no-go for a pilot
- **Go** when real-message accuracy ≥ 90%, the integration API is available, and the escalation queue has an owner.
- **No-go** if residents' messages can't be sent to an external LLM provider; in that case, evaluate a self-hosted model.
