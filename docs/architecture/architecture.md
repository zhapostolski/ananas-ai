# Ananas AI Platform — Internal Architecture

## Purpose
Build a marketing-first internal AI platform on `ai.ananas.mk` that provides daily marketing intelligence, portal-based structured analysis, Teams channel summaries, Teams bot engagement, executive and marketing briefs, and a reusable technical foundation for future company-wide AI adoption.

## Core design choices
- existing Ananas portal stack remains the user-facing application layer
- AWS hosts the runtime and operational components
- Microsoft Entra ID handles identity and access
- specialist agents produce structured outputs
- the portal reads from a database-backed read layer
- Teams serves as the communication and lightweight engagement surface
- model routing controls cost and quality
- every important behavior is captured in versioned config

## Major layers
1. user access and application entry
2. portal layer
3. thin control layer
4. read layer
5. data layer
6. runtime layer
7. specialist agents
8. integration layer
9. reliability layer
