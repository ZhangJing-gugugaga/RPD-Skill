# Task Plan: RPD-skill 整体生命周期管理

> 重构于 2026-08-19 · 适用 skill: planning-with-files
> 范围：RPD-skill 从 v1 地基 → v2 核心 → I4 外扩 → 未来三支柱的**完整生命周期**。
> 原有 I4 迭代计划（上版 task_plan.md）作为「当前活跃迭代」嵌入本计划，**细节不丢失**。
> 资产清单详见 `findings.md`；本文件只放生命周期地图、阶段状态、关键资产摘要与活跃阶段详情。

> **🚀 新会话启动指引（必读）**：打开仓库后按序读 ① `findings.md`（资产台账 + 研究结论）→ ② `progress.md`（当前状态 + 5-Question Reboot 自检）→ ③ 回到本文件「当前阶段」。当前最优先任务 = **L2 Phase I4-0（基线核对，git 与 eval 基线已完成）**，红线见文末。勿从零重新调研，资产与决策均已落盘。

---

## Goal

把 RPD-skill 当作一个**持续演进的产品**来管理：在「不 push 除非授权、main 受保护、测试 0 failed 才 commit、视觉验证禁 mock、信息不全先提问」五条红线之下，按版本阶段推进能力交付，并把 I4 外扩与未来三支柱登记为明确的前后承接关系，使任意新会话都能从本文件恢复全局上下文。

## Lifecycle Map（L0–L3）

| Stage | 范围 | 状态 | 关键交付物 |
|-------|------|------|-----------|
| **L0 地基** | v1.0.0–v1.3.0（2026-06） | ✅ Done | 7 个 v1 脚本 + SKILL.md + README + 安全增强 + 暖启动 + state-guard + prd-validator + intent-router |
| **L1 核心** | v2.0.0–v2.0.2（2026-08-03） | ✅ Done | 4 个 v2 脚本（cold-start/code-map/decisions/metrics）+ 技术规格书 + 19 eval 场景 + ≤8KB SKILL.md + R-18 物理锁 |
| **L2 外扩** | I4 迭代（R-19~R-25） | 🔄 Active | 混合检索 / 边信息图 / 分层记忆 / PRD↔代码影响 / 渐进式暴露 / 依赖锁定 + parking-lot 治理 |
| **L3 未来** | 三支柱（TAM/UA 启示）+ parking-lot 升级 | 📋 Planned | 项目级记忆 / 项目级图谱 / 经验资产化（阶段 A→B→C，不进入任何具体 I 排期） |

## Current Phase

**L2 — I4 外扩迭代**（Phase I4-0 基线核对 → I4-9 交付），详见下方「阶段详情 · L2」。

---

## 已确认决策（项目级 Charter，grill-me 2026-08-19）

| 决策 | 结论 |
|------|------|
| I4 排期 | ✅ 采纳并排期六条 P1，落序 R-22+R-19 → R-25 → R-20/R-23 → R-21 |
| parking-lot | ✅ 认可四档触发条件（依赖就绪 / 用户信号≥3 / 成本收益翻转 / 定期复核）；R-24/26/27/28/29 维持冻结、按需升级 |
| 三支柱架构 | ✅ 认可为长期方向（A 补漏 → B 资产化/隔离 → C 组织级组合），不进入任何具体 I 排期 |

## 现有资产清单（摘要 — 全量见 findings.md）

| 类别 | 资产 | 状态 |
|------|------|------|
| 核心交付 | SKILL.md / README.md / CLAUDE.md / TRAINING.md / LICENSE / _user_meta.json | 活跃 |
| 运行时脚本 | 12 个 `.py`（v1×8 + v2×4，见 findings.md 映射） | 活跃 |
| 文档 | docs/rpd-v2-technical-spec.md（17 节+2 附录）· rpd-v2-usage.md · research-report-ua-tam-optimization.md | 活跃 / I4 依据 |
| 参考模板 | references/ 6 件（brainstorming-flow · prd-template · state-file-spec · state-schema.json · keyword-map.json · rpd-v2-layout） | 活跃 |
| 评估 | eval/ 5 个独立场景 .md（A/B/C/D/S）+ run-eval.py 内联断言（E/F/G/H/I/O/P/Q/R/T/U/V/W）+ X 行为 = 19 场景 | 活跃 |
| 资产与推广 | assets/hero.png · example-state.md · promo/社区文案 v1 & v2 | 活跃 |
| 分发元数据 | .claude-plugin/{plugin,marketplace}.json · .github/{FUNDING, ISSUE_TEMPLATE×2, PULL_REQUEST_TEMPLATE, workflows/eval.yml} | 活跃 |
| 规划与研究 | task_plan.md / findings.md / progress.md（本生命周期三件套）· .workbuddy/research-materials(10+) · artifacts/审查报告 · memory/(2) · logs/ | 过程物 |

---

## 阶段详情

### Phase L0: v1 地基（v1.0.0–v1.3.0）— ✅ Done
- [x] v1.0.0 初始版本（2026-06-05）
- [x] v1.1.0 安全增强 SEC-001~007
- [x] v1.2.0 暖启动 + state-guard + prd-validator + intent-router
- [x] v1.3.0 SEC-001/002 修复 + Spec 漂移 + Git 并发 + Hard Constraints
- **交付物：** 7 脚本（intent-router / security-scanner / project-scanner / gap-analyzer / state-validator / state-guard / prd-validator）+ SKILL.md + README
- **验收（历史）：** 版本史见 CLAUDE.md；eval 基线在 L1 重构时建立

### Phase L1: v2 核心（v2.0.0–v2.0.2）— ✅ Done
- [x] v2.0.0 主指标重构 M1/M2/M3 + code-map 两层导航 + 取消停建 Gate + decisions.md grill-me + v1 兼容读取降级 + SKILL.md ≤8KB
- [x] v2.0.1 R-18 升级：state-guard 进程级物理锁防多 Agent 竞态覆写
- [x] v2.0.2 README 身份中性化 + 删平台插件目录 + intent-router 量词修复 + 文档并为一层半
- **交付物：** 4 新脚本（rpd-cold-start / code-map-generator / rpd-decisions / rpd-metrics）+ run-eval.py（19 场景）+ 技术规格书 + 用法文档 + rpd-v2-layout
- **验收（历史）：** 19 eval 场景通过（CLAUDE.md / TRAINING.md 记录为 18/18，README 记为 19；以 run-eval.py 实际运行数为准，待 L2 Phase 0 复跑核对）

### Phase L2: I4 外扩迭代 — 🔄 Active
> 基于 `docs/research-report-ua-tam-optimization.md`（537 行，26 参考文献）与已确认三项决策编制。
> 硬约束：router ≤3k / 单条 code-map ≤300 token、R-10 向后兼容、红线机检持续有效。

#### Phase I4-0: 基线核对与实施准备
- [x] git status 核对（2026-08-19）：当前在 `main`（受保护），工作区干净，仅 6 个未跟踪文件（计划三件套+研究报告+promo+.workbuddy），无已跟踪文件改动；实施须开 `type/scope` 分支
- [x] 复跑 eval 基线（2026-08-19）：`python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0），仓库未被污染；README 记 19、TRAINING.md 记 18 为文档口径差异，以实际 19 为准
- [ ] 通读 `SKILL.md`、`docs/rpd-v2-technical-spec.md`（重点：§3 code-map schema、§6 红线机检、§7 预算守卫、附录 A 需求池 R-01~R-18）
- [ ] 盘点 12 个 scripts 的职责边界（intent-router / code-map-generator / state-guard / rpd-decisions / gap-analyzer 等）
- [ ] 起草 R-19~R-25 需求编号占位（入规格附录 A 草案，待各 Phase 验收后转正）
- [ ] 确认 R-22 向量通道依赖取舍（见 Key Questions Q1）
- **Status:** complete
- **验收：** 基线测试数字落盘 progress.md（✅）；新增需求编号草案写入规格；依赖取舍有结论

#### Phase I4-1: R-22 混合检索（BM25 + 向量 + RRF）
- **涉及文件：** `scripts/code-map-generator.py`（检索侧）、新增 `scripts/retriever.py`（或并入）、`.rpd/` 检索逻辑、测试 `eval/`
- [ ] BM25 词典通道：文件名 / 符号名 / 仓库名等精确词命中
- [ ] 向量通道：语义检索（若 Q1 结论为"零依赖先行"，此通道打标 TODO 并在报告中注明降级）
- [ ] RRF 融合排序（Reciprocal Rank Fusion）
- [x] 单元测试：语义描述（如"支付重试逻辑"）可回退定位；精确词命中不劣于现有符号寻址（R-11）
- **Status:** complete
- **验收：** 检索"支付重试逻辑"可定位 code-map 层2 entry；单条注入 ≤300 token 预算不破；精确词命中不劣于现行

#### Phase I4-2: R-19 边信息复用（节点-边最小图）
- **涉及文件：** `code-map.json` schema（层2 entry 加 `edges`）、`scripts/code-map-generator.py`、R-10 复用逻辑（§5）、`docs/rpd-v2-technical-spec.md` §3.3
- [ ] schema 扩展：`edges`（类型 / 权重 / 目标节点），复用 UA 的 35 种边 / 8 大类 + 权重约定（contains 1.0 / calls 0.8 / imports 0.7 / depends_on 0.6 …）
- [ ] 从 R-10 读入的 `knowledge-graph.json` 映射边数据；引用完整性校验（悬挂边剔除 + 告警）
- [x] 查询能力：谁调用 X / X 依赖谁 / X 属于哪个架构层
- [x] 无 UA 图谱时的兜底路径（README/code 直读，不回退为自建全量解析管线）
- **Status:** complete
- **验收：** 层2 entry 可回答依赖/调用/归属三类问题；旧项目 schema 版本白名单 + 降级不崩

#### Phase I4-3: R-25 依赖版本锁定
- **涉及文件：** `code-map.meta.json`（依赖清单 + commit/指纹）、`scripts/state-guard.py` 或 `code-map-generator.py`
- [x] 快照绑定依赖清单 + git commit hash / 结构指纹
- [x] 依赖漂移检测：依赖/版本变化 → 提示重新生成图谱，禁止基于过期结构作答
- [x] 与三级信任（verified/unverified/stale）状态机衔接
- **Status:** complete
- **验收：** 模拟依赖漂移可被检测并提示；信任状态机不受影响；红线机检协议（§6）不回归

#### Phase I4-4: R-20 PRD↔代码影响分析
- **涉及文件：** 新增 `scripts/impact-analyzer.py`；复用 R-19 边；PRD 节点（domain/flow/step）↔ file/function 双向映射
- [ ] changedNodes / affectedNodes（1-hop）/ affectedLayers / blast radius 风险分级（Critical/High/Medium/Low）
- [ ] "改 PRD 需求 → 定位受影响代码模块并分级"（M2 变更闭环）
- [ ] "改代码 → 反查受影响 PRD 需求"
- [ ] 依赖 R-19 边数据质量，P1-b 排期（R-20 在 R-19 之后）
- **Status:** complete
- **验收：** M2 PRD 变更闭环可演示；双向映射均有输出；失败回退到现有直读路径

#### Phase I4-5: R-23 渐进式暴露
- **涉及文件：** `SKILL.md` 注入策略、预算守卫（§7）、冷启动 7 步（§9）
- [x] 三层暴露：router 层1 常驻（≤3k）→ code-map 层2 按需（≤300/条）→ 深入追问才注入语义摘要
- [x] 越级注入被守卫拦截；失败回退到 README/code 直读路径
- [x] 引入"本任务注入上限"硬预算（条目数 + 字符数双预算，参照 TAM 三重预算）
- **Status:** complete
- **验收：** 冷启动注入不超预算；双预算守卫生效；I0~I3 既有行为不回归

#### Phase I4-6: R-21 L0-L3 分层记忆
- **涉及文件：** `decisions.md` 结构（§12）、`scripts/rpd-decisions.py`、`.rpd/` 目录规格（§2）
- [ ] L0 原始证据层（对话/扫描输出，仅留指纹或路径引用，不常驻）→ L1 原子决策/需求事实 → L2 场景块（PRD 生成 / 接手半成品 / 继续开发）→ L3 项目画像
- [ ] 分层读写与过期规则；"高层存 Markdown、低层存证据引用"
- [ ] 检索回退：L2/L3 引导，需要具体事实时回退 L1/L0
- **Status:** complete
- **验收：** 跨会话可回溯决策依据（L0）；PRD 生成默认供 L2 不展开 L1/L0；单层膨胀受控

#### Phase I4-7: parking-lot 治理机制
- **涉及文件：** `docs/rpd-v2-technical-spec.md`（新增 parking-lot 附录）、可选 `scripts/rpd-parking-lot.py`
- [ ] 四档触发条件落地：依赖就绪 / 用户信号（≥3 次明确询问）/ 成本收益翻转 / 每迭代末定期复核
- [ ] 升级三要素：明确需求编号 + 影响范围 + 预算评估（杜绝"顺手混入"）
- [ ] 条目：R-24 经验资产化 / R-26 ACL / R-27 全图影响（2-hop+）/ R-28 团队记忆 / R-29 多语言
- **Status:** pending
- **验收：** 触发条件可机检；升级路径清晰；parking-lot 条目不在对外承诺中宣称"已规划交付"

#### Phase I4-8: 测试与验证（0-信任验证）
- [ ] 每个 fix 独立 `type/scope` 分支；`pytest -q` 0 failed 才 commit；**不 push 除非用户明确同意**
- [ ] eval 基线对比（M1 理解连续性 / M2 PRD 变更闭环 / M3 文档引用），不照搬 agent 声称
- [ ] 视觉/UI 类改动必须真实运行 + 截图验证（**禁止 mock 注入**，用真实数据验证）
- [ ] 回归：L0/L1 交付物、红线机检、预算守卫不回归
- **Status:** pending
- **验收：** 全量测试 0 failed；eval 指标无劣化；视觉改动有真实截图证据

#### Phase I4-9: 文档与交付
- [ ] 更新 `docs/rpd-v2-technical-spec.md`（R-19~R-25 转正入附录 A、parking-lot 附录、验收标准 §16）
- [ ] 更新 `SKILL.md`（≤8KB 约束内；超限则按 CLAUDE.md 约定处理）与 `docs/rpd-v2-usage.md`
- [ ] 沉淀经验到 memory + `.project-state.md`
- [ ] 向用户交付：改动清单 + 验证证据 + 下一步（I5 或 parking-lot 升级评估）
- **Status:** pending
- **验收：** 文档与实现一致；交付物完整可审

### Phase L3: 未来三支柱 / parking-lot 升级 — 📋 Planned
- [ ] 阶段 A（补漏）：当前迭代未覆盖的低成本增强，按需从 parking-lot 升级
- [ ] 阶段 B（资产化/隔离）：经验资产化（R-24）/ ACL（R-26）路线评估
- [ ] 阶段 C（组织级组合）：项目级记忆 + 项目级图谱 + 经验资产化组合管理；需数据模型验证后再评估
- **Status:** planned
- **触发条件：** 见 I4-7 parking-lot 四档机制；当前无活跃任务，不进入 I4 排期（用户决策 C）

---

## 硬约束（红线，全程有效）
1. 不 push 除非用户明确同意
2. main 受保护，实施走 `type/scope` 分支
3. 测试 0 failed 才 commit
4. 视觉验证必须真实截图（禁 mock 注入）
5. 信息不全先提问，不瞎猜
6. 预算守卫不破：router ≤3k / 单条 code-map ≤300 token
7. R-10 向后兼容：版本白名单 + 降级处理
8. 红线机检 + 三级信任持续有效

## Key Decisions（已拍板，实施时直接执行）

| # | 决策 | 依据 | 生效阶段 |
|---|------|------|---------|
| Q1 | R-22 混合检索：**零外部依赖先行**（BM25+RRF 双通道），向量通道打标 TODO 并在报告中注明降级 | 用户"务实主义"偏好 + 研究报告推荐 | I4-1 |
| Q2 | R-19 边数据：**仅复用 R-10 `knowledge-graph.json`**，不自建 AST 边抽取管线 | 规避自建全量解析；研究报告推荐 | I4-2 |
| Q3 | R-20 PRD 节点来源：**从现有 PRD 文档解析**（`references/prd-template.md` 结构），不新增 domain 注册机制；若解析覆盖不足则在 I4-4 实施时评估 | 最小改动原则 | I4-4 |
| Q4 | R-23 三级暴露阈值：**第三级语义摘要注入上限 ≤500 token**；"深入追问"判定 = 用户连续 2 轮追问同一符号/模块的深层语义 | 参照 TAM 三重预算 + 预算守卫 §7 | I4-5 |
| Q5 | I4 验收口径：**M1/M2 纳入 eval 基线作为 I4 出口 Gate**；M3 文档引用作为观测项不阻断 | 研究报告 §4.6 + v2 主指标定义 | I4-8 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| （L2 实施阶段发生再记录） | 1 | — |
| 研究阶段：parkin-lot 笔误 | 1 | 统稿修复为 parking-lot |
| 研究阶段：Ch2 Governed Memory 论文归属误述 | 1 | round1 审稿退回 → 修订 → round2 PASS |
| 生命周期重构：原 task_plan.md 仅 I4 范围 | 1 | 升级为 L0–L3 全生命周期，I4 细节保留为活跃子阶段 |

## Notes
- **权威依据**：`docs/research-report-ua-tam-optimization.md`（第 4 章 R-19~R-29、第 5 章三支柱）
- **进度通报**：每完成一个 Phase 更新本文件 Status 与 `progress.md`
- **经验沉淀**：每次修复后更新 memory
- **重构说明**：本文件由「I4 单次迭代计划」升级为「整体生命周期计划」，L0/L1 历史阶段据 CLAUDE.md 版本史回填，L2 沿用原 I4 计划，L3 为规划方向。
