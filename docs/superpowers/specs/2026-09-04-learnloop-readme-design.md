# LearnLoop README Redesign

## Goal

Replace the report-style README with a developer-friendly open-source product page. A first-time visitor should understand LearnLoop's value in under 30 seconds, start it locally without reading implementation internals, and find deeper technical details when needed.

## Audience

- Learners evaluating a personal AI learning workflow.
- Developers evaluating the architecture or considering a contribution.
- Maintainers deploying LearnLoop locally or to their own infrastructure.

## Content hierarchy

1. Product header: name, concise value statement, UI image, and a short scope boundary.
2. Feature highlights: learning loop, durable memory, grounded knowledge-base Q&A, auditable execution, and fallback behavior.
3. How it works: architecture image plus a compact eight-step workflow.
4. Quick start: prerequisites, backend and frontend commands, and a first-use path.
5. Configuration: minimal environment variables and optional Redis/embedding choices.
6. Technical design: Agent responsibilities, Memory-versus-RAG boundary, MCP tools, scoring, and resilience.
7. Roadmap and contributing: near-term improvements, issue/PR expectations, and verification commands.
8. License placeholder: request an explicit license choice before publishing a license claim.

## Copy rules

- Use product-oriented Chinese with concise English technical identifiers where they are code or configuration names.
- Describe implemented behavior only; label future work as roadmap.
- Do not include prior Azure URLs, former branding, personal credentials, local paths, or generated runtime data.
- Keep the detailed implementation material after Quick Start and Configuration.

## Verification

- Markdown image paths resolve to `UI.png` and `LearnLoop.png`.
- README contains no `AgentCoach` or prior deployment URLs.
- Backend branding test and frontend production build continue to pass.
- The rewritten README is committed and pushed to `main`.
