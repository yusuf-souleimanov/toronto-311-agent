# Use-Case Canvas: 311 Intake Assistant

| | |
|---|---|
| **Client (hypothetical)** | A city's 311 contact centre |
| **Problem** | Toronto logged about 500,000 customer-initiated 311 requests in 2025. Many are routine (missed pickups, potholes, dead animals) but still need an agent's time to classify and route, and a misrouted request is delayed. |
| **Users** | Residents (file requests); 311 agents (handle escalations); division staff (receive requests) |
| **Current process** | Resident calls or uses a web form → agent or resident picks a request type from 500+ options → request routed to a division |
| **Why an agent, not a form?** | Residents describe problems in their own words ("raccoon on the sidewalk"), not in City categories. An agent can ask the one question that matters ("alive or dead?") and pick among 500+ types. |
| **Why not fully automated?** | Wrong or unwanted submissions waste crews' time and erode trust. The resident confirms every request; anything unusual goes to a person. |
| **Scope (v1)** | 15 high-volume request types, covering about 160,000 requests (roughly a third of 2025 volume). Everything else is escalated. |
| **Success metrics** | Correct request type ≥ 90% on real messages; clarifying questions on ≤ 30% of conversations; zero submissions without confirmation; emergencies always sent to 911 |
| **Data needed** | Historical 311 data (have it: open data); real resident messages with correct types (gap: currently synthetic); official service guidance (gap: currently demo articles) |
| **Key risks** | See `governance/risk_register.md`. Biggest: accuracy measured on synthetic messages only. |
| **Out of scope** | Emergencies, payments, permits, licences, tracking existing requests, non-English conversations |
