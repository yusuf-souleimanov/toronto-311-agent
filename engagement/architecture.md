# Solution Architecture

## Diagram

```mermaid
flowchart LR
    U[Analyst] -->|question or doc batch| UI[Chat UI]
    UI --> G[LangGraph agent]
    G --> T1[read_document]
    G --> T2[extract_fields<br/>LLM + structured output]
    G --> T3[check_compliance<br/>deterministic rule]
    G --> T4[search_documents<br/>ChromaDB]
    G --> T5[flag_for_review]
    T5 --> Q[(Review queue)]
    Q --> R[Human reviewer]
    G --> A[(Audit log JSONL)]
    P[PDFs] --> X[Extraction + OCR] --> D[(Text store)] --> T1
    D --> E[Embeddings] --> T4
```

## Design decisions (fill in the reasoning, this is what interviewers ask about)

| Decision | Chosen | Alternatives considered | Why |
|---|---|---|---|
| Who decides compliance | Deterministic rule | LLM judges directly | |
| Where the LLM is used | Field extraction + Q&A only | Everywhere | |
| Retrieval vs direct read | Direct read for single docs, RAG for cross-doc questions | RAG for everything | |
| Orchestration | LangGraph | Plain loop, CrewAI | |
| Human-in-the-loop | Graph interrupt before `review` | Post-hoc reporting | |
| Deployment target | | | |

## Non-functional
- Cost per 1,000 docs: (from eval)
- Latency per doc: (from eval)
- Scaling: what breaks first at 10× volume
