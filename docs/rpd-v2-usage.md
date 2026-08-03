# RPD v2 使用规格（agent 运行参考）

> 本文件承载 v2 运行时细节，供 agent 在目标项目中使用 v2 能力时参考。
> 主控流程见 `SKILL.md`（瘦身后 ≤8KB），本文件为细节展开。

---

## 1. v2 冷启动 7 步

```
① 读 active-context.md（上次进度、下一步、阻塞、未落盘告警）
② 红线机检：读 code-map.meta.json；git diff map_commit..HEAD；fingerprint 比对
   → verified / unverified / stale 文件清单
③ 声明鲜度：一行声明"map 基于 commit <hash>，<N> 文件 verified，<M> 文件 stale"
   → 有 stale：先 Read 受影响文件或提示更新 map
   → understand-anything 降级：在此步显式告警（§5.3）
④ 按需加载：读 code-map.router.json（层1，若本会话尚未在 context）
   → 按任务需求经 router 查 entry_ref，读 code-map.json 单条 entry（≤300 token）
⑤ 定位：用 id = function:path:name 定位符号/文件/候选调用边（confidence 标注）
⑥ 动手：目标文件必须 verified（否则先 Read）；修改涉及符号 → 视为已验证/更新
⑦ 收尾：更新 active-context.md；增量落盘 code-map；未落盘 → 显式告警；
   决策变更 → decisions.md（grill-me 前置）；审核会话 → review-<date>.md
```

## 2. 红线机检协议（R-04）

- 数据源：`code-map.meta.json` 的 `map_commit` + `files.<path>.fingerprint`（sha256 全文）
- 会话启动：`git diff <map_commit>..HEAD --stat` 取变更文件，逐个比对 fingerprint
- 阻断规则：
  | 比对结果 | 信任 | 动作 |
  |----------|------|------|
  | fingerprint 一致 | `verified` | 可基于 map 定位 |
  | fingerprint 不一致 | `stale` | 禁止据此定位动手；强制 Read 该文件 |
  | 文件未在 map | `unverified` | 按需 Read；不阻断其他 verified 文件 |
- 无 `.git`：跳过 commit 比对，改全文件 fingerprint 抽查（`git_available: false`）

## 3. 读取预算守卫（R-07）

| 对象 | 硬上限 |
|------|--------|
| `code-map.router.json`（层1） | **≤3k token 且 ≤全码库 15%**（同时满足） |
| `code-map.json`（层2） | 不计入会话读取预算；按需读单条，从不整份喂入 |
| 单条 entry | **≤300 token** |
| `code-map.meta.json` | 极小（约 0.5–1k token） |

- 超限裁剪 top_symbols（保入口/高频/导出符号），meta 记录 `trimmed`
- 违规整份读 code-map.json → 审核视图「漂移」区块记一笔

## 4. 三级信任标注（R-13）

| 状态 | 判定 | 允许动作 |
|------|------|----------|
| `verified` | 本会话已 Read 且与 HEAD/fingerprint 一致 | 可基于 map 动手 |
| `unverified` | 来自 map、本会话未核对 | **动手前必须 Read** |
| `stale` | fingerprint 不匹配 | **禁止动手**；强制 Read + 重新生成/更新 entry |

> 默认态度：map 是导航，不是免 Read 通行证。宁可多 Read，不可凭过期 map 改错代码。

## 5. 审核者视图五区块（R-12）

| 区块 | 内容 |
|------|------|
| ① 鲜度 | map 基于的 commit；verified/unverified/stale 文件数；stale 列表 |
| ② 变更 | 自 map_commit 的 git diff 摘要；未落盘变更告警 |
| ③ 待确认 | decisions.md 中 proposed 决策；gap 漂移待裁决项 |
| ④ 漂移 | 文档决策 vs 代码实现不一致；router 预算超限；整份读 code-map.json 违规 |
| ⑤ 进度-代码对账 | 功能进度清单 vs code-map entry 状态逐项对账 |

归档：`.rpd/review-<date>.md`（同天多次追加 -2/-3）。

## 6. 主指标观测（M1/M2/M3）

| # | 指标 | 定义 | 对比口径 |
|---|------|------|----------|
| M1 | 理解连续性 | 有/无 map 时新会话是否保有理解（结构/符号/进度/决策）；再上手时间 | A/B 同任务两轮 |
| M2 | 定位成本 | 调用 vs 不调用 map 定位同一函数/接口调用的时间+token | 同任务两轮计时+token |
| M3 | 文档引用 | 定位 README/CHANGELOG/决策文档与代码对应关系的时间+token | 同上 |

- `net_tokens_to_first_action` 仅作次要观测，不作为 Gate 卡口
- 采集：`python scripts/rpd-metrics.py <root> record/report`，观测追加到 `.rpd/metrics.jsonl`

## 7. 重扫触发条件（默认不重扫）

1. 用户**明确要求**全量审查；
2. 目标符号**不知名**或无法仅靠 map 定位（如只知道 UI 文案）；
3. bug 排查**必须精确到某一行实现细节**（map 只有符号级信息）。

红线机检失败时强制重读单文件（不是全量重扫）。

## 8. 小仓库标准与收益边界

| 指标 | 小仓库阈值 |
|------|-----------|
| 源码文件数 | ≤ 20 个（src/ 下，排除 tests/generated/vendor） |
| 源码行数 | ≤ 1500 行（同上口径） |
| 符号数 | ≤ 150 个（推论值） |

- 判定：满足「文件数 ≤20 **或** 行数 ≤1500」即小仓库（取宽松口径）
- **收益边界声明**：小仓库 code-map 收益低于大仓库属**预期**；token 不是主指标，价值在于跨会话理解连续性与演进确定性——小仓会进化成大仓，map 从第一天就应建立。`required_h>85%` 不再作为停建 Gate。

## 9. understand-anything 兼容读取（R-10）

- 探测 `knowledge-graph.json`（`.claude/` → `.workbuddy/` → 项目根 → `.rpd/`）
- schema 匹配 → **只读复用**（绝不写）；不匹配 → 自建 code-map + 首条输出显式告警
- 无论复用/降级，`code-map.meta.json.understand_anything` 记录检测结果
