# RPD Skill v2 技术规格书（Agent 用）

> 面向接手 rpd skill v2 开发/维护的 agent。本文件是**实现约束**而非产品文档——所有已拍板决策（2026-08-03 方向明 Q1–Q7 + 主指标重构）必须遵守，本规格只做展开，不做翻案。
>
> 相关文件：`README.md`（对外口径）、`references/state-file-spec.md`（v1 状态文件规范）、`references/state-schema.json`（v1 schema）、`AGENT.md`（agent 交互指南）。v2 变更点见下文各节。

---

## 0. 文档约定

- **主工作区**：`E:/Desktop/work/RPD-skill/`（v1 副本 + v2 开发）。
- **试点项目**：`E:\Desktop\work\mix\roguelike`（C++，src 18 文件 + tests 9 文件，代码约 2428 行；对外口径 17 文件/1745 行按 `src/` 计）。
- **术语**：
  - `map` = code-map 产物总称（router + 主表 + meta）。
  - `entry` = code-map.json 中的单条符号记录。
  - `重扫` = 对项目源码做全量 Glob/Grep/Read 定位（v1 行为）。
  - `基于 map 动手` = 不 Read 源文件、直接以 map 信息为依据进行修改/推理。
- **层代号**：层1 = router.json（常驻 context），层2 = code-map.json（按需查单条）。
- 所有路径中的 `.rpd/` 均为项目根目录下的隐藏目录（全动态路径，见 §4）。

---

## 1. 升级目标与主线

### 1.1 问题陈述

v1 的跨会话记忆依赖"每次新会话 Glob/Grep 重扫代码"来重建项目认知。代价：
- 新会话冷启动即产生大量扫描类 token；
- 扫描结果无法跨会话复用，理解不连续；
- 定位"某个函数被谁调用"等高阶问题每次都从零开始。

### 1.2 升级主线

**从"每次重扫" → "读 code-map 导航"。**

- 生成一次 code-map，后续会话**优先读 map** 而非重扫源码。
- 主指标 = **跨会话理解连续性**（见 §1.3），token 不再是主指标。
- 软建议避免重扫；重扫降级为**按需兜底**，仅在明确情形触发（见 §1.4）。

### 1.3 主指标（多指标并列，net_tokens_to_first_action 降为次要观测）

| # | 指标 | 定义 | 对比口径 |
|---|------|------|----------|
| M1 | 理解连续性 | 有/无 code-map 时，新会话接手是否保有项目理解：无需重扫即知道结构、关键符号、上次进度、关键决策；再上手时间；理解是否丢失 | A/B：同一任务、同一新会话，有 map vs 无 map |
| M2 | 定位成本 | 调用 vs 不调用 map 定位同一函数/接口调用关系的时间成本与 token 成本 | 同任务两轮计时 + token 日志 |
| M3 | 文档引用 | 定位 README/CHANGELOG/决策文档与代码对应关系的时间与 token 成本 | 同上 |

- `net_tokens_to_first_action` 仅作次要观测，不作为 Gate 卡口。
- I0 阶段 arm A ×3 反解 S/m/k 参数（见 §12.1），方差过大再收紧。

### 1.4 重扫触发条件（A 臂冻结按需重扫策略，Q7）

**默认不重扫。** 仅当满足以下任一条件才执行全量/定向重扫：

1. 用户**明确要求**全量审查（如"把所有代码过一遍"）；
2. 目标符号**不知名**或无法仅靠 code_map 定位（如只知道 UI 上的一处文案，找不到对应符号）；
3. bug 排查**必须精确到某一行的实现细节**（map 只有符号级信息，无行级实现）。

红线机检失败（§6）时同样禁止"基于 map 直接动手"，但那是强制重读单文件，不是全量重扫。

---

## 2. `.rpd/` 目录结构规格

### 2.1 分层原则：产品层 vs 代码层

| 层 | 内容 | 生成者 | 可读 | 可写 | 示例 |
|----|------|--------|------|------|------|
| 产品层（md，人可读可改） | 进度、决策、审核视图 | agent（受 grill-me 约束） | ✅ | ✅（用户可手改） | `active-context.md`、`decisions.md`、`review-<date>.md` |
| 代码层（json，机器生成） | 符号表、路由、元数据 | `code-map 生成器` 只读不写 | ✅（只读） | ❌ agent 绝不手工编辑 | `code-map.router.json`、`code-map.json`、`code-map.meta.json` |

> **红线**：代码层 json 是机器产物，agent 在会话中只读、绝不可手工改（防格式漂移 + 防 fingerprint 失配）。任何"手工修复 json"的行为都应通过重跑生成器完成。

### 2.2 目录树（v2 目标态）

```
<project-root>/
├── .rpd/                          # v2 记忆落点（全动态路径，见 §4）
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
│   └── .rpd-backup-<timestamp>/   # 迁移备份（见 §4.3）
└── src/ ...                       # 用户源码（rpd 只读）
```

### 2.3 文件级规格

| 文件 | 层 | 常驻 context? | 体积预算 | 更新者 | 更新时机 |
|------|----|--------------|----------|--------|----------|
| `code-map.router.json` | 代码层 | ✅ 永远在 context | ≤3k token **且** ≤全码库 15%（§7） | 生成器 | 功能完成即更 / 收尾必写 |
| `code-map.json` | 代码层 | ❌ 按需读单条 | 不计入会话读取预算（体积可不计） | 生成器 | 同 router |
| `code-map.meta.json` | 代码层 | ✅ 启动时读（小） | 极小（约 0.5–1k token） | 生成器 | 同 router |
| `active-context.md` | 产品层 | ✅ 启动时读 | ≤2k token（软约束） | agent | 收尾必写 / 功能完成即更 |
| `decisions.md` | 产品层 | 启动时读（仅 accepted） | 软约束 | agent（grill-me 前置） | 决策确定后 |
| `review-<date>.md` | 产品层 | ❌ 归档，按需读 | 不限 | agent | 审核会话结束时 |

---

## 3. code-map 两层结构（核心）

### 3.1 总体关系

```
code-map.router.json（层1，常驻）
  ├─ version / schema_version
  ├─ project 摘要（name, language, file_count, line_count, commit）
  ├─ 顶层符号索引（每文件 1–N 条：符号名 → entry 指针）
  ├─ 文件清单（path → fingerprint, entry_count）
  ├─ 文档清单（README/CHANGELOG/决策文档 → 关联符号/模块）
  └─ 生成信息（generated_at, generator_version, commit, 预算统计）

code-map.json（层2，完整 key-value 符号表）
  └─ 每符号一条 entry：
       id = "function:<path>:<name>"
       { signature, file, kind, line, calls[]+confidence, doc_refs[] }
  └─ 附：inverted index（按符号名/关键词 → entry id 列表，供定位）

code-map.meta.json（元数据，红线机检 + 预算守卫的数据源）
  └─ commit, files{path: fingerprint}, estimated_read_tokens, trust 状态
```

- **从不整份喂入 code-map.json**。定位只做：按 `function:path:name` 查单条 entry（≤300 token，§8）。
- **router.json 永远在 context**，是冷启动的第一入口（§9）。

### 3.2 `code-map.router.json` schema（示例）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RPD Code-Map Router (Layer 1)",
  "version": 2,
  "schema_version": "2.0.0",
  "project": {
    "name": "roguelike",
    "language": ["cpp"],
    "file_count": 18,
    "line_count": 1745,
    "head_commit": "a1b2c3d4e5f6..."
  },
  "top_symbols": [
    {
      "id": "function:src/game.h:Game::update",
      "name": "Game::update",
      "file": "src/game.h",
      "line": 42,
      "kind": "method",
      "entry_ref": "code-map.json#function:src/game.h:Game::update"
    }
  ],
  "files": [
    {
      "path": "src/game.h",
      "fingerprint": "sha256:...",
      "entry_count": 12,
      "loc": 87
    }
  ],
  "documents": [
    {
      "path": "README.md",
      "topic": "overview",
      "related_symbols": ["function:src/game.h:Game::update", "function:src/main.cpp:main"]
    },
    {
      "path": "CHANGELOG.md",
      "topic": "history"
    }
  ],
  "budget": {
    "estimated_read_tokens": 2450,
    "token_limit": 3000,
    "pct_of_codebase": 12.4,
    "pct_limit": 15
  },
  "generated": {
    "generator_version": "2.1.0",
    "generated_at": "2026-08-03T18:00:00Z",
    "commit": "a1b2c3d4e5f6..."
  }
}
```

- `top_symbols` 必须满足**硬约束**：整份 router ≤3k token 且 ≤全码库 15%。超限时生成器按 `top_symbols` 裁剪（保留高频/入口/导出符号，PageRank 稀疏见 R-09）。
- `entry_ref` 提供 `code-map.json#<id>` 形式的定位地址。

### 3.3 `code-map.json` schema（层2，单条 entry 示例）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": 2,
  "schema_version": "2.0.0",
  "entries": {
    "function:src/game.h:Game::update": {
      "id": "function:src/game.h:Game::update",
      "name": "Game::update",
      "kind": "method",
      "file": "src/game.h",
      "line": 42,
      "signature": "void Game::update(float dt)",
      "doc": "Main per-frame update loop; advances player, enemies, FOV.",
      "calls": [
        { "target": "function:src/player.h:Player::move", "confidence": "heuristic" },
        { "target": "function:src/fov.cpp:compute_fov", "confidence": "resolved" }
      ],
      "called_by": [
        { "caller": "function:src/main.cpp:main", "confidence": "resolved" }
      ],
      "doc_refs": ["README.md", "CHANGELOG.md"]
    }
  },
  "inverted_index": {
    "update": ["function:src/game.h:Game::update"],
    "Game": ["function:src/game.h:Game", "function:src/game.h:Game::update"]
  }
}
```

**entry 字段约束**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | `function:path:name` 三段式；`kind` 变化时前缀变化（`class:`/`struct:`/`function:`/`method:`/`variable:`/`macro:`） |
| `name` | ✅ | 符号名（含限定名，如 `Game::update`） |
| `kind` | ✅ | `function` \| `method` \| `class` \| `struct` \| `variable` \| `macro` \| `enum` |
| `file` | ✅ | 相对项目根路径 |
| `line` | ✅ | 定义行号（符号定位锚点） |
| `signature` | ✅ | 人类可读签名（C++ 含返回类型与参数） |
| `doc` | ⭕ | 单行摘要（生成器从注释/文档提取，缺失则为空） |
| `calls[]` | ✅（至少空数组） | 候选调用边，每边必须带 `confidence`（§3.4） |
| `called_by[]` | ⭕ | 反向候选调用边（生成器计算，可能缺失） |
| `doc_refs[]` | ⭕ | 关联文档（README/CHANGELOG/决策文档），供 M3 定位 |

### 3.4 calls 边的对外口径（R-06，硬约束）

- 每一条调用边**必须**带 `confidence`，取值仅两种：
  - `resolved`：tree-sitter 查询到确定调用点（调用位置已确认）；
  - `heuristic`：基于符号名匹配/关键词推断的候选边（未确认调用点）。
- 对外（用户/README/审核视图）**只允许表述**：
  - "候选调用边" + "可验证锚点"（`file:line` 或 entry id）。
- **禁止**表述为"精确调用图 / call graph / 精确依赖图"。
- 理由：tree-sitter 是启发式结构解析，不是真正的 call graph 求解器。任何声称精确的行为都属于范围外（§14 Non-goals）。

### 3.5 `code-map.meta.json` schema（红线机检 + 预算守卫数据源）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RPD Code-Map Metadata",
  "version": 2,
  "schema_version": "2.0.0",
  "generator_version": "2.1.0",
  "generated_at": "2026-08-03T18:00:00Z",
  "head_commit": "a1b2c3d4e5f6...",
  "map_commit": "a1b2c3d4e5f6...",
  "files": {
    "src/game.h": {
      "fingerprint": "sha256:9f86d081884c7d65...",
      "entry_count": 12,
      "lines": 87
    }
  },
  "budget": {
    "router_estimated_read_tokens": 2450,
    "router_token_limit": 3000,
    "router_pct_of_codebase": 12.4,
    "router_pct_limit": 15,
    "entry_max_tokens": 300
  },
  "trust": {
    "overall": "verified",          // verified | unverified | stale（三级信任，§8）
    "last_verified_at": "2026-08-03T18:05:00Z"
  },
  "understand_anything": {
    "detected": false,               // 兼容读取（R-10，§11）
    "reused": false,
    "source_path": null
  }
}
```

---

## 4. 双层落点 + 全动态路径 + 迁移备份（R-03）

### 4.1 落点

- 所有 v2 记忆落于 `<project-root>/.rpd/`（`active-context.md`、`decisions.md` 也可落 `.rpd/`，与 code-map 同目录）。
- v1 的 `.project-state.md` 保留兼容读取，不强制删除（见 §11 兼容读取逻辑同样适用于 v1 状态文件）。

### 4.2 全动态路径

- **禁止硬编码** `~/.qoderworkcn/skills/rpd/` 或任何绝对路径。
- 路径解析顺序（rpd 自身脚本与产物）：
  1. 用户项目根（`.rpd/` 所在处）；
  2. skill 安装目录（`SKILL.md` 同级的 `scripts/`）；
  3. 均不存在 → 按 AGENT.md 降级表手动操作。
- 所有引用统一为相对项目根路径，写盘时用 `Path.resolve()` 归一化。

### 4.3 迁移与备份

- 首次在已有 v1 项目启用 v2 时：
  1. 检测到 `.project-state.md` 存在；
  2. 将其备份至 `.rpd-backup-<timestamp>/`（含时间戳，保留原文件不动）；
  3. 生成 `code-map.*` 三件套；
  4. 在 `active-context.md` 首行记录迁移信息（"从 v1 迁移，原状态文件已备份至 …"）。
- **覆盖前必须先备份**（沿用 v1 state-guard 原则），任何 `.rpd/` 下文件被覆盖前都先 `state-guard.py --action backup` 等价物。

---

## 5. 兼容读取 understand-anything（R-10，Q6）

### 5.1 检测

- 冷启动时检测项目内是否存在 `knowledge-graph.json`（understand-anything 插件的产物），路径探测顺序：`.claude/`、`.workbuddy/`、项目根、`.rpd/`。
- 找到且 schema 匹配 → **优先复用**（只读不写，绝不修改该文件）。

### 5.2 复用规则

- 只读：把 `knowledge-graph.json` 当作补充事实源，与自身 code-map 交叉核对；
- 只写自己的 `code-map.*`，绝不对 knowledge-graph.json 做任何写操作。

### 5.3 降级规则

- 找不到，或 schema 不匹配 → 降级为自建 code-map，**且首条输出必须显式告警**，不静默。告警模板：
  > ⚠️ 检测到 understand-anything 的 knowledge-graph.json 存在但 schema 不兼容（或缺失），已降级为 rpd 自建 code-map。不会读取/修改该文件。

### 5.4 meta 记录

- 无论复用还是降级，`code-map.meta.json.understand_anything` 记录检测结果（§3.5 示例字段）。

---

## 6. 红线机检协议（R-04，Q9）

### 6.1 数据源

- `code-map.meta.json` 记录生成时：
  - `map_commit`：生成时 HEAD commit hash；
  - `files.<path>.fingerprint`：每个**已入 map 文件**的内容 hash（sha256 全文）。

### 6.2 会话启动比对

冷启动流程第②步（§9）执行：

```
git diff <map_commit>..HEAD --stat      # 变更文件集合（若 map_commit == HEAD，跳过）
```

对每个变更文件：
1. 读取当前文件内容；
2. 计算 sha256；
3. 与 `meta.files[path].fingerprint` 比对。

### 6.3 阻断规则

| 比对结果 | 文件信任状态 | 阻断动作 |
|----------|--------------|----------|
| fingerprint 一致 | `verified` | 可基于 map 定位 |
| fingerprint 不一致（内容变） | `stale` | **禁止**据此定位动手；强制 Read 该文件后再决策（见 §8） |
| 文件未在 map 中（新增） | `unverified`（对新增文件 N/A） | 按需 Read；不阻断其他已 verified 文件 |

- **不一致即阻断**：只要存在任一 `stale` 文件且后续动作会依赖其 map 信息，就禁止"基于 map 直接动手"，必须先 Read 该文件。可只重读受影响文件，不需全量重扫（§1.4 的例外不触发全量重扫）。
- git 仓库不可用（无 `.git`）时：跳过 commit 比对，改为全文件 fingerprint 抽查（生成器标记 `git_available: false`，冷启动声明"无 git 环境，按 fingerprint 逐文件核验"）。

---

## 7. 读取预算守卫（R-07，Q2/Q10）

### 7.1 双层口径

| 对象 | 硬上限 | 说明 |
|------|--------|------|
| `code-map.router.json`（层1） | **≤3k token 且 ≤全码库 15%** | 永远在 context，两个条件**同时满足**；超任一即裁剪 top_symbols |
| `code-map.json`（层2） | 不计入会话读取预算 | 按需读单条，从不整份喂入 |
| 单条 entry | **≤300 token** | 读取一条 entry 的 token 上限 |
| `code-map.meta.json` | 极小（约 0.5–1k token） | 启动必读 |

- 3k/5k 二选一已被消解（Q2）：取 3k，同时叠加 15% 相对口径，二者取更严。
- 全码库 = 源码文件总 token 估算（`line_count * avg_tokens_per_line`，默认 10，可配置）。

### 7.2 生成器职责

- 生成时计算 `router_estimated_read_tokens` 写入 meta；
- 若超限：裁剪 `top_symbols`（保入口/导出/高频符号），并在 meta 记录 `trimmed: true` 与被裁剪数量；
- 单条 entry 若超 300 token（罕见，如超长签名）：截断 `signature`/`doc` 字段，保证 entry 读取可预测。

### 7.3 运行时守卫

- agent 定位时只允许读取单条 entry（`code-map.json` 的 `entries[id]`），**禁止**一次读整份文件；
- 若需要一次读取多条（如反向边列表），累加 ≤300 token/条，超出分批读；
- 违规行为（整份读 code-map.json）应在审核视图"鲜度/变更"区块记一笔（漂移检测）。

---

## 8. 三级信任标注（R-13，Q12）

### 8.1 信任状态定义

| 状态 | 判定 | 允许动作 |
|------|------|----------|
| `verified` | 本次会话已 Read 该文件，且内容与 HEAD 一致（或已用 fingerprint 核验一致） | 可基于其 map 信息定位/动手 |
| `unverified` | 来自 map、本会话未 Read 验证；或 map 信息存在但未被本次会话核对 | **动手前必须 Read 该文件**（Read 后可升级为 verified） |
| `stale` | fingerprint 与 meta 不匹配（文件已变更） | **禁止**据此定位动手；强制 Read 该文件，且 Read 后需重新生成/更新该 entry 或标记为最新 |

### 8.2 信任传播

- 冷启动红线机检后：全部 fingerprint 一致 → meta `trust.overall = verified`；有不一致 → `stale` 文件列表入审核视图"鲜度"区块。
- 会话中每 Read 一个文件，若与 HEAD 一致即标记该文件 `verified`（写入 meta 或会话内记录）。
- **默认态度**：来自 map 的信息一律视为 `unverified`，动手（修改/重构/删除）前先 Read 源文件。map 是导航，不是免 Read 通行证。

---

## 9. 会话冷启动流程（7 步）

```
① 读 active-context
   → active-context.md：上次进度、下一步、阻塞、未落盘告警
② 红线机检
   → 读 code-map.meta.json；git diff map_commit..HEAD；fingerprint 比对
   → 产出：verified / unverified / stale 文件清单
③ 声明鲜度
   → 输出一行声明："map 基于 commit <hash>，<N> 文件 verified，<M> 文件 stale（列名）"
   → 有 stale：进入"先 Read 受影响文件"或"提示更新 map"
   → 检测到 understand-anything 降级：在此步输出显式告警（§5.3）
④ 按需加载
   → 读 code-map.router.json（层1，若本会话尚未在 context）
   → 按任务需求经 router 查 entry_ref，读 code-map.json 单条 entry（≤300 token）
⑤ 定位
   → 用 id = function:path:name 定位符号、文件、候选调用边（confidence 标注）
   → 不确定/超范围 → 按 §1.4 触发定向重扫（不默认全量）
⑥ 动手
   → 基于 map 动手前：目标文件必须是 verified（否则先 Read）
   → 修改涉及符号/文件 → 视为"基于 map 的信息已被验证/更新"
⑦ 收尾
   → 更新 active-context.md（进度/下一步/阻塞）
   → 增量落盘 code-map（§10）；未落盘 → 显式告警
   → 决策变更 → decisions.md（grill-me 前置，§12.4）
   → 审核会话 → 生成 review-<date>.md（§13）
```

---

## 10. 更新时机（R-08，Q11）

### 10.1 触发时机（三必更 + 一必告警）

| 时机 | 动作 |
|------|------|
| **收尾必写** | 每次会话结束时：更新 `active-context.md`；若源码有改动，增量落盘 code-map |
| **功能完成即更** | 一个功能/一次重构完成时：增量更新 code-map（新增/修改/删除相关 entry） |
| **首次生成** | 项目首次启用 v2 时：全量生成三件套 |
| **未落盘告警** | 会话中源码有改动但未落盘就结束 → 收尾时**显式告警**："检测到未落盘的代码变更（文件列表），下次会话将按 fingerprint 标记为 stale" |

### 10.2 增量落盘（非全量重建）

- 只对**改动文件**重解析：
  - 删除的符号 → 从 code-map.json 删除对应 entry；
  - 新增/修改的符号 → 重解析该文件，更新/插入 entry；
  - router 的 `top_symbols`、`files[].fingerprint` 同步更新；
  - meta 的 `map_commit` 更新为当前 HEAD，`files[].fingerprint` 更新。
- 写盘采用**原子替换**：写 `.code-map.tmp/code-map.json.tmp` → 校验 → rename 覆盖。
- 未涉及的文件 entry 与 fingerprint 保持不变（这就是信任体系能工作的前提）。

---

## 11. 兼容读取 v1 状态文件（补充规则）

- 冷启动同时检测 `.project-state.md`（v1 状态文件）。
- 存在：读取其"功能进度清单"与"关键决策记录"作为 `active-context.md` 的输入，但**不覆盖** v2 的 `active-context.md`（冲突时以 v2 为准，v1 只做参考）。
- 迁移完成（首次生成 code-map 且已备份）后，v1 文件保留但不再主动写；用户明确要求才迁移其内容到 v2 文件。
- 不删除 v1 文件，避免破坏用户既有依赖。

---

## 12. decisions.md 决策日志（R-14，Q5）

### 12.1 文件格式

`decisions.md` 追加式日志，每条决策：

```markdown
## D-<n> <标题>
- **date**: YYYY-MM-DD
- **type**: 技术选型 | 架构模式 | 安全策略 | 业务逻辑 | 范围 | 其他
- **status**: proposed | accepted | rejected | superseded
- **decision**: <一句话决策>
- **reason**: <决策原因>
- **impact**: <影响范围>
- **confirmed_by**: <用户确认记录，人/时间>
```

### 12.2 写入权（Q5，硬约束）

- **agent 可以写** decisions.md，但每次决策**确定前**必须先以 **grill-me 形式拷问用户**（逐项确认：决策是什么、为什么、影响谁、是否有替代方案）。
- 用户确认前：只能写 `status: proposed`；
- 用户明确确认后：改为 `status: accepted` 并记录 `confirmed_by`。
- 用户否决 → `status: rejected`；被后续决策替代 → 旧条目标 `superseded` 并在新条目 `supersedes` 字段指向旧条目。

### 12.3 gap 落盘

- 检测到"文档决策 vs 代码实现"漂移（gap-analyzer 输出 CRITICAL）时：
  1. 记录到 `active-context.md` 的阻塞/风险区；
  2. 若是新决策 → 走 decisions.md 流程（proposed → 用户确认 → accepted）；
  3. 生成审核视图时把 gap 归入"漂移"区块（§13）。

---

## 13. 审核者视图信息架构（R-12，Q3）

### 13.1 五区块

审核者视图 = 终端文本（会话内，agent 主动输出）+ 归档文件 `.rpd/review-<date>.md`（可跨会话追溯）。

| 区块 | 内容 |
|------|------|
| ① 鲜度 | map 基于的 commit；本次会话 verified / unverified / stale 文件数；stale 文件列表 |
| ② 变更 | 自 map_commit 以来的 git diff 摘要（文件级）；未落盘变更告警 |
| ③ 待确认 | decisions.md 中 `proposed` 待用户确认的决策；gap 漂移待裁决项 |
| ④ 漂移 | 文档决策 vs 代码实现不一致（gap-analyzer CRITICAL）；router 预算超限记录；整份读 code-map.json 违规记录 |
| ⑤ 进度-代码对账 | 功能进度清单（active-context）vs 实际代码（code-map entry 状态）逐项对账；完成/缺失/多余实现 |

### 13.2 生成时机

- 用户要求"审核/回顾/Review"时；
- 冷启动发现 stale 数量 > 阈值（建议 ≥5 文件）时；
- 会话收尾可选生成（若期间有显著变更）。

### 13.3 归档格式

`review-<date>.md` 用日期命名（如 `review-2026-08-03.md`），同一天多次审核追加 `-2`、`-3`。文件头记录：审核时间、map commit、会话内读取 token 统计、核心结论。

---

## 14. Non-goals（范围外，10 条）

1. **不承诺精确调用图**：calls 边是"候选调用边 + 可验证锚点"，tree-sitter 是启发式，不做真 call graph 求解（R-06 硬约束）。
2. **不做全量重扫的默认行为**：重扫只在 §1.4 三个条件触发；默认走 map 导航。
3. **不手工编辑代码层 json**：code-map.* 只由生成器写入，agent 只读。
4. **不做跨语言统一符号解析**：R-16 多语言是 P2，v1 仅 C++/主语言，其它语言走"未索引文件 → 按需 Read"。
5. **不替代 understand-anything**：对 knowledge-graph.json 只读复用，不写、不迁移、不管理其生命周期。
6. **多会话并发写冲突用进程级物理锁兜底**：R-18 已升级——state-guard.py 的 atomic_update 用 `ProjectStateMutex`（msvcrt/fcntl 文件锁）包裹备份→写入→校验事务，防双 Agent 竞态覆写；fingerprint/原子写仍作兜底。
7. **不承诺 100% 的 token 节省**：token 是次要观测指标；小仓收益低属预期（见 §15 收益边界声明）。
8. **不生成逐行级代码索引**：map 是符号级导航，不含函数体/实现细节；精确到行的 bug 定位仍需 Read（§1.4③）。
9. **不自动写入用户决策**：decisions.md 中任何决策必须先 grill-me 拷问用户并获确认（Q5）。
10. **不做 git 无关项目的行为保证**：无 `.git` 时红线机检退化为 fingerprint 抽查，可靠性降级但流程不中断（§6.3）。

---

## 15. 小仓库标准定义（R-05，Q1/Q4 连锁）

### 15.1 建议阈值（写入 README 的"该仓收益边界声明"）

| 指标 | 小仓库阈值（建议值） | 说明 |
|------|---------------------|------|
| 源码文件数 | **≤ 20 个** | src/ 下源文件（排除 tests/generated/vendor） |
| 源码行数 | **≤ 1500 行** | 同上口径 |
| 符号数 | **≤ 150 个**（推论值） | 文件数×行数阈值反推的工程经验值 |

- **判定**：满足"文件数 ≤20 **或** 行数 ≤1500"即视为小仓库（取宽松口径，避免误伤）。
- **收益边界声明**（README 固定文案，Q4）：
  > 小仓库（≤20 源文件或 ≤1500 行）的 code-map 收益低于大仓库属**预期**。token 不是主指标；code-map 的价值在于**跨会话理解连续性**与**演进确定性**——小仓会进化成大仓，map 从第一天就应建立。required_h>85% 不再作为停建 Gate。
- **为什么不再停建**（Q1/Q4 连锁）：required_h>85% 停建取消，改为上述声明；code-map **必须建立**（小仓会进化成大仓）。

### 15.2 阈值校准说明

- 阈值来自试点 roguelike（18 源文件/1745 行，恰处临界附近）：以它为分界，≈20 文件/≈1500 行是"重扫成本低但 map 已有收益"的甜点区。
- 阈值为**建议值**，I3 验收（§16.5）用试点数据回代验证，若 A/B 实测表明小仓 map 收益为负且连续（≥3 项目），再上调阈值并同步更新 README 声明。
- 行数按源文件（src/）计，排除 tests/、generated/、vendor/、build 产物。

---

## 16. 验收标准

### 16.1 需求池验收（R-XX 每条）

| 需求 | 验收标准 |
|------|----------|
| **R-01 校准协议** | I0 完成 arm A ×3 反解 S/m/k；方差过大时输出收紧建议；S/m/k 写入 docs/calibration.md |
| **R-02 code-map 生成器** | tree-sitter 解析 C++ 生成三件套；C++ 的 reference query 支持；**不得回退 Pygments**（硬约束）；试点 roguelike 生成成功且 router ≤3k token & ≤15% |
| **R-03 双层落点+动态路径+迁移备份** | 产物落 `<root>/.rpd/`；无任何硬编码绝对路径；v1 项目首启备份 `.rpd-backup-<ts>/` 且原文件不动 |
| **R-04 红线机检** | 改一个已入 map 文件后，冷启动检测到 stale 并阻断"基于 map 动手"；必须 Read 后放行 |
| **R-05 SKILL.md 瘦身** | SKILL.md ≤8KB；README 含小仓库收益边界声明 + 小仓库标准定义（§15） |
| **R-06 calls confidence** | 所有 calls 边带 `confidence: heuristic\|resolved`；对外输出无"精确调用图"字样 |
| **R-07 读取预算守卫** | router 超限自动裁剪并记录；单条 entry 读取 ≤300 token；整份读 code-map.json 被拦截/记录 |
| **R-08 更新时机** | 收尾必写 active-context；功能完成增量落盘（仅改文件）；有未落盘变更时收尾显式告警 |
| **R-09 分层索引** | router.top_symbols 用 PageRank 稀疏化（P1）；top_symbols 保留高频/入口/导出符号 |
| **R-10 兼容读取** | 有 knowledge-graph.json 且 schema 匹配 → 复用且只读；不匹配 → 自建 + 首条输出显式告警 |
| **R-11 符号名路径寻址** | 定位不用纯行号；`function:path:name` 寻址在文件行号变化后仍有效（重生成后 id 稳定） |
| **R-12 审核者视图** | 五区块齐全；终端文本 + 归档 review-<date>.md 可跨会话追溯 |
| **R-13 三级信任** | verified/unverified/stale 判定正确；stale 文件禁止定位动手；unverified 动手前必须 Read |
| **R-14 decisions.md+gap 落盘** | 决策写前必 grill-me；status proposed→accepted 流转正确；gap CRITICAL 记录到阻塞区 |
| **R-15 clangd 校准**（P2） | 不排期；仅当 clangd 可用时作为 tree-sitter 校准源 |
| **R-16 多语言**（P2） | 不排期；主语言外走未索引→按需 Read |
| **R-17 parking-lot**（P2） | 需求池新增/暂缓需求记录到 `docs/parking-lot.md`，不丢失 |
| **R-18 多会话并发冲突**（P1 兜底） | 进程级物理锁（ProjectStateMutex）包裹写入事务；原子写 + fingerprint 兜底 |

### 16.2 迭代出口 Gate（I0–I5）

| 迭代 | 内容 | 出口 Gate |
|------|------|-----------|
| **I0** | R-01 校准协议（1.5 人日） | arm A ×3 完成，S/m/k 反解输出；方差评估 + 收紧建议；calibration.md 落盘 |
| **I1** | code-map 生成器 R-02/R-06（3.5 人日） | 试点 roguelike 生成三件套成功；router 预算达标；所有 calls 带 confidence；无 Pygments 回退 |
| **I2** | 骨架落地 R-03/R-04/R-07/R-08（2.5 人日） | 冷启动 7 步跑通；改文件后 stale 检测 + 阻断生效；预算守卫生效；收尾告警生效 |
| **I3** | 验收 R-05 + A/B 实测（1.5 人日） | SKILL.md ≤8KB；README 含收益边界声明；M1/M2/M3 至少各 1 组 A/B 数据；小仓阈值回代验证 |
| **I4** | P1 R-09~R-14（7.5 人日） | 分层索引、兼容读取、符号寻址、审核视图、三级信任、decisions 日志全部验收通过 |
| **I5** | P2（不排期） | 仅维护 parking-lot；不启动开发 |

---

## 17. 实施顺序与启动指引（给接手 agent）

### 17.1 顺序

```
I0 校准（R-01） → I1 生成器（R-02/R-06） → I2 骨架（R-03/R-04/R-07/R-08）
→ I3 验收（R-05 + A/B） → I4 P1（R-09~R-14） → I5 P2（不排期）
```

依赖关系：I0 的 S/m/k 反解结果供 I1 生成器调参；I1 的产物是 I2 骨架的输入；I2 跑通冷启动 7 步后才能做 I3 A/B 实测；I4 依赖 I2 的信任体系与 I1 的索引能力。

### 17.2 启动指引（Checklist）

1. [ ] 读本规格 + `AGENT.md` + `README.md` + `references/state-file-spec.md`（理解 v1 基线）
2. [ ] 确认工作区 `E:/Desktop/work/RPD-skill/` 与试点 `E:\Desktop\work\mix\roguelike` 可用
3. [ ] I0：设计 arm A 协议 → 在 roguelike 上跑 3 次反解 S/m/k → 输出 calibration.md
4. [ ] I1：选 tree-sitter Python 绑定（`tree-sitter` + `tree-sitter-cpp`），实现生成器；**禁用 Pygments**；为 C++ 配置 reference query
5. [ ] I1 验证：生成三件套，检查 router 预算、calls confidence、inverted index
6. [ ] I2：实现红线机检、预算守卫、增量落盘、收尾告警；打通冷启动 7 步
7. [ ] I3：SKILL.md 瘦身 ≤8KB；写 README 收益边界声明；跑 A/B（M1/M2/M3）
8. [ ] I4：按 R-09~R-14 顺序实现（R-09 → R-10 → R-11 → R-12 → R-13 → R-14）
9. [ ] 全程维护 `docs/parking-lot.md`（R-17）；不要动用户源码与 v1 产物
10. [ ] 每迭代结束：跑对应 Gate 检查表（§16.2），更新 decisions.md（grill-me 确认）

### 17.3 三条首要告诫（接手 agent 必读）

1. **map 是导航不是真相**：一切"基于 map 动手"都以 verified 为前提；unverified 必先 Read，stale 必禁动。宁可多 Read 一个文件，不可凭过期 map 改错代码。
2. **代码层 json 永远只读不手改**：任何需要"修 json"的场景 = 重跑生成器。手工编辑 code-map.* 会破坏 fingerprint 与信任链，属于红线。
3. **对外口径不可越界**：calls 边只叫"候选调用边 + 可验证锚点"，永远不叫"精确调用图"；对外文案与 README 都要守这条，否则误导用户信任度评估。

---

## 附录 A：需求池完整清单（P0/P1/P2）

| 编号 | 需求 | 优先级 | 迭代 |
|------|------|--------|------|
| R-01 | 校准协议（arm A ×3 反解 S/m/k） | P0 | I0 |
| R-02 | code-map 生成器（tree-sitter；C++ reference query；禁 Pygments） | P0 | I1 |
| R-03 | 双层 .rpd/ 落点 + 全动态路径 + 迁移备份 | P0 | I2 |
| R-04 | 红线机检（commit hash + fingerprint + 阻断） | P0 | I2 |
| R-05 | SKILL.md 瘦身 ≤8KB + README 收益边界声明 + 小仓库标准 | P0 | I3 |
| R-06 | calls confidence 标注（heuristic/resolved） | P0 | I1 |
| R-07 | 读取预算守卫（3k/15% + entry ≤300 token） | P0 | I2 |
| R-08 | 更新时机（收尾必写/功能完成即更/增量落盘/未落盘告警） | P0 | I2 |
| R-09 | 分层索引（router top_symbols PageRank 稀疏） | P1 | I4 |
| R-10 | 兼容读取 understand-anything（复用/降级+告警） | P1 | I4 |
| R-11 | 符号名路径寻址（function:path:name，不用纯行号） | P1 | I4 |
| R-12 | 审核者视图（五区块 + 归档） | P1 | I4 |
| R-13 | 三级信任（verified/unverified/stale） | P1 | I4 |
| R-14 | decisions.md + gap 落盘（grill-me 前置） | P1 | I4 |
| R-15 | clangd 校准 | P2 | I5（不排期） |
| R-16 | 多语言 | P2 | I5（不排期） |
| R-17 | parking-lot | P2 | I5（不排期） |
| R-18 | 多会话并发冲突（进程级物理锁兜底） | P1 | 已落地（state-guard ProjectStateMutex） |

## 附录 B：试点项目基线（I0/I3 引用）

- 路径：`E:\Desktop\work\mix\roguelike`
- 规模：src/ 18 文件 / 约 1745 行（对外口径）；含 tests/ 另 9 文件 / 约 2428 行（全量口径）
- 语言：C++（.h/.cpp）
- 用途：I0 arm A 校准、I1 生成器验证、I3 A/B 实测

---

*文档版本：v2-spec-1.0 · 作者：析客（requirement-analyst）· 日期：2026-08-03 · 状态：draft（待主理人/方向明确认）*
