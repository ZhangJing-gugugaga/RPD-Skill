<h1 align="center">RPD — Rapid Product Document</h1>

<p align="center">
  <strong>给你的 AI 编程项目装上"记忆"，不会每次开新对话就失忆。</strong>
  <br />
  <em>Give your Vibe Coding project "memory" — no more amnesia across conversations.</em>
</p>

<p align="center">
  <a href="https://github.com/ZhangJing-gugugaga/RPD-Skill"><img src="https://img.shields.io/badge/GitHub-RPD--Skill-blue" alt="GitHub" /></a>
  <a href="#installation--安装2-minutes"><img src="https://img.shields.io/badge/Install-2_min-green" alt="Install" /></a>
  <a href="#scripts--脚本工具箱"><img src="https://img.shields.io/badge/Scripts-8_Python-yellow" alt="Scripts" /></a>
  <a href="#hard-constraints--硬性红线"><img src="https://img.shields.io/badge/Security-Hard_Constraints-red" alt="Security" /></a>
  <a href="https://github.com/ZhangJing-gugugaga/RPD-Skill"><img src="https://img.shields.io/badge/Language-EN%20%7C%20ZH-purple" alt="Bilingual" /></a>
</p>

<p align="center">
  <a href="#english">English</a> | <a href="#中文版">中文版</a>
</p>

---

# English

## The Problem

You're Vibe Coding with AI. Three things kill your project:

| Breakpoint | What Happens | RPD's Fix |
|-----------|--------------|-----------|
| **Requirement Fracture** | "I want to build an App" → 3 days later, direction is wrong | Three-perspective diagnosis → Concept PRD → Scope freeze |
| **Context Fracture** | Switch AI conversation, it knows nothing about your project | `.project-state.md` state file, cross-session memory |
| **Time Fracture** | Come back after 2 weeks, forgot why chose SQLite | Key decision records + decision drift detection |

**One sentence: RPD gives your project "memory" so every new AI conversation picks up where you left off.**

---

## Features

- 🩺 **Three-perspective diagnosis** — User / Business / Technical perspectives, max 3 questions per round
- 📄 **Two-tier PRD** — Concept PRD (≤200 words) for alignment, Full PRD for development
- 🔒 **Security hard block** — 8 business security rules (SEC-001~008), function-level detection
- 🧠 **State file** — `.project-state.md` with subtask-level progress tracking
- 🔍 **Decision drift detection** — Detects when code diverges from documented decisions
- 🚀 **Deterministic routing** — `intent-router.py` classifies intent without LLM guessing
- 🛡️ **Path traversal protection** — Blocks `../` and symlink escape attacks
- 📊 **PRD completeness validation** — Script checks for missing error handling, state machines, field specs
- 💾 **Atomic state updates** — Backup + atomic write + validation + auto-rollback
- 🌐 **Bilingual** — All prompts, templates, and outputs in Chinese and English

---

## Installation（2 minutes）

### Step 1: Find your skills directory

```bash
# Project-level (recommended)
your-project/.claude/skills/rpd/

# Global (all projects)
~/.claude/skills/rpd/
```

### Step 2: Copy files

```bash
# From this repo
cp -r skills/rpd /your/project/.claude/skills/rpd
```

### Step 3: Verify

Say in Claude Code:
```
I want to build a personal finance tracker
```

If Claude asks "Who is the target user?" → ✅ Skill is active.
If Claude starts coding immediately → ❌ Not installed, check path.

---

## Three Entry Points

```
┌─────────────────────────────────────────────────┐
│              Project Lifecycle                    │
│                                                   │
│   💡 New Idea       🔧 Half-done      ⏸️ Paused   │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  ┌────────┐      ┌──────────┐      ┌──────────┐  │
│  │ Flow A │      │ Flow B   │      │ Flow C   │  │
│  │ New    │      │ Takeover │      │ Continue │  │
│  └────────┘      └──────────┘      └──────────┘  │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  PRD + State       Scan + PRD       Gap Analysis  │
│   File              File             + Action Plan │
└─────────────────────────────────────────────────┘
```

### Flow A: New Project

> **Trigger:** "I want to build..."

**Standard mode** (clear requirements):
1. Three-perspective diagnosis (User → Business → Technical), max 3 questions/round
2. Concept PRD (≤200 words) → User confirms
3. Scope freeze → Full PRD
4. State file generated

**Beginner mode** (vague idea):
1. `intent-router.py` detects vague input → Scene Exploration Mode
2. 3 rounds of casual conversation (scenarios → pain points → expectations)
3. Concept PRD in plain language → Skip standard diagnosis

### Flow B: Takeover Half-Finished

> **Trigger:** "Take over this project"

1. Security scan (hard block if secrets found)
2. Project scan (tech stack, components, API routes)
3. Confirm inference → Generate PRD + State file

### Flow C: Continue Development

> **Trigger:** "Continue development"

1. Security scan + State validation
2. Gap analysis (PRD vs actual code + decision drift)
3. Action plan with next steps

**Review mode** (inactive >3 days): Outputs PRD summary + feature status, asks "continue or revise?"

---

## Scripts

8 Python scripts, **zero dependencies, stdlib only**:

| Script | Purpose | Auto-triggered |
|--------|---------|----------------|
| `intent-router.py` | Deterministic intent classification | Every conversation start |
| `security-scanner.py` | 8 SEC rules + path traversal + prompt injection | Flow B/C start |
| `project-scanner.py` | Tech stack, components, API routes | Flow B |
| `gap-analyzer.py` | PRD vs code gap + decision drift detection | Flow C |
| `state-validator.py` | State file JSON Schema validation | After state changes |
| `state-guard.py` | Backup + atomic write + Git concurrency check | Before state updates |
| `prd-validator.py` | PRD completeness (error handling, state machines) | After PRD generation |
| `run-eval.py` | 11 evaluation scenarios | Development/testing |

> **You don't need to run these manually.** Claude calls them automatically.

---

## Hard Constraints

These rules are **absolutely non-negotiable** during execution:

| # | Rule | Enforcement |
|---|------|-------------|
| 1 | Security scan cannot be skipped | exit code 2 hard block |
| 2 | State validation cannot be skipped | exit code 3 rollback |
| 3 | Max 3 questions per round | Text constraint |
| 4 | Don't skip concept PRD | Text constraint |
| 5 | Don't overwrite without backup | `state-guard.py` |
| 6 | No path traversal | `verify_path_safety()` |

---

## State File: Your Project's Brain

`.project-state.md` records everything the AI needs to resume:

```markdown
---
name: my-app
state_revision: 3
---

## 功能进度清单
| 功能 | 子任务 | 优先级 | 状态 | 备注 |
|------|--------|--------|------|------|
| 用户登录 | 表单提交 | P0 | ✅ 已完成 | |
| 用户登录 | OAuth对接 | P0 | 🔨 进行中 | 70% |

## 关键决策记录
| 日期 | 类型 | 决策 | 原因 | 影响范围 |
|------|------|------|------|----------|
| 06-03 | 技术选型 | 用SQLite | 单机部署 | 数据层全局 |

## 诊断记录
| 轮次 | 视角 | 问题 | 用户回答摘要 |
|------|------|------|-------------|
| R1 | 用户 | 目标用户是谁？ | 独立开发者 |
```

---

## Quick Reference

| You Say | RPD Does |
|---------|----------|
| "I want to build..." | Flow A: New Project |
| "Take over this project" | Flow B: Takeover |
| "Continue development" | Flow C: Continue |
| "Quick mode" / "Simple version" | Turbo Mode (minimal output) |
| "Review" / "What was done before" | Review Mode |

---

## FAQ

### Do I need to memorize trigger words?
No. Just speak naturally. `intent-router.py` classifies your intent deterministically.

### What if I run out of tokens?
Turbo mode activates: skip concept PRD, minimal output format, security scan still runs (no tokens).

### Can I modify PRD mid-project?
Yes. Changing core features requires re-freeze scope. Concept PRD revised >3 times → user research suggested.

### What if state file conflicts?
`state-guard.py` checks Git concurrency before writing. If conflict detected (UU), it blocks with exit code 4.

---

# 中文版

## 问题

你在用 AI 做 Vibe Coding。有三件事会杀死你的项目：

| 死法 | 症状 | 解药 |
|------|------|------|
| **需求断裂** | "我想做一个 App" → 3 天后，方向跑偏了 | 三视角诊断 → 概念版 PRD → 范围冻结 |
| **上下文断裂** | 换个 AI 对话，它完全不知道你的项目 | `.project-state.md` 状态文件，跨会话记忆 |
| **时间断裂** | 两周后回来，忘了当初为什么选 SQLite | 关键决策记录 + 决策漂移检测 |

**一句话：RPD 让项目有记忆，每次开新 AI 对话都能接上。**

---

## 功能

- 🩺 **三视角诊断** — 用户/商业/技术三个视角，每轮最多 3 个问题
- 📄 **两级 PRD** — 概念版 PRD（≤200 字）快速对齐，落地版 PRD 指导开发
- 🔒 **安全硬阻断** — 8 条业务安全规则（SEC-001~008），函数级检测
- 🧠 **状态文件** — `.project-state.md` 支持子任务级进度追踪
- 🔍 **决策漂移检测** — 检测代码是否偏离了文档记录的决策
- 🚀 **确定性路由** — `intent-router.py` 分类意图，不依赖 LLM 猜测
- 🛡️ **路径遍历防护** — 阻止 `../` 和符号链接逃逸攻击
- 📊 **PRD 完整性校验** — 脚本检查缺失的错误处理、状态机、字段规范
- 💾 **原子化状态更新** — 备份 + 原子写入 + 校验 + 自动回滚
- 🌐 **中英双语** — 所有提示词、模板、输出支持中英文

---

## 安装（2 分钟）

### 第一步：找到 skills 目录

```bash
# 项目级（推荐）
your-project/.claude/skills/rpd/

# 全局级（所有项目可用）
~/.claude/skills/rpd/
```

### 第二步：复制文件

```bash
# 从本仓库复制
cp -r skills/rpd /your/project/.claude/skills/rpd
```

### 第三步：验证

在 Claude Code 中说：
```
我想做一个记账 App
```

如果 Claude 问"目标用户是谁？" → ✅ 插件已激活。
如果 Claude 直接开始写代码 → ❌ 未安装成功，检查路径。

---

## 三个入口

```
┌─────────────────────────────────────────────────┐
│              项目生命周期                          │
│                                                   │
│   💡 新想法       🔧 半成品      ⏸️ 停滞         │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  ┌────────┐      ┌──────────┐      ┌──────────┐  │
│  │ 流程 A │      │ 流程 B   │      │ 流程 C   │  │
│  │ 新项目 │      │ 接手     │      │ 继续开发 │  │
│  └────────┘      └──────────┘      └──────────┘  │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  PRD + 状态        扫描 + PRD       差距分析       │
│   文件             文件             + 行动计划     │
└─────────────────────────────────────────────────┘
```

### 流程 A：新项目

> **触发词：** "我想做一个……"

**标准模式**（需求明确）：
1. 三视角诊断（用户 → 商业 → 技术），每轮最多 3 个问题
2. 概念版 PRD（≤200 字）→ 用户确认
3. 范围冻结 → 落地版 PRD
4. 生成状态文件

**新手模式**（想法模糊）：
1. `intent-router.py` 检测到模糊输入 → 场景探索模式
2. 3 轮轻松对话（场景 → 痛点 → 期望）
3. 用大白话生成概念版 PRD → 跳过标准诊断

### 流程 B：接手半成品

> **触发词：** "接手这个项目"

1. 安全扫描（发现密钥则硬阻断）
2. 项目扫描（技术栈、组件、API 路由）
3. 确认推断 → 生成 PRD + 状态文件

### 流程 C：继续开发

> **触发词：** "继续开发"

1. 安全扫描 + 状态校验
2. 差距分析（PRD vs 实际代码 + 决策漂移）
3. 行动计划 + 下一步

**回顾模式**（停顿 >3 天）：输出 PRD 摘要 + 功能状态，询问"继续还是修改？"

---

## 脚本工具箱

8 个 Python 脚本，**零依赖，纯标准库**：

| 脚本 | 用途 | 自动触发时机 |
|------|------|-------------|
| `intent-router.py` | 确定性意图分类 | 每次对话开始 |
| `security-scanner.py` | 8 条 SEC 规则 + 路径遍历 + 提示词注入 | 流程 B/C 开始 |
| `project-scanner.py` | 技术栈、组件、API 路由 | 流程 B |
| `gap-analyzer.py` | PRD vs 代码差距 + 决策漂移检测 | 流程 C |
| `state-validator.py` | 状态文件 JSON Schema 校验 | 状态变更后 |
| `state-guard.py` | 备份 + 原子写入 + Git 并发检查 | 状态更新前 |
| `prd-validator.py` | PRD 完整性（错误处理、状态机） | PRD 生成后 |
| `run-eval.py` | 11 个评估场景 | 开发/测试 |

> **你不需要手动运行。** Claude 会在对应流程中自动调用。

---

## 硬性红线

以下规则在执行过程中**绝对不可违反**：

| # | 规则 | 强制执行方式 |
|---|------|-------------|
| 1 | 安全扫描不可跳过 | exit code 2 硬阻断 |
| 2 | 状态校验不可跳过 | exit code 3 回滚 |
| 3 | 每轮最多 3 个问题 | 文本约束 |
| 4 | 不可跳过概念版 PRD | 文本约束 |
| 5 | 不可无备份覆盖 | `state-guard.py` |
| 6 | 不可路径遍历 | `verify_path_safety()` |

---

## 状态文件：项目的大脑

`.project-state.md` 记录了 AI 恢复工作所需的一切：

```markdown
---
name: my-app
state_revision: 3
---

## 功能进度清单
| 功能 | 子任务 | 优先级 | 状态 | 备注 |
|------|--------|--------|------|------|
| 用户登录 | 表单提交 | P0 | ✅ 已完成 | |
| 用户登录 | OAuth对接 | P0 | 🔨 进行中 | 70% |

## 关键决策记录
| 日期 | 类型 | 决策 | 原因 | 影响范围 |
|------|------|------|------|----------|
| 06-03 | 技术选型 | 用SQLite | 单机部署 | 数据层全局 |

## 诊断记录
| 轮次 | 视角 | 问题 | 用户回答摘要 |
|------|------|------|-------------|
| R1 | 用户 | 目标用户是谁？ | 独立开发者 |
```

---

## 速查表

| 你说的 | RPD 做的 |
|--------|----------|
| "我想做一个……" | 流程 A：新项目 |
| "接手这个项目" | 流程 B：接手半成品 |
| "继续开发" | 流程 C：继续开发 |
| "快一点" / "简单点" | Turbo 模式（最小输出） |
| "回顾" / "之前做了什么" | 回顾模式 |

---

## 常见问题

### 需要记住所有触发词吗？
不需要，说人话就行。`intent-router.py` 会确定性地分类你的意图。

### Token 不够了怎么办？
Turbo 模式激活：跳过概念版 PRD，最小输出格式，安全扫描仍然执行（不消耗 token）。

### 可以中途修改 PRD 吗？
可以。修改核心功能需要重新冻结范围。概念版 PRD 修改 >3 次 → 建议先做用户调研。

### 状态文件冲突了怎么办？
`state-guard.py` 在写入前检查 Git 并发。如果检测到冲突（UU），会以 exit code 4 阻断。

---

<p align="center">
  <strong>RPD 不是万能的。它不能帮你做产品决策、写代码、融资。</strong>
  <br />
  <strong>它能做的是：让项目有记忆、方向不跑偏、Token 不浪费。</strong>
  <br /><br />
  <strong>RPD is not omnipotent. It can't make product decisions, write code, or raise funding.</strong>
  <br />
  <strong>What it can do: give your project memory, keep direction on track, save your tokens.</strong>
</p>
