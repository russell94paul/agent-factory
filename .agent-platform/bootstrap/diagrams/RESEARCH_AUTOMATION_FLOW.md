# Research Automation Flow — Claude Subscription Mode

```mermaid
flowchart LR
    Q[Claude Code identifies unresolved evidence gap] --> C{Research depth?}
    C -->|repo can answer| E[Repository evidence]
    C -->|narrow/current| W[Claude Code web search]
    C -->|deep multi-step| P[Versioned Claude Research prompt]
    P --> M[Dependency-aware Research queue]
    M --> H[Human triggers Claude Research]
    H --> R[Raw Research report]
    R --> I[Deterministic ingest check]
    E --> S[Claude Research Synthesizer]
    W --> S
    I --> S
    S --> CL[Claims / contradictions]
    S --> D[Decision candidates]
    S --> X[Experiments]
    S --> A[Architecture impact]
    CL --> G[Human / deterministic gate]
    D --> G
    X --> G
    A --> G
    G --> B[Build DAG / knowledge writeback]
```

Only the Research launch/return is manual in v0. Prompt construction, queueing, ingestion, synthesis, reconciliation and downstream project updates are automated.
