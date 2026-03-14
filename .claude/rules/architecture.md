# Architecture Rules

- Preserve the marketing-first Phase 1 scope unless a decision record changes it.
- Prefer additive changes over redesigns.
- The system uses a portal-first architecture with precomputed outputs; do not move core analysis to live portal prompts in Phase 1.
- Keep Teams bot scope intentionally lighter than the portal.
- Preserve the five core specialist agents unless there is a documented split.
- Avoid introducing a permanent runtime orchestrator.
- Do not move away from AWS-native assumptions without an ADR.
- If the structure changes, update the diagram source and changelog in the same change set.
