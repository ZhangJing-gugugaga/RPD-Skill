---
name: rpd
description: "MUST be invoked when the user: describes a new product idea, takes over an existing or half-finished project, resumes previous work, says 'continue development', 'where was I', '上次到哪了', '接着做', '继续开发', or asks for project status/进度/下一步. SHOULD also invoke for: PRD writing, requirement diagnosis, cross-session recovery, code-map navigation. English/中文."
description_zh: "当用户描述新产品想法、接手已有项目、恢复上次工作、询问项目进度，或说「继续开发/接着做/上次到哪了/继续上次」时必须使用。也适用于：写 PRD、需求诊断、跨会话进度恢复、code-map 代码导航。支持中英文。"
context: fork
languages: ["en", "zh"]
argument-hint: "new | take | cont | status | scan"
user-invocable: true
---

# RPD — Rapid Product Document

> 确定性认知工程学外骨骼 — 跨会话全生命周期状态机（deterministic cross-session state machine）。

## Language Detection / 语言检测
全程跟随用户首条消息语言（不确定默认中文）。

## Philosophy / 设计原则
- **确定性优先**：判断以脚本输出和状态文件为准，不凭概率推测。
- **最少信任**：AI 记忆不可靠，状态文件才是唯一真相源。
- **最小摩擦**：只在关键时刻介入（新项目/接手/继续），不打扰正常写码。
- **可审计**：决策入 `decisions.md`，变更走 `state-guard.py`，可追溯。

## Hard Constraints / 硬性红线（绝对不可违反）
1. **Security scan 不可跳过**：Flow B/C 开始必跑 `security-scanner.py`；exit 2 硬阻断（WARN 级不阻断，但要复核）。
2. **State validation 不可跳过**：更新状态文件（`.project-state.md` 或 `.rpd/active-context.md`）后必跑校验（v1 `state-validator.py`；v2 走 `state-guard.py` 原子写内置校验）；失败回滚。
3. **每轮最多 3 问**：等回答再继续。
4. **不跳过概念版 PRD**（标准模式）。
5. **不覆盖未备份文件**：写状态文件前先 `state-guard.py --action backup`。危险操作（覆盖/删除/移动/批量/格式转换）必须先告知用户并询问。
6. **路径不越界**。
7. **v2：代码层 json 只读**：`code-map.*.json` 机器产物，绝不手改；需修改=重跑生成器。
8. **v2：stale 禁止动手**：fingerprint 不匹配 → 先 Read 该文件，禁止「基于 map 动手」。
9. **v2：决策先 grill-me**：写入 `decisions.md` 前必须先拷问用户确认。
10. **v2：调用边口径**：calls 边只称「候选调用边 + 可验证锚点」，不称「精确调用图」。

## When to Use / 何时使用
**正向**：新想法（"我想做…"）、接手半成品、继续开发、问进度；"快一点"→极速、"回顾"→回顾模式。**负向**：纯写码/调试、纯技术讨论、需求已完备且无方向困惑。

## v2 Code-Map Mode / v2 代码导航
从「每次重扫」→「读 code-map 导航」。主指标 = **跨会话理解连续性**（M1/M2/M3）。
- **层1** `code-map.router.json` 常驻（≤3k token 且 ≤码库 15%）；**层2** `code-map.json` 按 `kind:path:name` 查单条（≤300 token），从不整份喂入。
- **meta** `code-map.meta.json`：commit + fingerprint（sha256），红线机检数据源；语义层 `code-map.semantic.json` 为派生缓存（`code-map-enrich.py`）。
- **三级信任**：verified（可动手）/ unverified（动手前必 Read）/ stale（禁止动手先 Read）；重扫仅三情形（全量审查/符号不知名/需精确到行）。
- 冷启动 7 步、审核视图、预算守卫、decisions 命令详见 `docs/rpd-v2-usage.md`。

## Script Path & Graceful Degradation / 脚本路径与优雅降级
脚本在 Skill 目录（`SKILL.md` 同级 `scripts/`），降级：Skill 目录 → 项目 `scripts/` → 手动。**脚本失败绝不终止流程。**

## Procedure / 流程

### Step 0: Intent Routing / 意图路由
必跑：`python scripts/intent-router.py "用户输入"` → 按 `recommended_flow` 分流（confidence=medium 时可结合上下文覆盖并说明理由）。

| flow | action |
|------|--------|
| scene_exploration | 场景探索（小白引导） |
| warm_start | 暖启动：问 1 核心问题后重判 |
| standard_diagnosis | 标准三视角诊断 |
| flow_b / flow_c | Flow B 接手 / Flow C 继续 |
| ask_user | 不确定，主动问用户 |

快捷命令：`/rpd new | take | cont | status | scan`。

### Flow A: New Project / 新项目
A-1 初始化 → A0 问题校验（6 项）→ A1 三视角诊断（用户/商业/技术/安全，每轮≤3 问；小白安全自动判）→ A2 概念版 PRD（≤200 字）→ A3 冻结确认 → A4 落地版（模板 `references/prd-template.md`）→ `prd-validator.py --ai-mode` → A5 状态文件（先 backup 再 validate）。
诊断问题与话术详见 `references/brainstorming-flow.md`。

### Flow B: Takeover Half-Finished / 接手半成品
B1 `security-scanner.py`（exit 2 阻断）→ B2 `project-scanner.py` → B3 推断确认 → B4 生成简化 PRD + 状态文件（代码完成度自动标 ✅/🔨/⏳）→ 校验。

### Flow C: Continue Development / 继续开发
C1 查 `.rpd/active-context.md`（v2 首选）→ 无则查 `.project-state.md`（v1 只读兼容）；均无→提示先「分析项目」或「新建项目」；>3 天未动→回顾模式 → C2 `security-scanner.py` → C3 `state-guard.py` 备份/校验 → C4 `gap-analyzer.py` → C5 行动建议 → C6 开发完成提醒更新状态。
**Fast Path**（轻量改动：单文件小修/文案/注释/一行修复）：C1+C3 后直接动手，跳过 C2/C4 全扫描；收尾仍必走 C6。

### v2 冷启动（新会话接手 v2 项目）
`python scripts/rpd-cold-start.py <root>`：① 读 active-context ② 红线机检 ③ 声明鲜度+显式告警 ④ 读 router ⑤ 定位 ⑥ 动手（verified 前置）⑦ 收尾。详见 `docs/rpd-v2-usage.md`。

## Host Hooks / 宿主强制层
装了插件 hooks（Claude Code/ZCode）时：会话启动自动注入状态摘要，收尾未落盘会收到 `[RPD-Skill 落盘提醒]`（`hooks/hooks.json`）。收到注入即视为已完成探测，直接进入 Flow C 或冷启动，无需用户再说「继续开发」。无 hook 宿主：把 `references/agents-bootstrap-snippet.md` 粘进项目 AGENTS.md/CLAUDE.md。

## Token Budget Control / Token 预算
概念版始终输出（≤200 字）；落地版紧张时只输出功能列表+页面结构。**Turbo Mode**（用户说"快一点"或 Token<2000）：跳过概念版与冻结确认，输出 4 行矩阵（进度/下一步/阻塞/预估）。

## Output Norms / 输出规范
- 概念版 PRD ≤200 字用人话；落地版：完整规范 + 状态机 + 字段校验
- 继续开发：进度摘要 + 下一步 + 阻塞项；极速模式：一行进度 + 一行下一步

## Script Toolbox / 脚本工具箱
| Script | Purpose / 用途 |
|--------|---------|
| `intent-router.py` | 确定性意图路由（每次对话开始） |
| `security-scanner.py` | 8 SEC + 注入 + 流式扫描（Flow B/C 开始） |
| `project-scanner.py` | 技术栈/组件/路由（Flow B） |
| `gap-analyzer.py` | PRD vs 代码 + 决策漂移（Flow C） |
| `state-validator.py` | 状态文件 Schema 校验（状态变更后） |
| `state-guard.py` | 备份 + 原子写 + 分支锁（状态更新前） |
| `prd-validator.py` | PRD 完整性 + `--ai-mode`（PRD 生成后） |
| `rpd-cold-start.py` | v2 冷启动 7 步 + v1 兼容（新会话接手） |
| `code-map-generator.py` | v2 code-map 三件套（功能完成/收尾） |
| `rpd-decisions.py` | decisions.md 决策日志（决策确认前） |
| `rpd-metrics.py` | M1/M2/M3 指标采集（会话观测） |
| `code-map-enrich.py` | 语义层富化/校验（结构层之上，可选） |
| `rpd-hook-bridge.py` | 宿主 hooks 入口：自动恢复+落盘提醒 |
| `run-eval.py` | eval 场景（19 个，开发/CI） |

## Failure Modes / 故障处理
脚本不可用→按降级表手动继续，绝不静默终止；状态损坏→修复或提示重新生成；概念版 PRD 改 >3 次→建议先用户调研；状态与代码严重不一致→提示用户确认。
