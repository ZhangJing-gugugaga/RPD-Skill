# RPD Skill — Agent 交互指南

> 本文件定义 AI Agent 如何与 RPD Skill 交互。

---

## 触发条件

当用户的消息匹配以下模式时，激活 RPD Skill：

| 用户说的 | 意图 | 流程 |
|----------|------|------|
| "我想做一个……" / "I want to build..." | 新项目 | Flow A |
| "帮我做个东西" / "我有个想法" | 新项目（暖启动） | Flow A |
| "接手这个项目" / "Take over" | 接手半成品 | Flow B |
| "继续开发" / "Continue development" | 继续开发 | Flow C |
| "快一点" / "简单点" | 极速模式 | Any |
| "回顾" / "之前做了什么" | 回顾模式 | Flow C |

---

## 执行流程

### 第一步：确定性路由

```bash
python scripts/intent-router.py "用户输入的原文"
```

根据输出的 `recommended_flow` 字段决定走哪条路，**不要靠自己猜**。

### 第二步：执行对应流程

按照 `SKILL.md` 中定义的 Flow A/B/C 执行。

### 第三步：调用脚本

在关键节点必须调用对应脚本：

| 节点 | 脚本 | 时机 |
|------|------|------|
| 意图分类 | `intent-router.py` | 每次对话开始 |
| 安全扫描 | `security-scanner.py` | Flow B/C 开始 |
| 状态校验 | `state-validator.py` | 状态变更后 |
| 状态备份 | `state-guard.py --action backup` | 状态更新前 |
| PRD 校验 | `prd-validator.py` | PRD 生成后 |
| 差距分析 | `gap-analyzer.py` | Flow C |

---

## Hard Constraints（绝对不可违反）

1. 安全扫描不可跳过（exit 2 硬阻断）
2. 状态校验不可跳过（exit 3 回滚）
3. 每轮最多 3 个问题
4. 不可跳过概念版 PRD
5. 不可无备份覆盖状态文件
6. 不可路径遍历

---

## 语言检测

从用户首条消息检测语言，全程跟随：
- 中文 → 中文回复
- 英文 → 英文回复
- 不确定 → 默认中文，询问偏好

---

## v2 决策纪律（grill-me 前置，R-14 硬约束）

> 与 Hard Constraints #3（每轮 ≤3 问）并存：grill-me 遵循「每轮最多 3 个问题」的节奏。

**agent 可以写 `decisions.md`，但每次决策确定前必须先以 grill-me 形式拷问用户**（逐项确认：决策是什么、为什么、影响谁、是否有替代方案）。

| 状态 | 条件 | 动作 |
|------|------|------|
| `proposed` | 决策提出，用户未确认 | 唯一可立即写入的状态 |
| `accepted` | 用户明确确认 | 改 status 并记录 `confirmed_by`（人/时间） |
| `rejected` | 用户否决 | 标 `rejected` |
| `superseded` | 被后续决策替代 | 旧条目标 `superseded`，新条目 `supersedes` 指向旧条目 |

**命令**：
```bash
python scripts/rpd-decisions.py <root> propose "标题" --decision "决策" --type 技术选型 --reason "原因" --impact "影响"
python scripts/rpd-decisions.py <root> accept <n> --confirmed-by "user/2026-08-03"
python scripts/rpd-decisions.py <root> reject <n>
python scripts/rpd-decisions.py <root> supersede <n> --by <新n>
python scripts/rpd-decisions.py <root> list
```

**gap CRITICAL 落盘**：`gap-analyzer.py` 输出 CRITICAL 漂移时：
1. 记录到 `active-context.md` 的阻塞/风险区；
2. 若是新决策 → 走 decisions.md 流程（proposed → 用户确认 → accepted）；
3. 审核视图把 gap 归入「漂移」区块。

**严禁**：不拷问用户就把决策标为 accepted；静默覆盖既有决策。

---

## v2 冷启动流程（7 步）与 code-map 导航

新会话接手 v2 项目时，按以下顺序执行（`rpd-cold-start.py` 已实现第①②③④步）：

```
① 读 active-context.md（上次进度、下一步、阻塞、未落盘告警）
② 红线机检：读 code-map.meta.json；git diff map_commit..HEAD；fingerprint 比对
   → 产出 verified / unverified / stale 文件清单
③ 声明鲜度：一行声明 map 基于的 commit + verified/stale 数；有 stale 先 Read 受影响文件
   → understand-anything 降级在此步显式告警（不静默）
④ 按需加载：读 code-map.router.json（层1）；按任务经 router 查 entry_ref，读单条 entry（≤300 token）
⑤ 定位：用 id = function:path:name 定位符号/文件/候选调用边（confidence 标注）
⑥ 动手：目标文件必须 verified；否则先 Read 该文件
⑦ 收尾：更新 active-context.md；增量落盘 code-map；决策变更 → decisions.md（grill-me）
```

**三条首要告诫**：
1. **map 是导航不是真相**：一切「基于 map 动手」都以 verified 为前提；unverified 必先 Read，stale 必禁动。
2. **代码层 json 永远只读不手改**：需要「修 json」= 重跑 `code-map-generator.py`。手工编辑会破坏 fingerprint 与信任链。
3. **对外口径不可越界**：calls 边只叫「候选调用边 + 可验证锚点」，永远不叫「精确调用图」。

**主指标**：M1 理解连续性 / M2 定位成本 / M3 文档引用 为并列主指标；`net_tokens_to_first_action` 仅作次要观测（`rpd-metrics.py` 采集）。

---

## 输出规范

- 概念版 PRD：≤200 字，用人话
- 落地版 PRD：完整规范 + 状态机 + 字段校验
- 继续开发：进度摘要 + 下一步 + 阻塞项
- 极速模式：一行进度 + 一行下一步
