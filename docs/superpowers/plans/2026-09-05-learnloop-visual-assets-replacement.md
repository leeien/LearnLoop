# LearnLoop Visual Asset Replacement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the two legacy README visual assets with a user-selected LearnLoop UI and a project-accurate architecture diagram, then publish the verified result.

**Architecture:** Keep the existing README image links unchanged: `UI.png` remains the product-interface asset and `LearnLoop.png` remains the system architecture asset. Edit the selected UI screenshot only enough to replace its old `AC` badge with a LearnLoop `LL` mark; use the approved generated architecture diagram because its layers map to the repository's frontend, API, domain Agent, capability, and data components.

**Tech Stack:** PNG assets, README Markdown, GitHub Actions-independent local validation, Git/GitHub.

## Global Constraints

- Preserve the existing README paths `./UI.png` and `./LearnLoop.png`; do not change prose or links unless validation shows an incorrect reference.
- The UI must retain the user-selected dashboard composition while replacing the `AC` monogram with `LL`.
- Neither asset may contain `AgentCoach`, an `AC` monogram, API keys, watermarks, QR codes, or third-party company logos.
- The architecture must represent React, FastAPI, five domain Agents, LLM/RAG/Memory, MCP tools, SQLite, Redis, Chroma, and the evaluation Harness.
- Do not push either binary asset until the user has approved the previews.

---

### Task 1: Prepare the user-selected UI asset

**Files:**
- Modify: `UI.png`
- Source: `C:\Users\LEE_LA~1\AppData\Local\Temp\codex-clipboard-201fed15-01a2-4a5f-9f2e-d9f626315188.png`

**Interfaces:**
- Consumes: the selected dashboard screenshot and the requirement to remove its legacy monogram.
- Produces: `UI.png`, a readable LearnLoop dashboard image with an `LL` mark.

- [ ] **Step 1: Inspect the selected screenshot and preserve its composition**

Run: open `C:\Users\LEE_LA~1\AppData\Local\Temp\codex-clipboard-201fed15-01a2-4a5f-9f2e-d9f626315188.png` with the image viewer.

Expected: the top-left brand reads `LearnLoop` and the only legacy visual identity is the dark rounded `AC` badge.

- [ ] **Step 2: Generate an image edit that changes only the legacy mark**

Use image generation with the screenshot as the reference and this instruction: `Keep this dashboard screenshot pixel-faithful. Replace only the dark rounded top-left AC badge with a matching dark rounded LL badge, rendered in cyan. Keep LearnLoop, every navigation label, card, chart, typography, layout, and all other pixels unchanged. Do not add a watermark or logo.`

Expected: a preview with `LL`, not `AC`, and no unintended content changes.

- [ ] **Step 3: Obtain user approval before replacement**

Show the generated preview in the conversation.

Expected: the user explicitly confirms it is the UI image to publish.

- [ ] **Step 4: Replace the repository UI asset after approval**

Run: copy the approved generated PNG to `D:\bjtuLearn\LearnCode\workplace\agents\LearnLoop\UI.png` with overwrite enabled.

Expected: `UI.png` is a PNG file and contains the approved dashboard.

### Task 2: Adopt the project-accurate architecture asset

**Files:**
- Modify: `LearnLoop.png`

**Interfaces:**
- Consumes: the approved generated architecture preview.
- Produces: `LearnLoop.png`, a visual map of the implemented application layers and learning loop.

- [ ] **Step 1: Validate the diagram against the implementation**

Run: inspect `README.md`, `frontend`, and `backend` for the React frontend, FastAPI API, domain Agents, RAG/Memory and MCP capability layer, plus SQLite, Redis, Chroma and evaluation Harness references.

Expected: each named architecture block is supported by the repository and no block claims a vendor-specific model or external SaaS.

- [ ] **Step 2: Obtain user approval for the architecture preview**

Show the approved architecture preview in the conversation with the mapping: `React → FastAPI → five Agents → LLM/RAG/Memory and MCP → SQLite/Redis/Chroma/Harness`.

Expected: the user explicitly accepts this architecture image.

- [ ] **Step 3: Replace the repository architecture asset after approval**

Run: copy the approved generated PNG to `D:\bjtuLearn\LearnCode\workplace\agents\LearnLoop\LearnLoop.png` with overwrite enabled.

Expected: `LearnLoop.png` is a PNG file and has the title `LearnLoop 系统架构`.

### Task 3: Verify README integration and publish

**Files:**
- Verify: `README.md`
- Verify: `UI.png`
- Verify: `LearnLoop.png`

**Interfaces:**
- Consumes: both approved replacement PNGs.
- Produces: a verified Git commit and remote update containing only the assets and any required documentation validation change.

- [ ] **Step 1: Verify image files and README references**

Run: `rg -n "^!\\[LearnLoop 界面\\]\\(\\./UI\\.png\\)|^!\\[LearnLoop 系统架构图\\]\\(\\./LearnLoop\\.png\\)" README.md` and inspect both PNGs with the image viewer.

Expected: both exact Markdown links are present and each PNG is legible, branded LearnLoop, and free of the prohibited legacy material.

- [ ] **Step 2: Run project regression checks**

Run: `D:\bjtuLearn\conda_env\evoagent310\python.exe -m unittest backend.tests.test_branding` from the repository root, then `npm run build` from `frontend`.

Expected: the branding test passes and the frontend production build completes without errors.

- [ ] **Step 3: Review the binary diff before publication**

Run: `git status --short` and `git diff --stat`.

Expected: only `UI.png` and `LearnLoop.png` are staged for the visual replacement; the pre-existing design specification and implementation plan remain separate documentation commits.

- [ ] **Step 4: Commit and push after all approvals**

Run: `git add UI.png LearnLoop.png && git commit -m "docs: refresh LearnLoop README visuals" && git push origin main`.

Expected: the remote `main` branch contains the two approved assets.
