# LearnLoop README Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the report-style README with a concise open-source product page for LearnLoop and publish it to `main`.

**Architecture:** The README remains the single entry point for product value, setup, configuration, and contribution guidance. Existing `UI.png` and `LearnLoop.png` remain local assets; implementation details stay in a dedicated technical-design section after the quick-start material.

**Tech Stack:** Markdown, Git, GitHub CLI, FastAPI, React/Vite.

## Global Constraints

- Write product-oriented Chinese and retain English only for code identifiers, commands, and configuration variables.
- Describe implemented behavior only; put future work exclusively in the roadmap.
- Do not include former branding, legacy deployment URLs, credentials, local absolute paths, or runtime data.
- Keep technical implementation detail after Quick Start and Configuration.
- Do not claim a license until the maintainer selects one.

---

### Task 1: Replace the README with the approved product-page hierarchy

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `UI.png`, `LearnLoop.png`, `backend/requirements.txt`, `frontend/package.json`, and the commands already used by the backend and Vite frontend.
- Produces: A standalone GitHub README with product header, highlights, workflow, quick start, configuration, technical design, roadmap, contribution guidance, and license note.

- [ ] **Step 1: Create a Markdown acceptance checklist before editing**

Record these required headings in `README.md`: `为什么选择 LearnLoop`, `核心工作流`, `快速开始`, `配置`, `技术设计`, `路线图`, `贡献`, and `许可证`.

- [ ] **Step 2: Verify the current README fails the acceptance checklist**

Run:

```powershell
$required = '为什么选择 LearnLoop','核心工作流','快速开始','配置','技术设计','路线图','贡献','许可证'
$content = Get-Content -Raw README.md
$required | Where-Object { $content -notmatch [regex]::Escape($_) }
```

Expected: at least `为什么选择 LearnLoop`, `路线图`, `贡献`, and `许可证` are reported as missing.

- [ ] **Step 3: Rewrite `README.md`**

Write the sections in this order:

```markdown
# LearnLoop

> LearnLoop 是一个开源 AI 学习闭环工具：将每日计划、知识检测、长期记忆和复盘连接起来，让每一次学习都能影响下一次行动。

![LearnLoop 界面](./UI.png)

## 为什么选择 LearnLoop
## 核心工作流
## 快速开始
## 配置
## 技术设计
## 路线图
## 贡献
## 许可证
```

Include a minimal `.env` table, backend and frontend startup commands, a first-use path, the five implemented Agent roles, the Memory/RAG boundary, five fixed Memory MCP tools, fallback behavior, and a roadmap limited to authentication, asynchronous work, retrieval evaluation, and desktop delivery.

- [ ] **Step 4: Verify the rewritten README**

Run:

```powershell
$required = '为什么选择 LearnLoop','核心工作流','快速开始','配置','技术设计','路线图','贡献','许可证'
$content = Get-Content -Raw README.md
$missing = $required | Where-Object { $content -notmatch [regex]::Escape($_) }
if ($missing) { throw "Missing headings: $($missing -join ', ')" }
if ($content -match 'AgentCoach|agreeable-forest|gentlefield') { throw 'Legacy branding or deployment URL found.' }
if (-not (Test-Path UI.png) -or -not (Test-Path LearnLoop.png)) { throw 'README image asset missing.' }
```

Expected: command exits successfully with no output.

- [ ] **Step 5: Run project verification**

Run:

```powershell
Set-Location backend
& 'D:\bjtuLearn\conda_env\evoagent310\python.exe' -m unittest discover -s tests -p 'test_branding.py' -v
Set-Location ..\frontend
npm run build
```

Expected: the branding test passes and Vite completes a production build.

- [ ] **Step 6: Commit and push the README rewrite**

Run:

```powershell
git add README.md
git commit -m "docs: rewrite LearnLoop product README"
git push origin main
```

Expected: GitHub `main` contains the rewritten README and the local branch is synchronized with `origin/main`.
