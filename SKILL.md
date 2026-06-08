---
name: rpd
description: "Use when: user describes a new product idea, asks to take over an existing project, or says 'continue development'. Covers: requirement diagnosis, PRD generation, project state management, and cross-session progress recovery. Supports Chinese (中文) and English."
description_zh: "当用户描述新产品想法、接手已有项目或说「继续开发」时使用。覆盖：需求诊断、PRD 生成、项目状态管理、跨会话进度恢复。支持中英文。"
context: fork
languages: ["en", "zh"]
---

# RPD — Rapid Product Document

> A structured product management skill covering the full project lifecycle.
> 覆盖项目全生命周期的结构化产品管理 Skill。

---

## Language Detection / 语言检测

**Detect the user's language from their first message and respond in the same language throughout the entire session.**

- If the user writes in Chinese (中文) → respond in Chinese
- If the user writes in English → respond in English
- If unclear → default to Chinese, but ask: "你希望用中文还是英文？ / Would you prefer Chinese or English?"

All prompts, questions, and outputs should use the detected language. The `.project-state.md` file content follows the user's language.

---

## Hard Constraints / 硬性红线

**The following rules are absolutely不可违反 throughout the entire Skill execution:**
**以下规则在整个 Skill 执行过程中绝对不可违反：**

1. **Security scan不可跳过 / 安全扫描不可跳过**：每次 Flow B（接手）和 Flow C（继续）开始时，必须先运行 `security-scanner.py`。If exit code 2, must hard block / 如果 exit code 2，必须硬阻断，不可降级。
2. **State validation不可跳过 / 状态校验不可跳过**：每次更新 `.project-state.md` 后，必须运行 `state-validator.py`。校验失败必须回滚。
3. **Max 3 questions per round / 每轮问题不超过 3 个**：诊断过程中，每轮最多问 3 个问题，等用户回答后再继续。
4. **Don't skip concept PRD / 不跳过概念版 PRD**：标准模式下，必须先输出概念版 PRD 并获得用户确认，再出落地版。
5. **Don't overwrite without backup / 不覆盖未备份的文件**：写入 `.project-state.md` 前，必须先运行 `state-guard.py --action backup`。
6. **No path traversal / 路径不越界**：所有文件操作必须在当前项目目录内，禁止 `../` 路径遍历。

---

## When to Use / 何时使用

**Positive matches / 正向匹配：**

| English | 中文 |
|---------|------|
| User describes a new product idea or feature request | 用户描述新产品想法或功能需求 |
| "I want to build..." / "I have an idea..." | "我想做一个..."、"有个点子..." |
| "Take over this project" / "Analyze this project" | "接手这个项目"、"分析一下这个项目" |
| "Continue development" / "What's next?" | "继续开发"、"下一步做什么"、"接着做" |
| "Update progress" / "Sync status" | "更新进度"、"同步状态" |

**Negative matches / 反向排除（不使用本 Skill）：**

- User is just writing code or debugging, no product direction questions
- User is doing pure technical discussion (architecture, performance, etc.)
- Project already has complete requirements docs and user has no direction confusion
- 用户只是在写代码或调试，没有产品方向的问题
- 用户在做纯技术讨论（架构选型、性能优化等）
- 项目已有完善的需求文档且用户没有方向困惑

---

## Inputs Required / 所需输入

- User's natural language description (product idea, takeover intent, or continue development intent)
- Current working directory (for scanning project files)
- 用户的自然语言描述（产品想法、接手意图、或继续开发意图）
- 当前工作目录（用于扫描项目文件）

---

## Procedure / 流程

### Step 0: Intent Router / 意图路由

**Deterministic routing (must execute) / 确定性路由（必须执行）**：

Before any other action, run / 在做任何其他事情之前，先运行：
```bash
python scripts/intent-router.py "用户输入的原文"
```

Route based on `recommended_flow` field / 根据输出的 `recommended_flow` 字段决定走哪条路：

| recommended_flow | Action / 动作 |
|------------------|---------------|
| scene_exploration | Enter Scene Exploration Mode (see below) / 进入场景探索模式 |
| warm_start | Warm start: ask 1 core question then re-assess / 暖启动：问 1 个核心问题后重新判断 |
| standard_diagnosis | Standard 3-round diagnosis / 标准三轮诊断 |
| flow_b | Take over half-finished / 接手半成品 |
| flow_c | Continue development / 继续开发 |
| ask_user | Uncertain, ask user / 不确定，主动问用户 |

#### Warm Start Layer / 暖启动层

**Trigger Word Expansion / 触发词扩展表**

| User says (EN) | User says (ZH) | RPD understands as |
|----------------|----------------|---------------------|
| "Help me make something" | "帮我做个东西" | New project (warm start) |
| "I have an idea" | "我有个想法" | New project (warm start) |
| "Um... just..." | "那个...就是..." | New project (warm start, proactively guide) |
| "Help me sort through this" | "帮我理一下" | Take over half-finished |
| "Halfway done" | "做到一半了" | Take over half-finished |
| "Continue from here" | "接着来" | Continue development |

**Warm Start Flow / 暖启动流程**

1. **Confirm with a friendly question / 用一句通俗话确认**:
   - EN: "You want to start something from scratch, right?"
   - ZH: "你是想从零开始做一个新东西，对吧？"

2. **First round: only ask 1 core question / 第一轮只问 1 个最核心的问题**:
   - EN: "Who is this for? Yourself or others?"
   - ZH: "你这个东西是给谁用的？自己用还是给别人用？"

3. **Assess user maturity based on answer / 根据回答判断用户成熟度**:
   - **Vague answer (e.g., "just... tracking expenses") / 回答模糊（"就是...记个账"）→ 降级为"场景探索模式"**, use everyday language to guide / 用生活化语言引导
   - **Clear answer (e.g., "A budgeting tool for indie developers") / 回答清晰（"给独立开发者用的记账工具"）→ 进入标准三轮诊断**

**Core Principle / 核心原则**: Talk about scenarios first, then people, then tech. Don't start with jargon like "target user" or "business model". / 先聊场景，再聊人，最后聊技术。不要一上来就甩"目标用户"、"商业模式"这些术语。

#### Scene Exploration Mode / 场景探索模式

**Trigger / 触发条件**: `intent-router.py` returns `maturity: vague` / 返回 `maturity: vague`

**Goal / 目标**: Use 3 rounds of casual conversation to help beginners turn vague ideas into concrete scenarios.
用 3 轮生活化对话，帮小白把模糊想法变成具体场景。

**Round 1: Talk about scenarios / 第 1 轮：聊场景**（问 2 个）
- EN: "When do you usually think about [doing this]?" / "What do you currently use to [solve this problem]?"
- ZH: "你平时什么时候会想 [做这件事]？" / "现在用什么方式 [解决这个问题]？"

**Round 2: Talk about pain points / 第 2 轮：聊痛点**（问 2 个）
- EN: "What annoys you most about [current solution]?" / "Is there something you want but don't have?"
- ZH: "现在 [这个方式] 最烦的是什么？" / "有没有什么想要但现在没有的？"

**Round 3: Talk about expectations / 第 3 轮：聊期望**（问 1 个）
- EN: "If something could help you [solve this], what's the ONE thing you'd want it to do?"
- ZH: "如果有一个东西能帮你 [解决这个问题]，你最希望它能做什么？一句话说。"

**After completion / 完成后**:
AI summarizes the scenario in its own words and asks: "I understand, you want to make a [summary], right?"
AI 用自己的话总结场景，问"我理解了，你是想做一个 [总结]，对吧？"

**After user confirms / 用户确认后**:
Output concept PRD in plain language (no template jargon), skip standard 3-round diagnosis.
直接输出概念版 PRD（人话版，不用模板术语），跳过标准三轮诊断。

#### Intent Routing / 意图分发

Route based on user intent / 根据用户意图分发：

| Intent (EN) | Intent (ZH) | Route to |
|-------------|-------------|----------|
| "new idea", "I want to build...", "I have an idea" | "新想法"、"我想做一个"、"有个点子" | **Flow A: New Project** |
| "take over", "analyze project", "half-finished" | "接手"、"分析项目"、"这个项目做到一半" | **Flow B: Takeover** |
| "continue development", "what's next", "keep going" | "继续开发"、"下一步"、"接着做" | **Flow C: Continue** |
| Unclear / 不确定 | → Ask: "What would you like to do? A) Start a new project B) Take over an existing project C) Continue previous development" | |

**Shortcut Commands / 快捷命令**

| Command | Action |
|---------|--------|
| `/rpd new` | New project flow |
| `/rpd take` | Take over half-finished project flow |
| `/rpd cont` | Continue development |
| `/rpd status` | Show current project status summary |
| `/rpd scan` | Run security scan + project scan only, don't enter flow |

---

### Flow A: New Project / 新项目

> From idea to PRD with structured diagnosis.
> 从想法到 PRD 的结构化转化。

#### A1: Three-Perspective Diagnosis / 三视角诊断

Restate your understanding of the core need, then tell the user:
> "I'll ask a few rounds of questions to align requirements. This will take about 3 minutes."
> "接下来我会通过几轮提问对齐需求，总共大约需要 3 分钟。"

**Round 1 (User Perspective / 用户视角) — pick 2-3:**

| English | 中文 |
|---------|------|
| Who is the target user? (age, occupation, scenario) | 目标用户是谁？（年龄段、职业背景、使用场景） |
| How do they currently solve this problem? | 他们现在用什么方式解决这个问题？ |
| What ONE specific thing does your product help with? | 你的产品帮他解决的是哪**一件**具体的事？ |
| How often will they use it? (daily / weekly / occasionally) | 这个场景下用户会多久用一次？ |

After questions: "Round 1, 2 rounds remaining" / 「第 1 轮，还剩 2 轮」

**Round 2 (Business Perspective / 商业视角) — ask all:**

| English | 中文 |
|---------|------|
| Is this free or paid? | 这是免费产品，还是用户要付费使用？ |
| If paid, what model: one-time / subscription / freemium? | 如果收费，模式是哪种：一次性买断 / 订阅 / 免费增值？ |
| How long do you plan to work on this? (validation / long-term) | 预期把这个产品做多久？（验证型项目 / 长期运营） |

After questions: "Round 2, 1 round remaining" / 「第 2 轮，还剩 1 轮」

**Round 3 (Technical Perspective / 技术视角) — ask all:**

| English | 中文 |
|---------|------|
| Where is data stored? (on user's phone / server / cloud) | 数据存在哪里？（自己手机 / 服务器 / 云端） |
| Do you need user registration and login? (yes / no) | 需要用户注册登录吗？（是 / 否） |
| How long do you plan to build this version? (days / weeks / months) | 这个版本大概要做多久？（几天 / 几周 / 几个月） |

After questions: "Round 3, 1 round remaining" / 「第 3 轮，还剩 1 轮」

**Round 4 (Security Perspective / 安全视角) — ask all:**

| English | 中文 |
|---------|------|
| Does it involve user registration and login? → Account security needed | 是否涉及用户注册和登录？→ 需要考虑账户安全 |
| Does it have user-generated content (comments, posts, avatars)? → Content moderation needed | 是否有用户发布内容的功能（评论、帖子、头像等）？→ 需要内容审核 |
| Does it have file upload? → File security measures needed | 是否有文件上传功能？→ 需要文件安全措施 |
| Does it use AI/LLM features? → Prompt protection needed | 是否使用 AI/大模型功能？→ 需要 Prompt 保护 |
| Does it involve payments or sensitive data? → Encryption and compliance needed | 是否涉及支付或敏感数据？→ 需要数据加密和合规 |
| Expected user scale? → Affects security investment priority | 预期用户规模？→ 影响安全投入的优先级 |

After questions: "Round 4 (Security), last question!" / 「第 4 轮（安全），最后一个问题了！」

**Beginner Mode / 小白模式**（当 intent-router 返回 maturity: vague 或 scene_exploration 时）：

安全视角由 AI 根据前几轮回答**自动判断**，不询问用户。
Security perspective is auto-determined by AI based on previous answers, without asking the user.

| If previous rounds mentioned... / 如果前几轮提到... | Auto-add / 自动加入 |
|---------------------------------------------------|---------------------|
| "login"/"register"/"account" / "登录"/"注册"/"账号" | Account security / 账户安全 |
| "comment"/"post"/"avatar"/"UGC" / "评论"/"发帖"/"头像" | Content moderation / 内容审核 |
| "upload"/"attachment"/"image" / "上传"/"附件"/"图片" | File security / 文件安全 |
| "AI"/"smart"/"bot" / "AI"/"智能"/"机器人" | Prompt protection / Prompt 保护 |
| "payment"/"money"/"bank" / "支付"/"钱"/"银行卡" | Encryption & compliance / 加密合规 |
| None of the above / 以上都没有 | Skip security perspective / 跳过安全视角 |

In concept PRD, add one line at the end / 在概念版 PRD 末尾一句话带过：
> Security considerations: [auto-filled items] / 安全考虑：[自动填入的项]

**Rules / 规则：**
- Max 3 questions per round, wait for answers before continuing
- Show progress after each round
- Use simple language for beginners, avoid jargon
- Do NOT output a full PRD at this stage
- 每轮最多 3 个问题，等待回答后再继续
- 每轮结束后显示进度
- 对小白用户使用通俗语言
- 此阶段禁止输出完整 PRD

#### A2: Concept PRD / 概念版 PRD

After diagnosis, output concept PRD (≤ 200 words):

**English:**
```
Who it's for: [one sentence]
Problem to solve: [one specific pain point]
How it works: [Web / App / Mini-program / CLI]
Tech requirements: [auth / data / third-party deps]
MVP Features (≤ 3):
  1. [Feature 1]
  2. [Feature 2]
  3. [Feature 3]
Out of Scope: [explicitly excluded features]
Business Model: [pricing or free]
```

**中文：**
```
给谁用的：[一句话描述目标用户]
解决什么问题：[一个具体痛点]
怎么用的：[Web / App / 小程序 / 命令行]
技术上需要什么：[账号体系 / 数据方案 / 第三方依赖]
最小可用版功能（≤ 3 条）：
  1. [功能一]
  2. [功能二]
  3. [功能三]
本版本不做：[明确排除的功能]
商业模式：[收费方式 或 免费]
```

#### Beginner Concept PRD / 小白版概念 PRD

When `intent-router.py` returns `maturity: vague` or `scene_exploration`, use this template:
当 `intent-router.py` 返回 `maturity: vague` 或 `scene_exploration` 时，使用此模板：

```
📱 What you want to make / 你想做的东西：
[One sentence, plain language / 一句话描述，用人话]

✨ Main features (do these 3 first) / 主要功能（先做这 3 个）：
1. [Feature 1, plain language / 功能一，用人话]
2. [Feature 2, plain language / 功能二，用人话]
3. [Feature 3, plain language / 功能三，用人话]

🚫 Not doing this time / 这次不做：
[Exclusions, plain language / 排除项，用人话]

💰 Free or paid / 免费还是收费：
[One sentence / 一句话]

🔧 Technical approach / 技术方案：
[One sentence, no jargon. E.g. "Data stored on your phone, no account needed"]
[一句话，不用术语。例如"数据存在你自己手机里，不需要注册账号"]
```

Then ask: "Is this direction aligned? Any adjustments needed?" / "方向是否对齐？有需要调整的地方吗？"

#### A3: Scope Freeze / 范围冻结

Output freeze checklist:

**English:**
```
Before we proceed to the full PRD, please confirm these won't change:

✅ Target User: [...]
✅ Core Features (≤ 3): [...]
✅ Platform: [...]
✅ Out of Scope: [...]

Please reply "confirmed" to continue.
```

**中文：**
```
在开始落地版之前，请确认以下内容不会再修改：

✅ 目标用户：[...]
✅ 核心功能（≤ 3 条）：[...]
✅ 平台选择：[...]
✅ 本版本不做：[...]

请回复"确认"后继续。
```

#### A4: Full PRD / 落地版 PRD

Refer to `references/prd-template.md` for the full template. Output complete PRD with all sections.

After completion, run the Six Blind Spots checklist (see `references/prd-template.md`).

#### PRD Completeness Check / PRD 完整性校验

After generating the full PRD, **must execute** / 生成落地版 PRD 后，**必须执行**：

```bash
python scripts/prd-validator.py <prd-file> --format text
```

If output shows `FAIL`, supplement missing content based on gaps list, then re-validate. / 如果输出 `FAIL`，根据 gaps 列表补充缺失内容后重新校验。

#### A5: Generate State File / 生成状态文件

Generate `.project-state.md` following `references/state-file-spec.md`.

**Decision Table Format / 决策记录格式**:

The decision table in `.project-state.md` must use 5 columns:
| 日期 | 类型 | 决策 | 原因 | 影响范围 |

**Type values / 类型字段**: 技术选型 / 架构模式 / 安全策略 / 业务逻辑 / 其他

#### State File Protection / 状态文件保护

After generating or updating `.project-state.md`, **must execute** / 生成或更新 `.project-state.md` 后，**必须执行**：

1. Backup (if file already exists) / 备份（如果文件已存在）：
   ```bash
   python scripts/state-guard.py .project-state.md --action backup
   ```

2. Validate / 校验：
   ```bash
   python scripts/state-validator.py .project-state.md
   ```

Output: "Project initialized, state file generated. Say 'continue development' to resume context." / "项目已初始化，状态文件已生成。对我说「继续开发」来恢复上下文。"

---

### Flow B: Takeover Half-Finished Project / 接手半成品

> Analyze existing code, generate PRD and state file.
> 分析已有代码，生成 PRD 和状态文件。

#### B1: Security Scan / 安全扫描

```bash
python scripts/security-scanner.py <project-directory>
```

If exit code 2 → output security report and STOP. / 输出安全报告并停止流程。

#### B2: Project Scan / 项目扫描

```bash
python scripts/project-scanner.py <project-directory>
```

Analyze JSON output for: tech stack, components, API routes, TODOs, stats.

#### B3: Confirm Inference / 推断确认

Based on scan results, confirm with user:

**English:**
1. "I infer this is a [X] product, correct?"
2. "Core features I understand: [list]. Anything missing?"
3. "Out of scope: [list]. Confirmed?"
4. "Tech stack is [X], correct?"

**中文：**
1. "我推断这是一个 [X] 产品，对吗？"
2. "核心功能我理解为这 3 个：[列出]，有遗漏吗？"
3. "本版本不做：[排除项]，确认吗？"
4. "技术栈是 [X]，对吗？"

#### B4: Generate PRD + State File / 生成 PRD + 状态文件

Generate simplified PRD (concept level is sufficient) and `.project-state.md`.

Feature progress auto-marking based on code analysis:
- Has complete implementation → ✅ Completed / ✅ 已完成
- Has partial code → 🔨 In Progress / 🔨 进行中
- No code but in PRD → ⏳ Not Started / ⏳ 未开始

Run validation:
```bash
python scripts/state-validator.py .project-state.md
```

Output: "Project takeover complete, state file generated. Say 'continue development' to start." / "已接手项目，状态文件已生成。对我说「继续开发」开始下一步。"

---

### Flow C: Continue Development / 继续开发

> Cross-agent / cross-time context recovery.
> 跨 agent/跨时间的上下文恢复。

#### C1: Check State File / 检查状态文件

Check if `.project-state.md` exists:
- Not found → "No state file found. Please 'analyze project' or 'new project' first." / "没有找到项目状态文件，请先「分析项目」或「新建项目」"
- Found → continue

**Review Mode / 回顾模式**

When user has been inactive for >3 days, or explicitly says "回顾"/"之前做了什么"/"what did we do"/"review":
当用户超过 3 天未操作，或明确说"回顾"/"之前做了什么"时：

1. Output PRD summary in plain language / 输出 PRD 摘要（用人话）
2. Output feature list with current status / 输出功能清单和当前状态
3. Ask / 问："要继续开发，还是想改改之前的方案？"/ "Continue development, or revise the plan?"
4. If revise → re-enter diagnosis (Flow A1) / 如果改方案 → 重新进入诊断流程（Flow A1）
5. If continue → proceed to C2 / 如果继续 → 进入 C2

#### C2: Security Scan / 安全扫描

```bash
python scripts/security-scanner.py <project-directory> --state-file .project-state.md
```

If exit code 2 → output security report and STOP.

#### C3: State Validation / 状态校验

```bash
python scripts/state-validator.py .project-state.md
```

If validation fails → try to fix or prompt user to regenerate.

#### C4: Gap Analysis / 差距分析

```bash
python scripts/gap-analyzer.py <project-directory> --state-file .project-state.md
```

#### C5: Generate Action Plan / 生成行动建议

Based on gap analysis:

| English | 中文 |
|---------|------|
| Progress: X/Y features completed (Z%) | 当前进度：X/Y 功能已完成（Z%） |
| Next: "Suggest completing [feature] because [reason]" | 下一步建议："建议先完成 [功能]，因为 [原因]" |
| Blocker: "Blocker [X] unresolved, suggest [solution]" | 阻塞提醒："阻塞项 [X] 尚未解决，建议 [方案]" |
| Deviation: "Found [X] deviates from PRD" | 偏离警告："发现 [X] 模块偏离 PRD" |
| Estimate: "Completing next feature takes ~[time]" | 预估工作量："完成下一个功能预计需要 [时间]" |

#### C6: Post-Development Update / 开发完成后的状态更新

After development completes, remind user:
> "Feature complete. Update project state file? (Updates enable more accurate progress tracking)"
> "功能已完成。要更新项目状态文件吗？（更新后可以更准确地追踪进度）"

Before updating:
1. Check for concurrent modifications: `git diff .project-state.md`
2. If conflicts exist, merge first before updating
3. Update `.project-state.md` with new status and `last-modified-by`
4. Run validation

---

## Token Budget Control / Token 预算控制

When token budget is tight, degrade gracefully:

| Component | EN | ZH |
|-----------|----|----|
| Concept PRD | Always output (low cost, ≤ 200 words) | 始终输出（成本低） |
| Full PRD | Output only feature list + page structure | 只输出功能列表 + 页面结构 |
| Continue Dev | Output only progress summary + next step | 只输出进度摘要 + 下一步建议 |
| Security Scan | Always execute (deterministic script, no LLM tokens) | 始终执行（确定性脚本，不消耗 token） |

### Turbo Mode / 极速模式

**Trigger conditions / 触发条件**:
- User explicitly says "hurry up", "simpler", "don't ask so much" / 用户明确说"快一点"、"简单点"、"别问那么多"
- OR token remaining < 2000 / 或 Token 剩余 < 2000

**Turbo mode behavior / 极速模式行为**:
1. Skip concept PRD, output minimal landing version directly (only feature list + page structure) / 跳过概念版 PRD，直接出精简落地版（只含功能列表 + 页面结构）
2. Skip scope freeze confirmation (assume user has verbally confirmed) / 跳过范围冻结确认（假设用户已口头确认）
3. Continue development only outputs: "Progress X%, next: [specific task], estimate [time]" / 继续开发只输出："进度 X%，下一步：[具体任务]，预估 [时间]"
4. Security scan always executes (no token consumption) / 安全扫描始终执行（不消耗 Token）

**Turbo mode output format / 极速模式输出格式**:
```
📋 [Project Name] Status / [项目名] 状态
- Progress: X/Y (Z%) / 进度：X/Y（Z%）
- Next: [one sentence] / 下一步：[一句话]
- Blocker: [one sentence or None] / 阻塞：[一句话 或 无]
- Estimate: [time] / 预估：[时间]
```

---

## Verification / 验证

After every state file change:
```bash
python scripts/state-validator.py .project-state.md
```

Before every "continue development" and "takeover":
```bash
python scripts/security-scanner.py <project-directory> [--state-file .project-state.md]
```

---

## Script Toolbox / 脚本工具箱

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `project-scanner.py` | Scan project structure, tech stack, components | Flow B (takeover), `/rpd scan` |
| `security-scanner.py` | Detect hardcoded secrets, injection, business security | Flow B, Flow C, `/rpd scan` |
| `state-validator.py` | Validate `.project-state.md` format and fields | After every state file change |
| `gap-analyzer.py` | Compare PRD features vs actual code implementation | Flow C (continue development) |
| `state-guard.py` | Backup and protect state file from corruption | Before updating state file |
| `prd-validator.py` | Check PRD completeness against template | After generating full PRD (A4) |
| `run-eval.py` | Run all evaluation scenarios | Testing RPD Skill itself |

---

## Failure Modes / 故障处理

| EN | ZH | Handling |
|----|-----|----------|
| Empty project | 空项目 | Prompt: "Use 'new project' flow" / 提示"请使用「新建项目」流程" |
| Corrupted state file | 状态文件损坏 | Try to fix, else prompt to regenerate / 尝试修复，失败则提示重新生成 |
| State version too high | 状态文件版本过高 | Prompt: "State file version incompatible, update RPD Skill" |
| Scan timeout | 扫描超时 | Degrade to manual tech stack questions / 降级为手动询问技术栈 |
| Empty feature list | 功能清单为空 | Prompt: "Complete requirement alignment first" / 提示"请先完成需求对齐" |

### Warm Resume Phrases / 温暖续传话术

When resuming development, use warm, natural language instead of mechanical prompts:

恢复开发时，使用温暖自然的语言，而不是机械的提示：

**EN examples:**
- "Last time we were working on [project name], and we've completed [X] features. Want to continue? You can say 'continue' or tell me what you'd like to do next."
- "We've made good progress on [project name] — [X] features done. Ready to pick up where we left off?"

**ZH examples:**
- "上次我们在做 [项目名]，已经完成了 [X] 个功能。要不要继续？你可以说「接着来」或者告诉我下一步想做什么。"
- "[项目名] 进展不错——已完成 [X] 个功能。准备从上次停下的地方继续吗？"

---

## Escalation / 熔断边界

| EN | ZH | Handling |
|----|-----|----------|
| Concept PRD revised >3 times | 概念版 PRD 修改 >3 次 | Suggest user research first / 建议先做用户调研 |
| Code contains hardcoded secrets | 代码含硬编码密钥 | Hard block, do not continue / 硬阻断，不继续 |
| State file severely inconsistent with code | 状态文件与代码严重不一致 | Ask user which is correct / 提示用户确认 |
| User rejects suggestions 3 times in a row | 用户连续 3 次否定建议 | Re-align requirements / 重新对齐需求 |
