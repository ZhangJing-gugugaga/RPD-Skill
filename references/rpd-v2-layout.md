# RPD v2 记忆落点与目录规格（.rpd/）

> 本文是 v2 `.rpd/` 目录布局的**权威契约**，供 code-map 生成器、冷启动流程、审核视图引用。
> 所有路径均为**相对项目根**（全动态路径，禁止硬编码绝对路径）。

---

## 1. 分层原则：产品层 vs 代码层

| 层 | 内容 | 生成者 | 可读 | 可写 | 示例 |
|----|------|--------|------|------|------|
| 产品层（md，人可读可改） | 进度、决策、审核视图 | agent（受 grill-me 约束） | ✅ | ✅（用户可手改） | `active-context.md`、`decisions.md`、`review-<date>.md` |
| 代码层（json，机器生成） | 符号表、路由、元数据 | code-map 生成器（只读不写） | ✅（只读） | ❌ agent 绝不手工编辑 | `code-map.router.json`、`code-map.json`、`code-map.meta.json` |

> **红线**：代码层 json 是机器产物，agent 在会话中只读、绝不可手工改（防格式漂移 + 防 fingerprint 失配）。任何"手工修复 json"的行为都应通过重跑生成器完成。

## 2. 目录树（v2 目标态）

```
<project-root>/
├── .rpd/                          # v2 记忆落点（全动态路径）
│   ├── code-map.router.json       # 层1：路由/索引（常驻 context）
│   ├── code-map.json              # 层2：完整符号表（按需查单条 entry）
│   ├── code-map.meta.json         # 元数据：commit hash、fingerprint、预算、信任
│   ├── active-context.md          # 产品层：本次会话上下文（进度/下一步/阻塞）
│   ├── decisions.md               # 产品层：决策日志（proposed→accepted）
│   ├── review-<date>.md           # 产品层：审核者视图归档（R-12）
│   └── .code-map.tmp/             # 生成器暂存（原子替换用，可清理）
│       └── code-map.json.tmp
├── (v1 产物，v2 迁移/共存)
│   ├── .project-state.md          # v1 状态文件（v2 保留兼容读取，不删除）
│   └── .rpd-backup-<timestamp>/   # 迁移备份
└── src/ ...                       # 用户源码（rpd 只读）
```

## 3. 文件级规格

| 文件 | 层 | 常驻 context? | 体积预算 | 更新者 | 更新时机 |
|------|----|--------------|----------|--------|----------|
| `code-map.router.json` | 代码层 | ✅ 永远在 context | ≤3k token **且** ≤全码库 15% | 生成器 | 功能完成即更 / 收尾必写 |
| `code-map.json` | 代码层 | ❌ 按需读单条 | 不计入会话读取预算（体积可不计） | 生成器 | 同 router |
| `code-map.meta.json` | 代码层 | ✅ 启动时读（小） | 极小（约 0.5–1k token） | 生成器 | 同 router |
| `active-context.md` | 产品层 | ✅ 启动时读 | ≤2k token（软约束） | agent | 收尾必写 / 功能完成即更 |
| `decisions.md` | 产品层 | 启动时读（仅 accepted） | 软约束 | agent（grill-me 前置） | 决策确定后 |
| `review-<date>.md` | 产品层 | ❌ 归档，按需读 | 不限 | agent | 审核会话结束时 |

## 4. 全动态路径解析顺序

1. 用户项目根（`.rpd/` 所在处）
2. skill 安装目录（`SKILL.md` 同级的 `scripts/`）
3. 均不存在 → 按 SKILL.md「Script Path & Graceful Degradation」降级表手动操作

所有引用统一为相对项目根路径，写盘时用 `Path.resolve()` 归一化。

## 5. 迁移与备份（首次在已有 v1 项目启用 v2）

1. 检测到 `.project-state.md` 存在；
2. 将其备份至 `.rpd-backup-<timestamp>/`（含时间戳，保留原文件不动）；
3. 生成 `code-map.*` 三件套；
4. 在 `active-context.md` 首行记录迁移信息（"从 v1 迁移，原状态文件已备份至 …"）。

> **覆盖前必须先备份**（沿用 v1 state-guard 原则），任何 `.rpd/` 下文件被覆盖前都先执行等价 `state-guard.py --action backup`。

## 6. 兼容读取 v1 状态文件

- 冷启动同时检测 `.project-state.md`（v1 状态文件）。
- 存在：读取其"功能进度清单"与"关键决策记录"作为 `active-context.md` 的输入，但**不覆盖** v2 的 `active-context.md`（冲突时以 v2 为准，v1 只做参考）。
- 迁移完成（首次生成 code-map 且已备份）后，v1 文件保留但不再主动写；用户明确要求才迁移其内容到 v2 文件。
- **不删除 v1 文件**，避免破坏用户既有依赖。
