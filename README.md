<h1 align="center">⚡ RPD — Rapid Product Document</h1>

<p align="center">
  <strong>智能体确定性认知工程学外骨骼 — 跨会话长周期全生命周期状态机</strong>
  <br />
  <em>Deterministic cognitive exoskeleton for AI agents — cross-session, full-lifecycle state machine.</em>
</p>

<p align="center">
  <a href="https://github.com/ZhangJing-gugugaga/RPD-Skill/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-UNLICENSED-red" alt="License" /></a>
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/Claude_Code-8A2BE2" alt="Claude Code" /></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-00c853" alt="Quick Start" /></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Runtime-8__stdlib__Python-yellow" alt="8 stdlib Python" /></a>
  <a href="#-security-engine"><img src="https://img.shields.io/badge/Security-8__SEC__Rules-critical" alt="8 SEC Rules" /></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Fullstack-Next.js__Router__Ready-blue" alt="Next.js Ready" /></a>
  <a href="#-eval-matrix"><img src="https://img.shields.io/badge/Eval-11__Scenarios-brightgreen" alt="11 Eval Scenarios" /></a>
  <a href="#-multi-platform-installation"><img src="https://img.shields.io/badge/Platform-Claude%20Code%20%7C%20Cursor%20%7C%20VS%20Code-lightgrey" alt="Multi-platform" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="#中文版">中文版</a>
</p>

<p align="center">
  <img src="assets/hero.png" alt="RPD — Rapid Product Document" width="800" />
</p>

---

**你用 AI 做 Vibe Coding，每次开新对话它就失忆了。两周后回来，忘了当初为什么选 SQLite。**

RPD 是一个 [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills)，通过 **8 个零依赖的纯标准库 Python 脚本** 构建硬核运行时阻断协议，将项目记忆、技术栈决策、业务安全护栏硬化为高确定性的本地控制流。告别概率型 Cloud Memory 的废话糊墙，拒绝每次新开对话后的"精神断层"。

> **核心使命：硬化跨会话项目孪生状态，拦截决策 Spec 漂移，强行将具备概率不确定性的 AI 智能体死死锁在线性工程的高保真轨道上。**

---

## 🚀 Quick Start

### 1. Install the skill

```bash
# Project-level (recommended)
mkdir -p .claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git /tmp/rpd-skill
cp -r /tmp/rpd-skill/* .claude/skills/rpd/
rm -rf /tmp/rpd-skill
```

Or global install (available in all projects):

```bash
mkdir -p ~/.claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git /tmp/rpd-skill
cp -r /tmp/rpd-skill/* ~/.claude/skills/rpd/
rm -rf /tmp/rpd-skill
```

### 2. Verify installation

在 Claude Code 中输入：

```
我想做一个记账App
```

| 结果 | 含义 |
|------|------|
| Claude 问 "这个东西是给谁用的？" | ✅ Skill 已激活 |
| Claude 直接开始写代码 | ❌ 未安装成功，检查路径 |

### 3. Start building

```
# New project
我想做一个给独立开发者用的记账工具

# Take over existing project
接手这个项目

# Continue previous work
继续开发
```

---

## ✨ Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🔄 Git 原生状态隔离</h3>
      <p><code>.project-state.md</code> 采用 Git-native 架构，配合 <code>state-guard.py</code> 的 Branch Affinity Lock，在 <code>git merge</code> 时自动熔断跨分支静默覆盖。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ 8 条业务安全规则</h3>
      <p>SEC-001~008 函数级检测：短信轰炸、UGC 无审核、文件上传漏洞、Prompt 泄露、无认证中间件。大文件流式扫描，永不静默跳过。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🎯 确定性意图路由</h3>
      <p><code>intent-router.py</code> 零 Token 硬分类：新项目 / 接手半成品 / 继续开发。小白自动进入场景探索模式，标准用户走三视角诊断。</p>
    </td>
    <td width="50%" valign="top">
      <h3>📉 Token 坍缩经济学</h3>
      <p>Turbo Mode 将项目上下文压缩为 4 行 100 Token 矩阵。安全扫描始终执行（零 Token 消耗）。长周期 Vibe Coding 的成本控制极限。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔍 决策漂移检测</h3>
      <p>PRD 定了用 JWT，代码里却装了 express-session。<code>gap-analyzer.py</code> 自动比对文档决策与实际依赖，发出 CRITICAL 警告。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🌐 现代全栈感知</h3>
      <p>完美兼容 Next.js App Router 文件路由、Prisma/Supabase 等现代 BaaS。双向中英文词根映射字典，中文功能名自动匹配英文代码。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔐 原子化状态更新</h3>
      <p>备份 → 原子写入 → JSON Schema 校验 → 失败自动回滚。<code>state-guard.py</code> 保证状态文件永远不会写坏。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🗣️ 中英双语</h3>
      <p>从首条消息检测语言，全程跟随。所有模板、诊断问题、安全报告、PRD 输出均支持中英文。</p>
    </td>
  </tr>
</table>

---

## 📦 Multi-Platform Installation

### Claude Code (Native)

**Project-level install** (recommended — isolated per project):

```bash
mkdir -p .claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git /tmp/rpd-skill
cp -r /tmp/rpd-skill/* .claude/skills/rpd/
rm -rf /tmp/rpd-skill
```

**Global install** (available across all projects):

```bash
mkdir -p ~/.claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git /tmp/rpd-skill
cp -r /tmp/rpd-skill/* ~/.claude/skills/rpd/
rm -rf /tmp/rpd-skill
```

### One-line install (macOS / Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/ZhangJing-gugugaga/RPD-Skill/main/install.sh | bash
```

### One-line install (Windows PowerShell)

```powershell
iwr -useb https://raw.githubusercontent.com/ZhangJing-gugugaga/RPD-Skill/main/install.ps1 | iex
```

### Cursor

1. Clone this repository into your project
2. Cursor auto-discovers the skill via `.claude-plugin/plugin.json`
3. If auto-discovery fails: **Cursor Settings → Plugins** → paste `https://github.com/ZhangJing-gugugaga/RPD-Skill`

### VS Code + GitHub Copilot

1. Clone this repository into your project
2. VS Code auto-discovers the skill via `.claude-plugin/plugin.json`
3. For personal skills (all projects): copy to `~/.claude/skills/rpd/`

### Platform Compatibility

| Platform | Status | Install Method | Notes |
|----------|--------|----------------|-------|
| Claude Code | ✅ Native | `.claude/skills/rpd/` | Primary target, full feature support |
| Cursor | ✅ Supported | Auto-discovery via `plugin.json` | Clone repo into project |
| VS Code + Copilot | ✅ Supported | Auto-discovery via `plugin.json` | Clone repo into project |
| Codex | ⚠️ Experimental | Manual copy to skills directory | Core flows only |
| Gemini CLI | ⚠️ Experimental | Manual copy to skills directory | Core flows only |

---

## 🔄 Update

### Update to latest version

```bash
# If installed via git clone
cd .claude/skills/rpd && git pull origin main

# If installed globally
cd ~/.claude/skills/rpd && git pull origin main
```

### Check current version

```bash
grep '"version"' .claude/skills/rpd/.claude-plugin/plugin.json
```

### Pin to specific version

```bash
cd .claude/skills/rpd
git fetch --tags
git checkout v1.5.0  # or any tag
```

---

## 🏗 Architecture

```
[用户输入 (自然语言 / 快捷指令)]
                 │
                 ▼
      ┌──────────────────┐
      │ intent-router.py │ ──── 零 Token 意图硬路由与成熟度判断
      └──────────────────┘
                 │
  ┌──────────────┼──────────────┐
  ▼              ▼              ▼
Flow A          Flow B         Flow C
新项目          接手半成品      续传开发
三视角降维诊断  安全&技术探伤   差距分析&决策漂移
概念/落地版PRD  (流式分块防护)  (Next.js现代感知)
  │              │              │
  └──────────────┼──────────────┘
                 ▼
      ┌──────────────────┐
      │  state-guard.py  │ ──── 备份自滚回 & Git Branch Affinity Lock
      └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │state-validator.py│ ──── YAML Frontmatter JSON Schema 强卡口
      └──────────────────┘
```

### Runtime Toolbox

| Script | Deterministic Assertion | Invocation Trigger | Exit Codes |
|--------|------------------------|--------------------|------------|
| `intent-router.py` | Regex keyword hard-routing, maturity classification | Every conversation start | `0` success, `1` error |
| `security-scanner.py` | 8 SEC rules + path traversal + prompt injection + chunk streaming | Flow B/C cold start | `0` clear, `1` error, `2` blocked |
| `project-scanner.py` | Tech stack, components, API routes, TODOs | Flow B takeover | `0` success, `1` error |
| `gap-analyzer.py` | PRD vs code gap + decision drift + Next.js route detection | Flow C continue | `0` success, `1` error, `2` no state, `3` no features |
| `state-guard.py` | Atomic write + backup (max 10) + Git branch affinity lock | Before state file changes | `0` success, `1` error, `2` rollback, `3` not found, `4` conflict |
| `state-validator.py` | YAML frontmatter JSON Schema validation | After state file changes | `0` valid, `1` error, `3` invalid |
| `prd-validator.py` | Semantic gap audit (error handling, state machines, field specs) | After full PRD generation | `0` complete, `1` error, `2` gaps found |
| `run-eval.py` | 11 evaluation scenarios | Development / CI | `0` all pass, `1` some fail |

> **You never run these manually.** Claude calls them automatically at the appropriate workflow nodes.

### Under the Hood

| Component | Mechanism | Why It Matters |
|-----------|-----------|----------------|
| `intent-router.py` | Pre-compiled regex patterns, first-match-wins priority | Zero token consumption, deterministic routing |
| `security-scanner.py` | Function-level context window (`to_top` mode) + chunk streaming for >1MB files | Detects inline rate-limit middleware, never silently skips large files |
| `gap-analyzer.py` | Three-layer interface detection (API route → page route → data model) + bidirectional CN↔EN keyword map (50+ entries) | Chinese "登录" matches English `login` in code |
| `state-guard.py` | `branch-affinity` YAML field + `git branch --show-current` comparison | Prevents cross-branch silent merge of project memory |
| `state-validator.py` | JSON Schema with `minimum`/`maximum`/`pattern`/`enum` constraints | Blocks agent from selectively truncating metadata |
| `prd-validator.py` | Six-blind-spot checklist + `####` heading detection | Ensures PRD covers error handling, state machines, field specs |

---

## 🔐 Security Engine

| Rule ID | Name | Severity | Detection Pattern |
|---------|------|----------|-------------------|
| SEC-001 | SMS/Email API without rate limiting | `CRITICAL` | `sendSMS()` / `sendEmail()` without `rateLimit` in function context |
| SEC-002 | UGC write without content moderation | `CRITICAL` | `Comment.create()` without `contentModerat` in function context |
| SEC-003 | File upload without type validation | `HIGH` | `multer({storage})` without `fileFilter` |
| SEC-004 | File storage on local disk | `MEDIUM` | `diskStorage()` usage |
| SEC-005 | Hardcoded System Prompt | `HIGH` | `SYSTEM_PROMPT = "..."` in code |
| SEC-006 | Direct file URL without access control | `MEDIUM` | `res.json({url: ...})` without signed URL |
| SEC-007 | API route without authentication middleware | `HIGH` | `router.get("/api/...")` without `auth` in context window |
| SEC-008 | System Prompt via string concatenation | `LOW` | `SYSTEM_PROMPT = var + "..."` |

**Additional protections:**

| Protection | Mechanism |
|------------|-----------|
| Path traversal | `verify_path_safety()` — resolves symlinks, blocks `../` escape |
| Prompt injection | Pattern-based detection in state files (`ignore previous instructions`, etc.) |
| Large file bypass | Files >1MB streamed line-by-line with `[大文件流式拦截]` prefix |
| Comment filtering | Lines starting with `#`, `//`, `*` skipped to prevent false positives |

---

## 📐 Architecture Boundary & Non-Goals

RPD 专注于为大语言模型提供运行时确定性控制流约束，其工程职责遵循严格的**最小干预原则**：

| Scope | Description |
|-------|-------------|
| **Non-Goals** | 本系统不介入具体生成式代码的物理编写，不替代人类进行顶层商业/产品选型决策，亦不提供概率型的发散推演 |
| **Core Mission** | 硬化跨会话项目孪生状态，拦截决策 Spec 漂移，强行将具备概率不确定性的 AI 智能体死死锁在线性工程的高保真轨道上 |

---

## 📁 Directory Structure

```
rpd/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata (name, version, keywords)
├── SKILL.md                     # Main control instructions (bilingual, 6 Hard Constraints)
├── README.md                    # This file
├── scripts/
│   ├── intent-router.py         # Deterministic intent classification
│   ├── security-scanner.py      # 8 SEC rules + streaming + path traversal
│   ├── project-scanner.py       # Tech stack / component / route detection
│   ├── gap-analyzer.py          # PRD vs code + decision drift + Next.js
│   ├── state-validator.py       # YAML frontmatter JSON Schema validation
│   ├── state-guard.py           # Atomic write + backup + branch affinity
│   ├── prd-validator.py         # PRD completeness audit
│   └── run-eval.py              # 11 evaluation scenarios
├── references/
│   ├── prd-template.md          # PRD template (concept + full + security checklist)
│   ├── state-file-spec.md       # State file specification (5-col feature + 5-col decision)
│   ├── state-schema.json        # JSON Schema for state file validation
│   └── keyword-map.json         # CN↔EN keyword mappings (50+ entries)
├── eval/
│   └── scenarios/               # 11 eval scenario definitions
└── assets/
    └── example-state.md         # Example state file (new format)
```

---

## 🧪 Eval Matrix

11 evaluation scenarios covering all core functionality, run via `python scripts/run-eval.py`:

| Scenario | Name | What It Tests | Exit |
|----------|------|---------------|------|
| A | Empty Project | State file not found → correct error message | `1` |
| B | Corrupted State File | Invalid YAML frontmatter → schema rejection | `3` |
| C | Prompt Injection | Injection patterns in state file → hard block | `2` |
| D | Half-Finished Project | React+Vite detection → correct tech stack | `0` |
| E | Intent Router | 7 intent classification test cases (CN+EN) | `0` |
| F | PRD Validator | Complete / missing error handling / `####` headings | `0`/`2` |
| G | Decision Drift | No drift / MEDIUM coexistence / HIGH replacement | `0` |
| H | State Guard | Backup / cleanup / rollback operations | `0` |
| I | SEC Rules | SEC-001 detection, inline limiter bypass, comment filtering | `0`/`2` |
| O | Chinese Name | Chinese project name in YAML frontmatter | `0` |
| P | Turbo Mode | Vague input → `scene_exploration` routing | `0` |

---

## 📋 State File Example

`.project-state.md` — the project's digital twin, committed to Git:

```markdown
---
name: my-app
state_revision: 3
branch-affinity: main
last-commit-sha: a1b2c3d4
created: 2026-06-03
last-synced: 2026-06-08T14:30:00
status: in-development
entry-type: new-idea
---

## 功能进度清单
| 功能 | 子任务 | 优先级 | 状态 | 备注 |
|------|--------|--------|------|------|
| 用户登录 | 表单提交 | P0 | ✅ 已完成 | |
| 用户登录 | OAuth对接 | P0 | 🔨 进行中 | 70% |
| 记账功能 | 手动记账 | P0 | ⏳ 未开始 | |

## 关键决策记录
| 日期 | 类型 | 决策 | 原因 | 影响范围 |
|------|------|------|------|----------|
| 06-03 | 技术选型 | 用SQLite | 单机部署 | 数据层全局 |
| 06-05 | 安全策略 | 用JWT认证 | 无状态 | 认证层 |
```

---

## ❓ FAQ

| Question | Answer |
|----------|--------|
| 需要记住触发词吗？ | 不需要。`intent-router.py` 确定性分类意图，说人话就行 |
| Token 不够了怎么办？ | Turbo Mode 自动激活：跳过概念版 PRD，4 行 100 Token 输出，安全扫描照常（零 Token） |
| 可以中途改 PRD 吗？ | 可以。修改核心功能需重新冻结范围。概念版 PRD 改 >3 次建议先做用户调研 |
| 状态文件冲突了？ | `state-guard.py` 检测 Git UU 冲突 + Branch Affinity 不匹配 → exit(4) 硬阻断 |
| 能用在非 Node.js 项目？ | 可以。脚本扫描通用模式。框架检测对 React/Vue/Express/Flask/Django/Go/Java 最佳 |
| 大文件会被跳过吗？ | 不会。>1MB 文件流式逐行扫描，带 `[大文件流式拦截]` 前缀 |
| Next.js App Router 支持？ | 支持。`gap-analyzer.py` 检测 `app/api/xxx/route.ts` 的 `export async function` |

---

## 🤝 Contributing

| Step | Action |
|------|--------|
| 1 | Fork the repository |
| 2 | Create a feature branch (`git checkout -b feature/my-feature`) |
| 3 | Run eval tests (`python scripts/run-eval.py`) |
| 4 | All 11 scenarios must pass |
| 5 | Commit and open a pull request |

请先开 Issue 讨论重大变更。

---

<p align="center">
  <strong>不介入决策，不接管编码。RPD 旨在为生成式智能体硬化本地工程契约。</strong><br>
  <strong>锁死长周期时空记忆，阻断认知偏差，让每一颗 Token 都精准压进高确定性交付的弹夹。</strong>
</p>
