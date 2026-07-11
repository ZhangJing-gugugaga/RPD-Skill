---
name: rpd
description: "Use when: user describes a new product idea, asks to take over an existing project, or says 'continue development'. Covers: requirement diagnosis, PRD generation, project state management, and cross-session progress recovery. Supports Chinese (中文) and English."
description_zh: "当用户描述新产品想法、接手已有项目或说「继续开发」时使用。覆盖：需求诊断、PRD 生成、项目状态管理、跨会话进度恢复。支持中英文。"
context: fork
languages: ["en", "zh"]

argument-hint: "new | take | cont | status | scan"
user-invocable: true
allowed-tools: [Read, Write, Glob, Grep, Shell, run_shell_command]
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

## Script Path & Graceful Degradation / 脚本路径与优雅降级

All scripts referenced in this Skill live in the Skill's own directory, NOT the user's project directory:
所有脚本均位于 Skill 自身目录下，而非用户项目目录：

```
~/.qoderworkcn/skills/rpd/scripts/
```

**Resolution rule / 路径解析规则**:
When a procedure says `python scripts/xxx.py`, resolve the path as:
当流程中写 `python scripts/xxx.py` 时，按以下顺序查找：

1. First try: `~/.qoderworkcn/skills/rpd/scripts/xxx.py` (Skill directory / Skill 目录)
2. If not found, check if the user's project has a local `scripts/` directory
3. If neither exists, **degrade gracefully** using the manual fallback table below

**Graceful Degradation Table / 降级对照表**:

| Script | If unavailable, do this manually / 脚本不可用时手动操作 |
|--------|-----------------------------------------------------|
| `intent-router.py` | Read the user's first message, match against the Intent Routing table and Warm Start Trigger Word table in Step 0. Determine `recommended_flow` manually based on keyword matching. / 根据用户首条消息，手动匹配 Step 0 中的意图路由表和暖启动触发词表，判断 `recommended_flow`。 |
| `security-scanner.py` | Skip automated scan. Ask user: "Does this project handle user data, payments, or authentication?" If yes, manually check for hardcoded secrets by grepping for common patterns (API keys, passwords, tokens). If no, proceed without scan. / 跳过自动扫描，手动询问用户项目是否涉及用户数据、支付或认证，必要时手动 grep 检查硬编码密钥。 |
| `project-scanner.py` | Manually scan project: list files with `ls` or `Glob`, read key files (package.json, requirements.txt, README.md, main entry files). Infer tech stack, components, and API routes from file structure. / 手动扫描项目：用 ls 或 Glob 列出文件，读取关键文件（package.json、requirements.txt、README.md、入口文件），推断技术栈和组件。 |
| `state-validator.py` | Read `.project-state.md` manually, check that required fields exist (project name, PRD path, features list, timestamps). If missing fields, note them for the user. / 手动读取 .project-state.md，检查必填字段是否存在，缺失的字段记录给用户。 |
| `gap-analyzer.py` | Compare PRD feature list against actual code files manually. For each PRD feature, search for corresponding implementation files. Mark as ✅/🔨/⏳ based on code completeness. / 手动对比 PRD 功能列表和实际代码文件，按代码完整度标记 ✅/🔨/⏳。 |
| `state-guard.py` | Before writing `.project-state.md`, manually copy the existing file to `.project-state.md.bak` in the same directory. / 写入前手动复制 .project-state.md 为 .project-state.md.bak。 |
| `prd-validator.py` | Manually check PRD against the template in `references/prd-template.md`. Verify all required sections exist (一~十五). Count badcase entries (≥8 required). Check AI role specificity. / 手动对照 references/prd-template.md 检查 PRD，验证章节完整性、badcase 数量和 AI 职责具体性。 |

**Core principle / 核心原则**: Script failures must NEVER terminate the Skill. Always degrade to manual operation and continue the flow.
脚本失败绝不能终止 Skill 流程。必须降级为手动操作并继续执行。

---

## Procedure / 流程

### Step 0: Intent Router / 意图路由

#### Step 0a: Conversation Context Detection / 对话上下文检测

**Before running any script, check the current conversation for existing product context.**
在运行任何脚本之前，先检查当前对话中是否已存在充分的产品讨论。

Scan the conversation history for the following signals / 扫描对话历史，检测以下信号：

| Signal / 信号 | Example / 示例 |
|---------------|----------------|
| Product name discussed / 产品名称已讨论 | "叫 Termify"、"名字是 XXX" |
| Target user identified / 目标用户已明确 | "给程序员用"、"面向独立开发者" |
| Core features listed (≥2) / 核心功能已列出（≥2 个） | "上传 GIF、选风格、下载脚本" |
| Tech stack mentioned / 技术栈已提及 | "用 Flask"、"前端 HTML/CSS" |
| User explicitly asks to write PRD / 用户明确要求写 PRD | "开始写 PRD 吧"、"出 PRD" |

**Decision / 决策**:

- If ≥3 signals found / 检测到 ≥3 个信号 → **Offer Fast Path / 提供快速通道**:
  > "I detected that you've already discussed [product name], [target users], and [core features] in our conversation. I can skip the diagnosis rounds and generate the PRD directly from what we've already discussed. Skip diagnosis? / 检测到你们已经讨论了 [产品名]、[目标用户] 和 [核心功能]。可以跳过诊断，直接基于已有对话生成 PRD。是否跳过？"
  >
  > - User says yes / 用户确认 → Go directly to A-1 (Greenfield Setup) then A2 (Concept PRD) or A4 (Full PRD) based on context depth / 根据上下文深度直接跳到 A2 或 A4
  > - User says no / 用户拒绝 → Continue to Step 0b (normal intent routing) / 继续正常意图路由

- If <3 signals / 信号不足 → Continue to Step 0b (normal intent routing) / 继续正常意图路由

#### Step 0b: Deterministic Routing / 确定性路由

**Deterministic routing (must execute) / 确定性路由（必须执行）**：

Before any other action, run / 在做任何其他事情之前，先运行：
```bash
python ~/.qoderworkcn/skills/rpd/scripts/intent-router.py "用户输入的原文"
```

> **Fallback / 降级**: If `intent-router.py` is not found or fails, manually match the user's input against the Intent Routing table and Warm Start Trigger Word table below to determine `recommended_flow`. / 如果脚本不可用，手动匹配用户输入与下方意图路由表和暖启动触发词表。

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

**Round 3: Talk about basics / 第 3 轮：聊基础**（问 2 个）
- EN: "Where is the data stored? (on your phone / server / cloud)" / "Do users need to register and login?"
- ZH: "数据存在哪里？（自己手机 / 服务器 / 云端）" / "需要用户注册登录吗？（是 / 否）"

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

#### A-1: Greenfield Setup / 从零开始的项目初始化

**Trigger / 触发条件**: The project directory does not exist yet, or the user asks to create a new project folder. / 项目目录尚不存在，或用户要求创建新项目文件夹。

This step handles the "from zero" scenario — the user has a product idea but no project directory, no code, no state file. The skill should NOT fail or terminate in this case; it should seamlessly create the workspace and proceed to PRD generation.
此步骤处理"从零开始"的场景——用户有产品想法但还没有项目目录、没有代码、没有状态文件。Skill 在这种情况下不应失败或终止，而应无缝创建工作空间并继续 PRD 生成。

**Procedure / 流程**:

1. **Confirm project directory / 确认项目目录**:
   - If user specified a directory path → use it / 如果用户指定了路径 → 使用该路径
   - If user only specified a project name → create directory in current working directory / 如果用户只给了项目名 → 在当前工作目录下创建
   - Ask: "Where should I create the project? [suggested path] OK?" / "项目创建在哪里？[建议路径] 可以吗？"

2. **Create project directory / 创建项目目录**:
   ```bash
   mkdir -p <project-directory>
   cd <project-directory>
   git init  # If user wants version control / 如果用户需要版本控制
   ```

3. **Skip security scan / 跳过安全扫描**:
   No code exists yet, so `security-scanner.py` and `project-scanner.py` are not applicable. Note: "New project, no code to scan. Security scan will run after first code is written." / "新项目，没有代码可扫描。安全扫描将在首次写代码后运行。"

4. **Proceed to A0 or A2 / 进入 A0 或 A2**:
   - If coming from Step 0a Fast Path (conversation has rich context) → skip to A2 (Concept PRD) / 如果来自快速通道（对话已有丰富上下文）→ 跳到 A2
   - If normal entry → proceed to A0 (Problem Validation) / 正常进入 → 进入 A0

**Key principle / 关键原则**: For a greenfield project, the PRD comes FIRST, then code. The skill should never block PRD generation on the absence of code or project files.
对于从零开始的项目，PRD 先于代码。Skill 绝不能因为没有代码或项目文件而阻断 PRD 生成。

#### A0: Problem Validation / 问题校验

After user provides their initial product idea, before starting diagnosis:

1. Check input quality against 6 criteria / 检查输入质量，6 项标准：
   - Is target user too broad? ("所有人" = too broad) / 目标用户是否太泛？（"所有人"=太泛）
   - Is core scenario specific enough? / 核心场景是否具体？
   - Is the pain point a real problem, not just a feature idea? / 用户卡点是否是真问题（而非功能想法）？
   - Is the MVP scope too large? / MVP 是否过大？
   - Is the "out of scope" boundary clear? / 本期不做的边界是否清楚？
   - Is the AI role specific, or just "call LLM"? / AI 的角色是否具体（而非只写"调用大模型"）？

2. Output validation table / 输出校验表格：
   | 检查项 | 当前判断 | 存在的问题 | 修改建议 |
   |--------|----------|------------|----------|

3. If issues found, suggest adjustments before proceeding to A1 / 如发现问题，建议调整后再进入 A1
4. If input is insufficient, make reasonable assumptions but mark them with 「假设」/ 信息不足时做合理假设，但必须用「假设」标注

> This step ensures the diagnosis in A1 starts from a well-formed problem statement.
> 此步骤确保 A1 的诊断从结构良好的问题描述开始。

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

**Round 3a (Technical - Infrastructure / 技术 - 基础设施) — ask all:**

| English | 中文 |
|---------|------|
| Where is data stored? (on user's phone / server / cloud) | 数据存在哪里？（自己手机 / 服务器 / 云端） |
| Do you need user registration and login? (yes / no) | 需要用户注册登录吗？（是 / 否） |
| What devices will users primarily use? (mobile / desktop / both) | 用户主要在什么设备上用？（手机 / 电脑 / 都要） |

After questions: "Round 3a, 2 rounds remaining" / 「第 3a 轮，还剩 2 轮」

**Round 3b (Technical - Scope / 技术 - 范围) — ask all:**

| English | 中文 |
|---------|------|
| How many main pages will the product have? | 产品预计有几个主要页面？ |
| How long do you expect this version to take? (weeks) | 这个版本预期几周内可以做出来？ |
| Does it need to connect to other services? (payment, maps, etc.) | 是否需要连接其他服务？（支付、地图等） |

After questions: "Round 3b, 1 round remaining" / 「第 3b 轮，还剩 1 轮」

**Round 4a (Security - Account & Data / 安全 - 账户与数据) — ask all:**

| English | 中文 |
|---------|------|
| Does it involve user registration and login? → Account security needed | 是否涉及用户注册和登录？→ 需要考虑账户安全 |
| Does it have user-generated content (comments, posts, avatars)? → Content moderation needed | 是否有用户发布内容的功能（评论、帖子、头像等）？→ 需要内容审核 |
| Does it have file upload? → File security measures needed | 是否有文件上传功能？→ 需要文件安全措施 |

After questions: "Round 4a (Security), 1 round remaining" / 「第 4a 轮（安全），还剩 1 轮」

**Round 4b (Security - AI & Scale / 安全 - AI 与规模) — ask all:**

| English | 中文 |
|---------|------|
| Does it use AI/LLM features? → Prompt protection needed | 是否使用 AI/大模型功能？→ 需要 Prompt 保护 |
| Does it involve payments or sensitive data? → Encryption and compliance needed | 是否涉及支付或敏感数据？→ 需要数据加密和合规 |
| Expected user scale? → Affects security investment priority | 预期用户规模？→ 影响安全投入的优先级 |

After questions: "Round 4b (Security), last question!" / 「第 4b 轮（安全），最后一个问题了！」

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
Product Name: [name]
Who it's for: [one sentence]
Core Problem: For [who], in [scenario], because [pain point], wants [result].
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
产品名称：[名称]
给谁用的：[一句话描述目标用户]
核心问题：对 [谁]，在 [什么场景] 下，因为 [卡点]，所以希望 [结果]
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

Refer to `references/prd-template.md` for the full template. Output complete PRD with all sections, including AI-enhanced sections (七~十五): problem validation, input design, output design, AI workflow, AI responsibilities, badcase analysis, validation goals, PRD risks, and AI PRD self-check.

**Before writing the PRD to a file, ask the user:**
> "May I write the full PRD to [filename]? / 可以将落地版 PRD 写入 [文件名] 吗？"

Wait for user confirmation before writing any file.

After completion, run the Six Blind Spots checklist (see `references/prd-template.md`).

#### PRD Completeness Check / PRD 完整性校验

After generating the full PRD, **must execute** / 生成落地版 PRD 后，**必须执行**：

```bash
python ~/.qoderworkcn/skills/rpd/scripts/prd-validator.py <prd-file> --format text --ai-mode
```

> **Fallback / 降级**: If script unavailable, manually check PRD against `references/prd-template.md`. Verify sections 一~十五 exist, count badcase entries (≥8), check AI role specificity. / 脚本不可用时，手动对照 `references/prd-template.md` 检查 PRD 章节完整性、badcase 数量和 AI 职责具体性。

The `--ai-mode` flag enables AI PRD section checks (badcase count ≥8, AI role specificity, section presence). / `--ai-mode` 启用 AI PRD 章节检查（badcase 数量≥8、AI 职责具体性、章节存在性）。

If output shows `FAIL`, supplement missing content based on gaps list, then re-validate. / 如果输出 `FAIL`，根据 gaps 列表补充缺失内容后重新校验。

#### A5: Generate State File / 生成状态文件

**Before generating the state file, ask the user:**
> "May I generate the project state file (.project-state.md)? / 可以生成项目状态文件吗？"

Wait for confirmation, then proceed with backup + write + validate.

Generate `.project-state.md` following `references/state-file-spec.md`.

**Decision Table Format / 决策记录格式**:

The decision table in `.project-state.md` must use 5 columns:
| 日期 | 类型 | 决策 | 原因 | 影响范围 |

**Type values / 类型字段**: 技术选型 / 架构模式 / 安全策略 / 业务逻辑 / 其他

#### State File Protection / 状态文件保护

After generating or updating `.project-state.md`, **must execute** / 生成或更新 `.project-state.md` 后，**必须执行**：

1. Backup (if file already exists) / 备份（如果文件已存在）：
   ```bash
   python ~/.qoderworkcn/skills/rpd/scripts/state-guard.py .project-state.md --action backup
   ```
   > **Fallback / 降级**: If script unavailable, manually copy: `cp .project-state.md .project-state.md.bak` / 脚本不可用时手动复制备份。

2. Validate / 校验：
   ```bash
   python ~/.qoderworkcn/skills/rpd/scripts/state-validator.py .project-state.md
   ```
   > **Fallback / 降级**: If script unavailable, manually read `.project-state.md` and verify required fields exist (project name, PRD path, features list, timestamps). / 脚本不可用时手动检查必填字段。

Output: "Project initialized, state file generated. Say 'continue development' to resume context." / "项目已初始化，状态文件已生成。对我说「继续开发」来恢复上下文。"

---

### Flow B: Takeover Half-Finished Project / 接手半成品

> Analyze existing code, generate PRD and state file.
> 分析已有代码，生成 PRD 和状态文件。

#### B1: Security Scan / 安全扫描

```bash
python ~/.qoderworkcn/skills/rpd/scripts/security-scanner.py <project-directory>
```

> **Fallback / 降级**: If script unavailable, ask user if project handles user data, payments, or authentication. If yes, manually grep for hardcoded secrets (API keys, passwords, tokens). If no, proceed without scan. / 脚本不可用时，手动询问用户项目是否涉及敏感数据，必要时手动检查硬编码密钥。

If exit code 2 → output security report and STOP. / 输出安全报告并停止流程。

#### B2: Project Scan / 项目扫描

```bash
python ~/.qoderworkcn/skills/rpd/scripts/project-scanner.py <project-directory>
```

> **Fallback / 降级**: If script unavailable, manually scan project: list files with `ls`/`Glob`, read key files (package.json, requirements.txt, README.md, entry files). Infer tech stack and components from file structure. / 脚本不可用时，手动扫描项目文件结构和关键文件。

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
python ~/.qoderworkcn/skills/rpd/scripts/state-validator.py .project-state.md
```

> **Fallback / 降级**: If script unavailable, manually verify `.project-state.md` has required fields (project name, PRD path, features list, timestamps). / 脚本不可用时手动检查必填字段。

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
python ~/.qoderworkcn/skills/rpd/scripts/security-scanner.py <project-directory> --state-file .project-state.md
```

> **Fallback / 降级**: If script unavailable, ask user about sensitive data handling. Manually grep for hardcoded secrets if needed. / 脚本不可用时手动检查安全风险。

If exit code 2 → output security report and STOP.

#### C3: State Validation / 状态校验

```bash
python ~/.qoderworkcn/skills/rpd/scripts/state-validator.py .project-state.md
```

> **Fallback / 降级**: If script unavailable, manually verify `.project-state.md` required fields. / 脚本不可用时手动校验字段。

If validation fails → try to fix or prompt user to regenerate.

#### C4: Gap Analysis / 差距分析

```bash
python ~/.qoderworkcn/skills/rpd/scripts/gap-analyzer.py <project-directory> --state-file .project-state.md
```

> **Fallback / 降级**: If script unavailable, manually compare PRD feature list against actual code files. For each PRD feature, search for corresponding implementation files. Mark as ✅/🔨/⏳ based on code completeness. / 脚本不可用时手动对比 PRD 与代码实现。

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
python ~/.qoderworkcn/skills/rpd/scripts/state-validator.py .project-state.md
```
> **Fallback / 降级**: Manually check required fields in `.project-state.md`. / 手动检查必填字段。

Before every "continue development" and "takeover":
```bash
python ~/.qoderworkcn/skills/rpd/scripts/security-scanner.py <project-directory> [--state-file .project-state.md]
```
> **Fallback / 降级**: Manually check for hardcoded secrets and security risks if script unavailable. / 脚本不可用时手动检查安全风险。

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
| Skill terminated without output | Skill 终止无输出 | Check script paths (use `~/.qoderworkcn/skills/rpd/scripts/`), degrade to manual flow per the Graceful Degradation Table. Never silently terminate. / 检查脚本路径，按降级表手动执行流程，绝不静默终止。 |
| Script not found | 脚本未找到 | Use the Graceful Degradation Table in the "Script Path & Graceful Degradation" section to continue manually. / 使用「脚本路径与优雅降级」章节中的降级对照表手动继续。 |
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

---

## Follow-Up Actions / 后续推荐

After completing RPD flow, recommended next steps / 完成 RPD 流程后，推荐后续操作：

| Scenario / 场景 | Recommended Skill / 推荐技能 | Why / 原因 |
|----------|-------------------|-----|
| PRD completed, ready to implement / PRD 完成，准备实施 | `/brainstorming` or design system skill | Turn PRD into implementation plan / 将 PRD 转为实施计划 |
| Project state file generated / 状态文件已生成 | `/sprint-plan` | Break features into sprint stories / 将功能拆分为冲刺故事 |
| Takeover completed (Flow B) / 接手完成 | `/code-review` | Review existing code quality / 审查现有代码质量 |
| Security scan found issues / 安全扫描发现问题 | Manual remediation / 人工修复 | Fix SEC findings before proceeding / 先修复安全问题再继续 |
| Need to track progress / 需要追踪进度 | `/sprint-status` | Monitor implementation against PRD / 监控实施进度与 PRD 对齐 |
