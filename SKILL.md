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

Route based on user intent / 根据用户意图分发：

| Intent (EN) | Intent (ZH) | Route to |
|-------------|-------------|----------|
| "new idea", "I want to build...", "I have an idea" | "新想法"、"我想做一个"、"有个点子" | **Flow A: New Project** |
| "take over", "analyze project", "half-finished" | "接手"、"分析项目"、"这个项目做到一半" | **Flow B: Takeover** |
| "continue development", "what's next", "keep going" | "继续开发"、"下一步"、"接着做" | **Flow C: Continue** |
| Unclear / 不确定 | → Ask: "What would you like to do? A) Start a new project B) Take over an existing project C) Continue previous development" | |

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

**Important: For beginners, first ask "Will users use this on mobile or desktop?" before asking about specific platforms.**
**重要：对小白用户，先问"用户主要在手机上用还是电脑上用？"，再细分平台。**

| English | 中文 |
|---------|------|
| What device will users primarily use? (mobile / desktop / both) → then refine: web app / mobile app / mini-program | 用户主要在什么设备上用？（手机 / 电脑 / 都要）→ 细分 |
| Do you need user accounts and login? | 是否需要用户账号和登录体系？ |
| Where is data stored? (local / cloud) | 数据存在哪里？（本地 / 云端） |
| Any third-party services? (maps, payments, AI, etc.) | 是否需要连接其他服务？（地图、支付、AI 等） |
| How many main pages? | 产品预计有几个主要页面？ |
| How many weeks to build this version? | 这个版本预期几周内可以做出来？ |

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
Core User: [one sentence]
One Problem to Solve: [one specific pain point]
Product Form: [platform]
MVP Features (≤ 3):
  1. [Feature 1]
  2. [Feature 2]
  3. [Feature 3]
Out of Scope: [explicitly excluded features]
Business Model: [pricing or free]
Technical Prerequisites: [auth / data / third-party deps]
```

**中文：**
```
核心用户：[一句话描述目标用户]
要解决的一件事：[一个具体痛点]
产品形态：[平台]
最小可用版功能（≤ 3 条）：
  1. [功能一]
  2. [功能二]
  3. [功能三]
本版本不做：[明确排除的功能]
商业模式：[收费方式 或 免费]
技术前提：[账号体系 / 数据方案 / 第三方依赖]
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

#### A5: Generate State File / 生成状态文件

Generate `.project-state.md` following `references/state-file-spec.md`.

Run validation:
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

## Failure Modes / 故障处理

| EN | ZH | Handling |
|----|-----|----------|
| Empty project | 空项目 | Prompt: "Use 'new project' flow" / 提示"请使用「新建项目」流程" |
| Corrupted state file | 状态文件损坏 | Try to fix, else prompt to regenerate / 尝试修复，失败则提示重新生成 |
| State version too high | 状态文件版本过高 | Prompt: "State file version incompatible, update RPD Skill" |
| Scan timeout | 扫描超时 | Degrade to manual tech stack questions / 降级为手动询问技术栈 |
| Empty feature list | 功能清单为空 | Prompt: "Complete requirement alignment first" / 提示"请先完成需求对齐" |

---

## Escalation / 熔断边界

| EN | ZH | Handling |
|----|-----|----------|
| Concept PRD revised >3 times | 概念版 PRD 修改 >3 次 | Suggest user research first / 建议先做用户调研 |
| Code contains hardcoded secrets | 代码含硬编码密钥 | Hard block, do not continue / 硬阻断，不继续 |
| State file severely inconsistent with code | 状态文件与代码严重不一致 | Ask user which is correct / 提示用户确认 |
| User rejects suggestions 3 times in a row | 用户连续 3 次否定建议 | Re-align requirements / 重新对齐需求 |
