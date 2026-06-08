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

## 输出规范

- 概念版 PRD：≤200 字，用人话
- 落地版 PRD：完整规范 + 状态机 + 字段校验
- 继续开发：进度摘要 + 下一步 + 阻塞项
- 极速模式：一行进度 + 一行下一步
