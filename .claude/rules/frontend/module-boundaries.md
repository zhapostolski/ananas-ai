# Frontend Module Rules

- Performance module reads Performance Agent outputs only.
- CRM & Lifecycle module reads CRM Agent outputs only.
- Reputation module reads Reputation Agent outputs only.
- Marketing Ops module reads Marketing Ops outputs only.
- Cross-Channel Brief reads the summary layer.
- Portal modules consume structured API data; avoid embedding model-specific logic in the frontend.
- Implement graceful degradation: show last successful output, timestamp, and status banner if fresh data is unavailable.
- Keep UI structured and operational, not chat-first.
