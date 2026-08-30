# I4 交付完整性审计（task_plan 未勾 checkbox 对账）

> 生成时间：2026-08-30 16:1x（Asia/Shanghai，I4 Advancer 轮）
> 基线 commit：`709a6fe`（`verify(I4-closeout): …§八 H3 合并前风险审计验证通过 [verifier]`）
> 口径：沿用 `docs/automation-governance-proposal.md` §零（R-1 当前值=写入时刻快照 + 复现命令 / R-2 来源=commit hash / R-3 不因数值变旧追更）
> 状态：**只做核对与记录，不修改 `task_plan.md`**（其结构/勾选属 Verifier 与用户权限）

---

## 0. 缘起：Verifier 检查项 6 有一个结构性盲点

`.workbuddy/automation-rules.md` 的 0-trust 清单第 6 项「计划一致性」，PASS 标准写的是 *task_plan.md Phase 状态 vs 实际* —— 实际执行中它只核对了 **`Status:` 字段**（十个 Phase 全 `complete`、pending=0）就判 PASS。

但 `task_plan.md` 里 Phase 下面还有**逐条 checkbox**。实测：I4-0~I4-9 共 **27 个 checkbox 处于未勾状态**（4+3+2+4+3+3+4+4），而它们所属的 Phase 无一例外都标着 `complete`。

| 项 | 值 | 复现命令 |
|---|---|---|
| Phase Status 全 complete | 10 / 10 | `grep -c "^\- \*\*Status:\*\* complete" task_plan.md` |
| **未勾 checkbox 数** | **27** | `awk '/^#### Phase I4-0/,/^### Phase L3/' task_plan.md \| grep -c "^- \[ \]"` |
| 含未勾项的 Phase | I4-0(4) / I4-1(3) / I4-2(2) / I4-4(4) / I4-6(3) / I4-7(3) / I4-8(4) / I4-9(4) = **27** | 同上（I4-3 与 I4-5 全勾） |

于是出现两种可能，二者对 H3（合并进 main）的含义完全不同：

- **A. 清单滞后** —— 功能已实现，只是没人回头勾 → 合并安全，勾上即可
- **B. 假 complete** —— 功能其实没做，Status 被提前标完成 → 合并会把缺口带进 main

本文用三重对账把 A / B 分开。

---

## 1. 方法：三重对账，任一为凭

不采信 Status、不采信任何 agent 自述。每项 checkbox 必须至少命中以下之一：

1. **代码符号**：`grep` 到对应实现（函数 / 常量 / schema 字段），落到 `file:line`
2. **eval 断言**：`scripts/run-eval.py` 中存在对该行为的 `assert`（19/19 PASS 即为其持续生效的证据）
3. **规格章节**：`docs/rpd-v2-technical-spec.md` 有对应章节 / 附录条目

三者皆无 → 判为 **未实现**；仅能落「过程动作」（如"通读文档"）→ 判 **不可机检**，注明。

---

## 2. 结论总表（27 项）

| 判定 | 数量 | 含义 |
|---|---|---|
| ✅ **已实现（清单滞后）** | **22** | 其中 **21 项**三重对账直接命中（功能在库且被 eval 断言持续守护）；**1 项**（I4-0① 通读）为产物级间接证据 → 只差勾选 |
| ⚠️ **临界** | **1** | I4-9 ② SKILL.md ≤8KB：LF 口径合规但余量仅 76 字节，CRLF 口径已破线 → 见 §4 F1 |
| 🔍 **不可机检（流程纪律）** | **4** | I4-8 全部 4 项：属工作方式约束，无代码产物可断言 → 见 §4 F3 |

**没有一项判为「未实现」** → I4 的 `complete` 不是假的，是**清单没跟上实现**。H3 合并的安全性论证不受影响。

---

## 3. 逐 Phase 证据（已实现 22 项 + 临界 1 项 + 流程 4 项）

### I4-0 基线核对（4 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | 通读 SKILL.md + spec（§3/§6/§7/附录A） | ✅ 间接 | 产物已落地：spec 新增 `### 3.6 edges 边信息（R-19）`:294 / `### 3.7 PRD↔代码影响（R-20）`:306 / `### 3.8 渐进式暴露（R-23）`:314 / `## 3.9 L0-L3 分层记忆（R-21）`:572；`## 16. 验收标准`:677。未读不可能写出这些章节 |
| ② | 盘点 12 个 scripts 职责边界 | ✅ | SKILL.md 工具箱表（:94–110，15 行）已列全部脚本；`grep -c "\.py" SKILL.md` = **30** 处引用 |
| ③ | 起草 R-19~R-25 编号占位（入附录 A） | ✅ 已转正 | spec §16.1 `:701–711` **7 个编号全在**（R-19/20/21/22/23/24/25），且 R-24/R-26~R-29 标注 parking-lot 冻结 → 超出"占位"要求 |
| ④ | 确认 R-22 向量通道依赖取舍 | ✅ | Q1 已入 task_plan §Key Decisions；`retriever.py:10` `vector channel : R-22 Q1 - disabled`、`:374` note、`:444` 运行时输出；eval `:745` 断言 `channels.vector.enabled is False` 且 `:746` 断言 note 含 `TODO` |

### I4-1 R-22 混合检索（3 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | BM25 词典通道 | ✅ | `retriever.py:90` `# --- BM25 (zero dependency)`、`:112 bm25_rank`、`:141 search_bm25`；eval `:736–744` 断言精确词 `Game` 命中且 `channel == "exact"` 排第一 |
| ② | 向量通道打标 TODO | ✅ | 同上 ④；eval `:745–746` |
| ③ | RRF 融合排序 | ✅ | `retriever.py:42 RRF_K = 60`、`:185 rrf_fuse`、`:201 build_results`；eval `:744` 断言融合后 exact 仍居首（R-11 不劣化） |

### I4-2 R-19 边信息（2 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | `edges` schema 扩展 + 权重约定 | ✅ | `code-map-generator.py:54 KG_EDGE_WEIGHTS`（calls 0.8 / contains 1.0 / imports 0.7 / depends_on 0.6）、`:59 DEFAULT_EDGE_WEIGHT`、`:461 "edges": []`；spec `:239–240` + `### 3.6`:294；eval `:1293 ✅ R-19 edges` |
| ② | 从 R-10 `knowledge-graph.json` 映射 + 引用完整性校验 | ✅ | `:738` 只读加载（4 个候选路径）、`:765 attach_kg_edges`（`:768` 悬挂边剔除、`:778` 计数 `dangling_dropped`）、`:825` R-10 探测（只读不写）；eval `:757–815` 构造含 `sym:ghost` 的 KG 验证悬挂剔除、`:1293` 汇总断言 |

### I4-4 R-20 PRD↔代码影响（4 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | changed/affected(1-hop)/layers/blast 分级 | ✅ | `impact-analyzer.py:192 _grade_blast`（`:195 Critical` / `:197 High` / `:199 Medium` / `:200 Low`）、`:265 analyze_prd_to_code`（`:308 blast_radius`）；spec `### 3.7`:306 |
| ② | 改 PRD → 定位受影响代码并分级 | ✅ | `:265` + eval `:990–995`（断言 1-hop 经 R-19 边带出 `helper`） |
| ③ | 改代码 → 反查受影响 PRD 需求 | ✅ | `:313 analyze_code_to_prd` + eval `:1001–1008`（含 `:1008` 未命中符号不猜） |
| ④ | 依赖 R-19 边质量，P1-b 排期 | ✅ | spec `:735` 实施顺序 `R-22→R-19→R-25→R-20→R-23→R-21`，R-20 确在 R-19 之后 |

### I4-6 R-21 分层记忆（3 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | L0 证据 → L1 原子 → L2 场景 → L3 画像 | ✅ | `memory-layers.py:61 LAYERS = ("L0","L1","L2","L3")`、`:62 WRITABLE`；spec `## 3.9`:572 |
| ② | 分层读写与过期规则 | ✅ | `:64 BLOAT_L1=500` / `:65 BLOAT_L2=200`；`--expired` 标记 + `--drop-clean` 删除（docstring :28）；eval `:1072–1174` |
| ③ | 检索回退（L2/L3 引导，需事实时回退 L1/L0） | ✅ | docstring `:24–26`；`--fact`→L1、`--evidence`→L0（:38–39）；eval `:1174 ✅ R-21 memory: …fallback…` |

### I4-7 parking-lot 治理（3 项）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | 四档触发条件可机检 | ✅ | `parking-lot.py:10 T2 user_signal …(3)`、`:31 --audit`；eval `:1193` 断言 `landed` 含 R-19/R-21（依赖就绪判定生效）；spec `## 附录 C`:797 + `### 四档触发条件（机检可查）`:801 |
| ② | 升级三要素（编号 + 影响范围 + 预算） | ✅ | `:32 --upgrade --id --impact --budget`；eval `:1207–1234` 缺任一要素被拒；spec `### 升级三要素`:810 |
| ③ | 五条目登记（R-24/26/27/28/29） | ✅ | `:70–88` 五条目含 `deps` 与 `notes`；eval `:1252 ✅ R-24/R-26~R-29`；spec `### 登记条目（5）`:818 |

### I4-9 文档与交付（4 项，3 落地 1 临界）

| # | checkbox | 判定 | 证据 |
|---|---|---|---|
| ① | 更新 spec（R-19~R-25 转正 + parking-lot 附录 + 验收 §16） | ✅ | §16.1 `:701–711` 7 编号转正；`## 附录 C`:797；`## 16. 验收标准`:677 + `### 16.2 迭代出口 Gate（I0–I5）`:713 |
| ② | 更新 SKILL.md（**≤8KB**）与 usage | ⚠️ **临界** | SKILL.md 工具箱表已更新（:94–110），但体积见 §4 F1 —— **未违反，但余量仅 76 字节** |
| ③ | 沉淀经验到 memory + `.project-state.md` | ✅ | `.project-state.md` 存在（4659 B，2026-08-21 12:23）；`.workbuddy/memory/` 有 2026-08-18~22 / 29 / 30 共 7 份日志 + `MEMORY.md` |
| ④ | 向用户交付（改动清单 + 验证证据 + 下一步） | ✅ | 收官报告 commit `27f7fd5`（2026-08-21 14:13:45）；`docs/handoff-automation-2026-08-19.md` 260 行 |

---

## 4. 三个发现

### F1 ⚠️ R-05（SKILL.md ≤8KB）处于临界：LF 合规、CRLF 破线

> 差点误报：工作区 `wc -c SKILL.md` = **8235** > 8192，初判"违反硬约束"。深挖后是**行尾口径问题**，不是违规。

| 口径 | 实测 | vs 8192 | 复现命令 |
|---|---|---|---|
| 工作区文件（Windows CRLF） | **8235 B** | **超 43 B** | `wc -c SKILL.md` |
| Git 对象（LF，仓库真值） | **8116 B** | 余量 **76 B**（0.93%） | `git show HEAD:SKILL.md \| wc -c` |
| 字符数 | 5341 | — | `wc -m SKILL.md` |

**根因**：`core.autocrlf=true` + 无 `.gitattributes` → 检出时 119 行各加 1 个 CR，恰好 8116+119=8235（`grep -c $'\r' SKILL.md` = **119**，`wc -l SKILL.md` = **119**，完全对得上）。**Git 里存的仍是 LF 的 8116**。

**引入点**：`4c40084`（2026-08-21 12:24:36）`feat(I4-9): I4 文档交付（… SKILL 工具箱 18 行 ≤8KB …）` —— 该 commit 按 LF 口径（8116）**声明成立**，非造假。体积演变实测：v1 期 8325→44872 B 超限 → `4b0352a` 9543 → `35efe9a` 7583（v2.0.0 瘦身达标）→ `3296420` 7927 → `1081696` 7877 → `4c40084` 8116。

**为什么值得记**：76 字节 ≈ 2~3 行中文。**任何一次"顺手给 SKILL.md 加一行工具说明"都会打破 R-05**，而当前没有任何机检会拦住它（`i4-gate.py` 不检查 SKILL.md 体积）。

**建议（有先后依赖）**：
1. 若要给 `i4-gate.py` 加体积守卫，**必须用 LF 口径** `git show HEAD:SKILL.md | wc -c`，**不能用 `wc -c SKILL.md`** —— 后者在 Windows 上会恒定误报（8235 > 8192 直接让 eval FAIL，反过来卡死红线 3）
2. 若先压缩 SKILL.md（如精简工具箱表措辞腾出 ≥200 B）→ 再加守卫，两个口径同时安全

### F2 task_plan 的「12 个 scripts」已滞后 6 个

`ls scripts/*.py | wc -l` = **18**。task_plan §现有资产清单 与 I4-0 ② 均写「12 个 `.py`（v1×8 + v2×4）」。差值 6 = I4 新增的 `retriever.py` / `impact-analyzer.py` / `exposure-guard.py` / `memory-layers.py` / `parking-lot.py` / `i4-gate.py`。

属**描述滞后**，非缺陷；但接手 agent 按「12」去盘点会漏掉 6 个 I4 主力脚本。建议在 I4-0 ② 勾选时一并更正为 18（Verifier 权限）。

### F3 I4-8 的 4 项属流程纪律，其中 1 项与现状存在事实偏离

| # | checkbox | 现状（实测） |
|---|---|---|
| ① | 每个 fix 独立 `type/scope` 分支 | ⚠️ **偏离**：I4 全部提交在同一个 `automation/i4-l2` 分支上（`git log --oneline origin/main..HEAD \| wc -l` = 45，全在该分支）。这是自动化串行节奏的既定约定（见 `.workbuddy/automation-rules.md`），与 task_plan 硬约束 2「实施走 `type/scope` 分支」字面不一致 —— **人工开发时须回到 type/scope 约定，自动化轮次沿用单分支** |
| ② | eval 基线对比 M1/M2/M3 | ✅ 已被 eval 场景 V（`:1304`）覆盖；spec `:623` 明确 M2 为机检项 |
| ③ | 视觉/UI 改动真实截图（禁 mock） | N/A —— I4 无 UI 改动，纯 CLI + Markdown；红线不适用 |
| ④ | 回归（红线机检 / 预算守卫不回归） | ✅ `scripts/i4-gate.py` 常驻，Verifier 每轮补跑（`--json` → `"pass": true`） |

---

## 5. 处置建议

| # | 动作 | 归属 | 依赖 |
|---|---|---|---|
| 1 | 勾选 I4-0①~④ / I4-1①~③ / I4-2①② / I4-4①~④ / I4-6①~③ / I4-7①~③ / I4-9①③④ 共 **22 项** | **Verifier**（Advancer 禁改 `task_plan.md`） | 无 |
| 2 | I4-9② 暂**不勾**，按 F1 先压缩再加守卫 | 用户拍板 → Advancer 执行 | 需授权（`SKILL.md` 与 `scripts/` 虽在 Advancer 写入范围，但压缩属内容改动，建议先确认） |
| 3 | I4-0② 的「12」改为「18」 | Verifier（勾选时顺带） | 同 1 |
| 4 | I4-8① 加注「自动化轮次例外」 | 用户 / Verifier | 无 |

**对 H3（合并进 main）的影响**：无新增阻塞。本审计排除了「假 complete」的可能，§八 的合并面结论（17 纯新增 / 4 文件 14 处删改）继续成立。
