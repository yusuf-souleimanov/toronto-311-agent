# Use-Case Canvas

*Write this in Week 1 before building anything. It is the first thing you'd hand a client.*

| | |
|---|---|
| **Problem** | Compliance teams manually check hundreds of supplier documents for expiry. It's slow, and stale docs slip through. |
| **Users** | Compliance analyst (daily), compliance manager (reviews exceptions, owns policy) |
| **Current process** | Steps, time per doc, error rate (estimate, and say it's an estimate) |
| **Why an agent, not a script?** | Documents vary in layout and wording; analysts also ask open questions ("which vendors have nothing newer than 2022?"). A script covers fixed layouts; an agent with tools covers both. |
| **Why not fully automated?** | Wrong flags carry regulatory and vendor-relationship cost. Human approves every flag. |
| **Success metrics** | Flag recall ≥ __%, review rate ≤ __%, time per doc cut from __ to __, cost per doc ≤ $__ |
| **Data needed** | Supplier PDFs, policy age limit, vendor master list (optional) |
| **Risks** | See `governance/risk_register.md` |
| **Out of scope (v1)** | Authenticity checks, non-English docs, automatic vendor outreach |
