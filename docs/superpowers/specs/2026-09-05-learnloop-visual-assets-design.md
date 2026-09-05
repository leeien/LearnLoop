# LearnLoop Visual Asset Redesign

## Goal

Replace the legacy README screenshots with two original LearnLoop visual assets that share a coherent visual language and contain no former branding.

## Asset 1: Product interface

- Destination: `UI.png`.
- Purpose: demonstrate LearnLoop as a personal AI learning-loop dashboard.
- Style: dark navy background, blue-to-purple gradients, restrained cyan success accents, rounded cards, clean sans-serif typography.
- Required content: LearnLoop wordmark; daily learning loop headline; task progress; knowledge mastery; due-review reminder; a RAG learning card; a compact weekly activity summary.
- Text: Chinese UI labels, with English retained only for concise technical labels such as `RAG`.
- Constraints: no former-project name or monogram, no outdated navigation wording, no watermark, no fake personal data, and no overflowing or unreadable text.

## Asset 2: System architecture

- Destination: `LearnLoop.png`.
- Purpose: explain the implemented application flow in a README-friendly overview.
- Style: light background, blue-purple primary nodes, cyan accent flow lines, rounded cards, Chinese labels with code identifiers in backticks where useful.
- Required flow: React frontend → FastAPI API → domain services and five Agents → LLM / RAG / Memory MCP → SQLite, Redis, Chroma → Learning Harness.
- Required learning loop: plan → task completion → Quiz → evaluation → durable memory → mastery and review → reflection.
- Constraints: no former branding, no external deployment names, no API keys, no hidden chain-of-thought, no watermark, and no unsupported components.

## Integration and verification

- Keep the existing README image references: `./UI.png` and `./LearnLoop.png`.
- Preserve the original assets only in Git history; replace the two files in the working tree.
- Check both files are valid PNGs, visually inspect them, verify README references resolve, scan image file names and README text for former branding, run the backend branding test and the frontend production build, then commit and push.
