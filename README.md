# RPD — Rapid Product Document

> A Claude Code skill covering the full project lifecycle. Supports Chinese (中文) and English.
> 覆盖项目全生命周期的 Claude Code Skill，支持中英文。

**Inspiration / 灵感来源：** [FlowUs RPD Skill](https://flowus.cn/panix/share/9258e8aa-7a06-4b8d-9817-b7c6d1a0724d)

---

## What Problem Does This Solve? / 解决什么问题？

Three fatal breakpoints in the Vibecoding era / Vibecoding 时代的三大死法：

| Breakpoint / 死法 | Symptom / 症状 | RPD's Solution / 解药 |
|-------------------|----------------|----------------------|
| **Requirement Fracture / 需求断裂** | "I want to build an App" → 3 days later, direction is wrong | Three-perspective diagnosis → Concept PRD → Scope freeze |
| **Context Fracture / 上下文断裂** | Switch AI conversation, it knows nothing about your project | `.project-state.md` state file, cross-session memory |
| **Time Fracture / 时间断裂** | Come back after 2 weeks, forgot why chose SQLite | Key decision records + gap analysis |

**In one sentence: RPD gives your project "memory" so it doesn't get amnesia every new conversation.**
**一句话：RPD 让你的项目有"记忆"，不会每次开新对话就失忆。**

---

## Installation / 安装（2 minutes / 2 分钟搞定）

### Find Your Skills Directory / 找到 skills 目录

```
# Option A: Project-level (only for current project / 项目级)
your-project/.claude/skills/rpd/

# Option B: Global (available for all projects / 全局级)
~/.claude/skills/rpd/
```

### Copy Files / 复制文件

```bash
# Project-level / 项目级安装：
cp -r skills/rpd /your/project/path/.claude/skills/rpd

# Global / 全局安装：
cp -r skills/rpd ~/.claude/skills/rpd
```

### Verify / 验证安装

Say this in Claude Code / 在 Claude Code 中说：

```
> I want to build a personal finance tracker
> 我想做一个记账 App
```

If Claude asks "Who is the target user?" → Skill is active.
If Claude starts writing code immediately → Skill not installed correctly, check path.

---

## Three Entry Points / 三个入口

```
┌─────────────────────────────────────────────────┐
│              Project Lifecycle / 项目生命周期      │
│                                                   │
│   💡 New Idea       🔧 Half-done      ⏸️ Paused   │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  ┌────────┐      ┌──────────┐      ┌──────────┐  │
│  │ New    │      │ Takeover │      │ Continue │  │
│  │ Project│      │          │      │ Dev      │  │
│  │ Flow A │      │ Flow B   │      │ Flow C   │  │
│  └────────┘      └──────────┘      └──────────┘  │
│      │                 │                 │        │
│      ▼                 ▼                 ▼        │
│  PRD + State       PRD + State       Action Plan  │
│   File              File                           │
└─────────────────────────────────────────────────┘
```

---

## Flow A: New Project / 新项目

> **Trigger / 触发词:** "I want to build..." / "我想做一个……"

### Example Conversation / 完整对话示例

**You:** `I want to build a personal finance tracker to track daily expenses`
**你：** `我想做一个记账 App，帮我追踪每天的花销`

**Claude:**
```
I understand you want to build a personal finance tool to track daily expenses.
I'll ask a few rounds of questions to align requirements. This will take about 2 minutes.

Round 1 (User Perspective):
1. Who is the target user? (yourself? or a group?)
2. How do you currently track expenses? (Excel? memory? another app?)
3. What's the ONE core thing this app needs to solve?

「Round 1, 2 rounds remaining」
```

*(Conversation continues with 3 rounds, then concept PRD, scope freeze, full PRD, state file)*

### Key Rules / 关键规则

| EN | ZH |
|----|-----|
| Claude won't output PRD on the first message | 不会在第 1 句话就输出 PRD |
| Max 3 questions per round | 每轮最多 3 个问题 |
| Must freeze scope before full PRD | 必须冻结范围后才能出落地版 |
| Concept PRD ≤ 200 words | 概念版 ≤ 200 字 |

---

## Flow B: Takeover Half-Finished / 接手半成品

> **Trigger / 触发词:** "Take over this project" / "接手这个项目"

**You:** `Take over this project, analyze current progress`
**你：** `接手这个项目，分析一下当前进度`

**Claude:** *(Runs security scan → project scan → confirm inference → generate PRD + state file)*

> ⚠️ **If hardcoded secrets are found, the flow will hard-block.** This is not a suggestion—it's a hard stop. Fix security issues first.
> ⚠️ **如果发现硬编码密钥，流程会直接硬阻断。** 这不是建议，是强制停止。先处理安全问题。

---

## Flow C: Continue Development / 继续开发

> **Trigger / 触发词:** "Continue development" / "继续开发"

**You:** `Continue development`
**你：** `继续开发`

**Claude:**
```
Current progress: 1/3 features completed (33%)

Next step: Complete the pagination logic for "expense categories",
as it's a prerequisite for the monthly report.

Blocker: Report export format (CSV vs Excel) not yet confirmed.
Suggest confirming format before building the report feature.

Estimate: ~2-3 hours to complete expense categories.

Shall we start?
```

---

## State File: The Project's Brain / 状态文件：项目的"大脑"

`.project-state.md` is the heart of RPD. It records:
- PRD summary (core features, exclusions, business model)
- Feature progress checklist (completion status of each feature)
- Key decision records (avoid re-discussing decided topics)
- Current blockers (unresolved issues)

When switching agents, the new agent reads this file to restore context in 30 seconds.

| Scenario / 场景 | Without State File / 没有 | With State File / 有 |
|-----------------|--------------------------|---------------------|
| Switch AI conversation | "Who are you? Start from scratch" | Read state file, 30s context recovery |
| Come back after 2 weeks | "Where was I?" | Check feature progress checklist |
| Take over someone's project | Read 1000 lines of code | Scan → generate state file → clear overview |

---

## Scripts / 脚本工具箱

4 Python scripts, **zero dependencies, stdlib only** / 4 个 Python 脚本，**零依赖，纯标准库**：

| Script / 脚本 | Purpose / 用途 | When Used / 何时用 |
|---------------|----------------|-------------------|
| `project-scanner.py` | Scan project structure, tech stack, components, API | Auto-run on takeover / 接手半成品时自动运行 |
| `gap-analyzer.py` | Compare PRD vs actual code | Auto-run on continue dev / 继续开发时自动运行 |
| `state-validator.py` | Validate state file format | Auto-run after state changes / 状态变更后自动运行 |
| `security-scanner.py` | Detect hardcoded secrets and injection | Auto-run before takeover/continue / 接手和继续前自动运行 |

> **You don't need to run these manually.** Claude calls them automatically in the corresponding flows.
> **你不需要手动运行。** Claude 会在对应流程中自动调用。

```bash
# Validate state file / 校验状态文件
python scripts/state-validator.py .project-state.md

# Scan project / 扫描项目
python scripts/project-scanner.py /your/project/path

# Security scan / 安全扫描
python scripts/security-scanner.py /your/project/path

# Run eval tests / 运行评估测试
python scripts/run-eval.py
```

---

## FAQ / 常见问题

### Do I need to memorize all trigger words? / 需要记住所有触发词吗？

No. Just speak naturally / 不需要，说人话就行：

| You Say / 你说的 | RPD Understands / RPD 理解为 |
|------------------|------------------------------|
| "I want to build..." / "我想做一个……" | New project / 新项目 |
| "I have an idea..." / "有个点子……" | New project / 新项目 |
| "Take over this project" / "接手这个项目" | Takeover / 半成品 |
| "Analyze this project" / "分析一下这个项目" | Takeover / 半成品 |
| "Continue development" / "继续开发" | Continue / 继续开发 |
| "What's next?" / "下一步做什么" | Continue / 继续开发 |

### Concept PRD vs Full PRD? / 概念版和落地版的区别？

| | Concept PRD / 概念版 | Full PRD / 落地版 |
|--|---------------------|-------------------|
| Length / 字数 | ≤ 200 words | Thousands of words / 数千字 |
| Content / 内容 | Core definition + feature list | Full specs + state machines + field validation |
| Purpose / 用途 | Quick alignment / 快速对齐 | Guide development / 指导开发 |
| Token cost | Very low / 极低 | Higher / 较高 |

### What if state file conflicts? / 状态文件冲突了怎么办？

1. Before updating: `git diff .project-state.md` to check conflicts
2. If unmerged changes exist, merge first then update
3. Never blindly overwrite another agent's progress

### What if I run out of tokens? / Token 不够了怎么办？

| When Token Tight / Token 紧张时 | Degrade To / 降级方案 |
|-------------------------------|---------------------|
| Concept PRD | Always output (low cost) / 始终输出 |
| Full PRD | Only feature list + page structure / 只输出功能列表 + 页面结构 |
| Continue Dev | Only progress summary + next step / 只输出进度摘要 + 下一步 |
| Security Scan | Always execute (no LLM tokens) / 始终执行（不消耗 token） |

### Can I modify PRD mid-project? / 可以中途修改 PRD 吗？

Yes, but:
- Concept PRD revised >3 times → Claude suggests user research first
- Changing core features → need to re-freeze scope
- Changing "out of scope" → need to re-evaluate technical feasibility

---

## Quick Reference / 工作流速查表

```
┌──────────────────────────────────────────────────────────┐
│              RPD Workflow Quick Reference                  │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  📌 New Project / 新项目                                    │
│  You say → "I want to build [description]"                 │
│  Claude → 3 rounds → Concept PRD → Freeze → Full PRD       │
│  Output → .project-state.md                                │
│                                                            │
│  📌 Takeover / 接手半成品                                    │
│  You say → "Take over this project"                        │
│  Claude → Security scan → Project scan → Confirm → PRD     │
│  Output → .project-state.md                                │
│                                                            │
│  📌 Continue Dev / 继续开发                                  │
│  You say → "Continue development"                          │
│  Claude → Security → Validate → Gap analysis → Action plan │
│  Output → Progress summary + next step                     │
│                                                            │
│  📌 Dev Complete / 开发完成                                   │
│  Claude reminds → "Update state file?"                     │
│  You say → "Update" / "更新"                                │
│  Claude → Update .project-state.md                         │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## Best Practices / 使用建议

| EN | ZH |
|----|-----|
| Don't skip scope freeze | 不要跳过范围冻结 |
| Don't ignore security scan | 不要忽略安全扫描 |
| Don't manually edit `.project-state.md` | 不要手动编辑 `.project-state.md` |
| Concept PRD is your anchor | 概念版 PRD 是你的锚点 |
| "Continue development" is your most-used entry | "继续开发"是你最常用的入口 |

> **RPD is not omnipotent. It can't make product decisions, write code, or raise funding for you.**
>
> **What it can do: give your project memory, keep your direction on track, save your tokens.**
>
> **RPD 不是万能的。它不能帮你做产品决策、写代码、融资。**
>
> **它能做的是：让项目有记忆、方向不跑偏、Token 不浪费。**

---

## Directory Structure / 目录结构

```
skills/rpd/
├── .claude-plugin/           # Plugin configuration
│   ├── plugin.json           # Plugin metadata
│   └── marketplace.json      # Marketplace listing
├── SKILL.md                  # Main control file (bilingual)
├── README.md                 # This file (bilingual)
├── scripts/                  # Deterministic scripts (Python stdlib)
│   ├── project-scanner.py    # Scan project structure
│   ├── gap-analyzer.py       # Gap analysis
│   ├── state-validator.py    # State file validation
│   ├── security-scanner.py   # Security scanning
│   └── run-eval.py           # Evaluation tests
├── references/               # Knowledge base
│   ├── brainstorming-flow.md # Brainstorming process
│   ├── prd-template.md       # PRD template
│   ├── state-file-spec.md    # State file spec
│   └── state-schema.json     # JSON Schema
├── eval/scenarios/           # Evaluation scenarios
└── assets/example-state.md   # Example state file
```
