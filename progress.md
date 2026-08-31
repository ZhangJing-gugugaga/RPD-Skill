# Progress Log — RPD-skill 整体生命周期

## Session: 2026-08-19（纠错：创建 WorkBuddy Todo）

### 本次会话：Agent 团队误建 → 清理 → 创建真实 WorkBuddy Todo
- **Status:** complete
- **错误：** 第一次用 TeamCreate + 后台 Agent 创建了自主运行的 agent 团队，用户要的是 WorkBuddy 项目 todo（UI 可审查可微调）。
- **清理：** 删除团队 rpd-i4-automation（TeamDelete 成功）；后台 agent 已 killed。
- **正确创建：** 用 `mcp__wb-issues__todo_create` 创建 10 条 WorkBuddy todo（I4-0~I4-9）：
  - 先查 `todo_statuses`（claim/running/paused/done）+ `project_members`（owner id: 6c5fe5b9），不猜参数
  - 每条带 title/description/assignee/priority/tags/start_date/due_date/status_id
  - I4-0 标进行中（git+eval 基线已完成）；I4-1~9 标待开始
- **Todo ID 清单：** I4-0(rhb7Wp) / I4-1(rcW4RS) / I4-2(raUZs4) / I4-3(rnAxRa) / I4-4(rsO1C9) / I4-5(rvXVu0) / I4-6(rZEKBI) / I4-7(r7Madr) / I4-8(rMym7V) / I4-9(rDdzl2)
- **保留资产：** automation/i4-l2 分支（commit 854a67f）+ .workbuddy/automation-rules.md + 计划三件套 + Key Decisions Q1~Q5

---

## Session: 2026-08-19（自动化启动 · 双 Agent 配置）

### 本次会话：双 Agent 自动化配置与首个 tick 启动
- **Status:** complete（配置完成，Advancer 运行中）
- **用户决策：** 推进 reasoning / 验证 default · FAIL 自动 revert+重试 · 仅 automation 分支手动 merge · 严格 1h 交替
- Actions taken:
  - 创建 `automation/i4-l2` 分支（从 main）
  - 清理计划：Key Questions → **Key Decisions**（Q1–Q5 全部转为明确决策，计划无"本轮不做"类延后语）
  - 写入 `.workbuddy/automation-rules.md`（Advancer + Verifier 完整规则 + 7 项 0-trust 验证清单 + 串行节奏）
  - 提交基础文件到 automation 分支（commit `854a67f`：计划三件套 + 规则 + 研究报告）
  - 创建团队 `rpd-i4-automation`
  - 创建 Task #1（I4-0 基线核对收尾）
  - 启动 **Advancer agent**（reasoning 模型，后台运行，agent_id: advancer@rpd-i4-automation）
- Files modified: task_plan.md（Key Decisions + L3 措辞）· .workbuddy/automation-rules.md（新建）· progress.md（本日志）
- 当前状态：**Advancer 在后台推进 I4-0**；完成后通知 team-lead → 启动 Verifier 验证 → PASS 标 complete / FAIL revert → 启动下一 Advancer
- Key Decisions 摘要：
  - Q1: R-22 零外部依赖先行（BM25+RRF），向量打标 TODO
  - Q2: R-19 仅复用 R-10 knowledge-graph.json，不自建 AST
  - Q3: R-20 从现有 PRD 文档解析，不新增 domain 注册
  - Q4: R-23 第三级语义摘要 ≤500 token，"深入追问"= 连续 2 轮追问
  - Q5: M1/M2 纳入 eval 基线作为 I4 出口 Gate

---

## Session: 2026-08-19（配置收尾 · 基线条化）

### 本次会话：基线条化，确保新会话可立即接手
- **Status:** complete
- **目标：** 用户要求"把项目资产、计划、任务配置好，确保新开会话能立即基于已有资产和任务开始干活"。
- Actions taken:
  - `git status` / `git branch` 核对：当前 `main`（受保护），工作区干净，仅 6 未跟踪文件（计划三件套+研究报告+promo+.workbuddy）
  - `python scripts/run-eval.py` 完整跑批：**19/19 PASS**（A~X，exit 0），仓库未被污染
  - 澄清 README(19) vs TRAINING(18) 口径差异：以实际 19 为准
  - `task_plan.md` 顶部加「新会话启动指引」；I4-0 的 git 核对 + eval 基线两项标记完成
  - `progress.md` Test Results 填入真实基线数字
- Files modified: task_plan.md（启动指引 + I4-0 基线项）· progress.md（Test Results）
- 现状：新会话按启动指引读三件套即可从 L2 I4-0 中段直接接手（剩余：通读规格 / 盘点脚本 / 起草 R-19~R-25 / 拍板 Q1~Q5）

## Session: 2026-08-19（生命周期重构）

### 本次会话：planning-with-files 配置（整体生命周期）
- **Status:** complete
- **触发：** 用户要求"使用 planning-with-files，为本项目配置好计划、任务和已有资产，本项目是 RPD-skill 的整体生命周期"
- **关键判断：** 原 `task_plan.md` 仅覆盖 I4 单次迭代，需升级为 L0–L3 全生命周期计划；I4 细节保留为活跃子阶段，不丢失。
- Actions taken:
  - 全量盘点仓库资产（Glob 全树 + 精读 README / CLAUDE / TRAINING / SKILL / 原有三件套）
  - 重构 `task_plan.md`：L0 地基（v1.0–1.3）→ L1 核心（v2.0–2.0.2）→ L2 外扩（I4 Phase 0–9）→ L3 未来三支柱；含生命周期地图、资产摘要、决策、红线、Key Questions
  - 重构 `findings.md`：新增全量资产台账（A–H 八类，含 12 脚本阶段映射、19 eval 场景归属、分发元数据、研究过程物）
  - 本文件新增本次会话日志
- Files created/modified:
  - task_plan.md（重构为生命周期计划）
  - findings.md（新增资产台账 + 生命周期上下文）
  - progress.md（本会话日志）
- 待办（下一步）：
  - 用户确认生命周期框架解读无误（尤其：I4 作为活跃子阶段、L3 仅规划）
  - 进入 L2 Phase I4-0：git status 核对 + 复跑 eval 基线 + 通读规格 + 起草 R-19~R-25 编号 + 拍板 Key Questions Q1~Q5

---

### 前置阶段：深度研究（已完成，L2 输入）
- **Status:** complete
- Actions taken:
  - 调度深度研究团队 5 阶段工作流，完成 5 章研究报告并全部审稿通过
  - 终稿 `docs/research-report-ua-tam-optimization.md`（537 行，26 条参考文献）
  - grill-me 追问 → 用户确认三项决策（采纳 I4 / 认可 parking-lot / 认可三支柱）
- Files created/modified:
  - docs/research-report-ua-tam-optimization.md（创建）
  - .workbuddy/research-materials/*（10 个过程文件）
  - .workbuddy/memory/2026-08-19.md（创建）

### 前置阶段：I4 计划初版（已被本次会话升级）
- **Status:** superseded（升级为生命周期计划）
- Actions taken:
  - 按 planning-with-files 创建 task_plan.md（I4 迭代计划）+ findings.md + progress.md
  - 盘点 scripts/ 12 .py、specs 目录结构
- Note: 原 I4-only 计划已并入本生命周期计划的 L2 阶段，细节完整保留。

## Session: 2026-08-19（Advancer · I4-0 基线核对收尾）

### 本次会话：I4-0 收尾 — 通读规格 / 盘点脚本 / R-19~R-25 草案入附录 A
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `chore: 初始化自动化计划三件套 [automation-init]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **I4-0 勾选项完成：**
  - [x] 通读 SKILL.md（113 行）+ docs/rpd-v2-technical-spec.md（682 行，重点 §3 code-map schema / §6 红线机检 / §7 预算守卫 / 附录 A）
  - [x] 盘点 12 个 scripts 职责边界（intent-router / code-map-generator / state-guard / rpd-decisions / gap-analyzer 等，见 findings.md §B 台账核对一致）
  - [x] 起草 R-19~R-25 需求编号占位 → 写入 `docs/rpd-v2-technical-spec.md` 附录 A（标注"草案，验收后转正"）+ R-24 归 parking-lot 不排期
  - [x] Q1 确认：R-22 零外部依赖先行（BM25+RRF，向量打标 TODO）— 已在 Key Decisions，直接执行
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** docs/rpd-v2-technical-spec.md（附录 A + R-19~R-25 + 占位说明）· .gitignore（配置阶段遗留：忽略 .workbuddy/* + promo/，保留 automation-rules.md）· progress.md（本日志）
- **遗留：** todo 同步依赖 wb-issues MCP 工具，本会话工具列表不可用则记录不猜（见 Error Log）；Verifier 验证后由 Verifier 标记 task_plan.md Phase I4-0 为 complete

## Test Results

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Eval 全量基线（run-eval.py） | `python scripts/run-eval.py` | 19 场景全过 | **19/19 PASS**（A~X，exit 0） | ✅ 2026-08-19 |
| Git 分支/状态基线 | `git status` + `git branch` | main 受保护、工作区干净 | main；6 未跟踪文件（计划三件套+研究+promo+.workbuddy）；无跟踪文件改动 | ✅ 2026-08-19 |
| README vs TRAINING eval 场景数口径 | 19 / 18 | 以 run-eval.py 实际为准 | 实际 19/19；TRAINING.md 18 为旧口径，待文档修订 | ✅ 已澄清 |
| I4-0 Verifier 验证（a9af0b7） | 7 项 0-trust 检查 | 19/19 PASS + 仅文档改动 + 守卫在位 | eval 19/19（exit 0）· diff 仅 .gitignore/spec/progress.md 3 文件 · 预算守卫 3000/300 在位 · 三级信任+stale 在位 · SCHEMA_VERSION 2.0.0+降级在位 · 无视觉改动 | ✅ 2026-08-19 判定A |
| I4-1 Verifier 验证（aa0bb2c） | 7 项 0-trust 检查 | 19/19 PASS + 仅涉及文件改动 + I4-1 验收达成 | eval 19/19（exit 0）· diff 仅 spec/progress/retriever.py/run-eval.py 4 文件 · 预算守卫 3000/300 在位 · 三级信任+stale 在位 · SCHEMA_VERSION 2.0.0+降级在位 · 无 UI 改动 · 验收实测：中文"支付重试逻辑"→#1 PaymentRetry(bm25) / 精确"PaymentRetry"→#1 exact / 预算 57t≤300t / 向量 TODO 在位 | ✅ 2026-08-19 判定A |
| I4-2 Verifier 验证（68e0f4e） | 7 项 0-trust 检查 + I4-2 验收（查询能力补齐） | 19/19 PASS + 三类查询可达 + 白名单/降级不崩 | eval 19/19（exit 0，含 Scenario U 3f/3g）· diff 仅 spec(+2)/progress/retriever.py(+151)/run-eval.py(+46) 4 文件，task_plan 未动 · 预算守卫 3000/300/300+EDGE_MAX=24 在位 · 三级信任+stale 在位 · SCHEMA 2.1.0+白名单(2.0.0,2.1.0)+降级在位 · 验收实测（真实项目+KG）：who-calls helper→Game(calls 0.8) / deps-of Game→main(contains 1.0)+helper(calls 0.8) / layer-of Game→Core / 未解析→resolved:false 空结果 | ✅ 2026-08-19 判定A |
| I4-3 Verifier 验证（61908d4+eb9f56c） | 7 项 0-trust 检查 + I4-3 验收（R-25 依赖锁定） | 19/19 PASS + 快照/漂移/降级均实测 + 红线机检不回归 | eval 19/19（exit 0，含 Scenario U 3h）· diff 仅 code-map-generator(+84)/rpd-cold-start(+34)/run-eval(+75)/spec(1 行)/progress 5 文件，task_plan 未动 · 预算守卫 3000/300 在位 · 三级信任+stale 在位（dependency_drift 为增量第 3 支柱，非回归）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · R-25 专项实测（真实 C++ 项目+package.json）：快照 detected=True+fingerprint / 无漂移 ok / 改版本→fingerprint_mismatch+freshness 含"依赖漂移"告警 / 删清单→missing / 旧 meta 无 dependencies→checked=False 降级不崩 | ✅ 2026-08-19 判定A |
| I4-4 Verifier 验证（4076938） | 7 项 0-trust 检查 + I4-4 验收（R-20 PRD↔代码影响） | 19/19 PASS + 双向映射/1-hop/blast/降级均实测 + 预算守卫/兼容不回归 | eval 19/19（exit 0，含 Scenario U 3i）· diff 仅 impact-analyzer.py(新增429)/run-eval(+77)/spec(+9)/progress(+18) 4 文件，task_plan 未动 · 预算守卫 3000/300 未回归 + impact RESULT_MAX_TOKENS=300 · 三级信任+stale 在位（:126-170）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · R-20 专项实测（真实 C++ 项目+真实 PRD+KG）：PRD→code changed=Game(layer Core)+1-hop=helper/main(edges 涌出)+blast Medium / code→PRD Game 反查命中 feature+page / 未解析 resolved:false 不猜 / 无 code-map 降级直扫 game.cpp/game.h / 缺 PRD ok:false 不崩 / 载荷 182t·77t·153t ≤300t | ✅ 2026-08-19 判定A |
| I4-5 Verifier 验证（56076ca+d8e713a） | 7 项 0-trust 检查 + I4-5 验收（R-23 渐进式暴露） | 19/19 PASS + 三层注入/追问闸门/双预算/降级均实测 + I0~I3 不回归 | eval 19/19（exit 0，含 Scenario U 3j 断言行）· diff 仅 exposure-guard.py(新增307)/rpd-cold-start(+48)/run-eval(+54)/spec(+8)/progress(+20) 5 文件，task_plan 未动 · 预算守卫 3000/300 未回归 + 新增 L3 500t(Q4) + 双预算 24条/2000t · 三级信任+stale 在位（:169-213 未回归）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · R-23 专项实测（真实 C++ 项目）：L1 241t≤3000t / L2 Game 30t≤300t resolved / L3 deep=0 拦截(deep_followup_required) / L3 deep=2 放行 39t≤500t / 双预算 entries=2≤24 tokens=69≤2000 ok / 未解析 NoSuchSymbolXYZ 降级不猜 / cold-start exposure_layers checked:true（无 code-map 走 no_router 降级不崩） | ✅ 2026-08-20 判定A |
| I4-6 Verifier 验证（94220bf） | 7 项 0-trust 检查 + I4-6 验收（R-21 L0-L3 分层记忆） | 19/19 PASS + 四层读写/过期/回退/膨胀守卫/降级均实测 + 预算守卫/兼容不回归 | eval 19/19（exit 0，含 Scenario U 3k 断言行）· diff 仅 memory-layers.py(新增508)/rpd-cold-start(+44)/run-eval(+104)/spec(+43)/progress(+19) 5 文件，task_plan 未动 · 预算守卫 3000/300/500/24/2000 未回归 · 三级信任+stale 在位（rpd-cold-start.py:211-255 未回归）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · R-21 专项实测（真实 .rpd 库）：空库降级 ok / import-decisions 只导入 accepted(D-1 imported=1) / --fact 零依赖→d1 命中 + miss→resolved:false+fallback_evidence / fast-path 只供 L2+L3(profile p1, scope=prd 场景 s1 仅在 --list L2) / 过期 m9 标记→drop-clean 删除 / decisions.md 指纹变更→content_matches False / --stats counts+warnings 在位 / cold-start step01 memory checked:true counts+fallback | ✅ 2026-08-20 判定A |
| I4-7 Verifier 验证（11ee591+ad76b15） | 7 项 0-trust 检查 + I4-7 验收（parking-lot 四档触发） | 19/19 PASS + 四触发机检/升级三要素/承诺守卫/降级均实测 + 预算守卫/兼容不回归 | eval 19/19（exit 0，含 Scenario U 3l 8 组断言行）· diff 仅 parking-lot.py(新增327)/run-eval(+77)/spec(+39)/progress(+19) 4 文件，task_plan 未动 · 预算守卫 3000/300 未回归 + LIST_LIMIT=50 · 三级信任+stale 在位（rpd-cold-start.py:211-255 未回归）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · I4-7 专项实测（真实 .rpd 库）：空库 builtin 5 条目 / audit 四触发逐条机检（threshold=3、R-28 dep_ready=False 因缺 R-26、landed=R-19~R-23,R-25） / promise-check 零违规 / 缺 budget exit 1 / 幽灵 R-95 无触发 exit 2 / R-96 信号≥3 升级成功+落盘 store / 损坏 store 降级 builtin 不崩 | ✅ 2026-08-20 判定A |
| I4-8 Verifier 验证（79ad7b6） | 7 项 0-trust 检查 + I4-8 验收（Q5 出口 Gate 机检） | 19/19 PASS + M1 A/B 连续性/M2 PRD 闭环/M3 观测/回归守卫/诚实失败均实测 + 预算守卫/兼容不回归 | eval 19/19（exit 0，含 Scenario U 3m 两断言）· diff 仅 i4-gate.py(新增344)/run-eval(+37)/spec(+28)/progress(+17) 4 文件，task_plan 未动 · 预算守卫 3000/300 未回归（code-map-generator.py:46/49）+ gate 内 M1 93t/M2 176t ≤300t 实测 · 三级信任+stale+dependency_drift 在位（rpd-cold-start.py:141/213）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · I4-8 专项实测（真实 C++ 项目+KG+PRD）：带 map+PRD → exit 0 PASS（M1 arm A map_resolved=True entry 93t≤300t / M2 changed=[Game] affected=[helper,main] blast Medium 176t≤300t / M3 observation 注记不阻断 / 回归 3/3 ok）；移走 code-map → exit 2 如实 FAIL（M1 arm B source_scan degrade (explicit, no guess) / M2 ok:false）—— Gate 不因降级路径放行丢失闭环 | ✅ 2026-08-20 判定A |
| I4-9 Verifier 验证（4c40084） | 7 项 0-trust 检查 + I4-9 验收（文档与交付） | 19/19 PASS + 仅文档改动 + SKILL ≤8KB + 状态文件可校验 | eval 19/19（exit 0，A~X 全过）· diff 仅 .project-state.md(新增67)/SKILL.md(26)/spec(+14)/usage(+70)/progress(+17) 5 文件，task_plan 未动 · 预算守卫 3000/300 在位 · 三级信任+stale 在位（rpd-cold-start.py:211-255）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · I4-9 验收实测：SKILL.md git blob 8116 B ≤ 8192 B（R-05 不破，119 行 LF↔CRLF 差异恰 119 B）· .project-state.md state-validator Validation PASSED exit 0 · spec §16.1 R-19~R-29 验收行 + §17.1 顺序链在位 · usage §11 速查 6 脚本 CLI 在位 · SKILL 工具箱 12→18 行与 6 新脚本对齐 | ✅ 2026-08-21 判定A |
| I4-closeout Verifier 验证（27f7fd5） | 7 项 0-trust 检查 + I4 收官报告（交付清单/验证证据/L3 建议） | 19/19 PASS + 仅 progress.md 改动 + 报告与真实 commit 历史一致 | eval 19/19（exit 0，A~X 全过）· diff 仅 progress.md（+44/-4：5-Question Reboot 更新 + 收官报告），task_plan.md diff 0 行 · 预算守卫 3000/300 在位（code-map-generator.py:46/49）· 三级信任+stale+dependency_drift 在位（rpd-cold-start.py）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位 · 计划一致性：收官报告交付清单 10 模块 commit/判定与前 10 轮 Verifier 记录逐一吻合 · 无视觉改动 · 判定A（无 pending phase 可标 complete，I4 全模块已收官） | ✅ 2026-08-21 判定A |
| I4-closeout 治理提案 Verifier 验证（562c14b） | 7 项 0-trust 检查 + 治理提案文档（A/B/C 三选项 + D1/D2 决策点） | 19/19 PASS + 仅新增 1 文档 + 文档自我声称可复验 + 未擅改自动化配置 | eval 19/19（exit 0，A~X 全过，`All scenarios passed!`）· commit 真实 diff = 仅 docs/automation-governance-proposal.md（+102/-0，1 file changed），progress.md 在此 commit 零改动（文档 §六「1 file changed, 102 insertions」自我声称核实属实）· task_plan.md diff 0 行（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49 + exposure-guard.py:45/46）· 三级信任+stale 在位（rpd-cold-start.py:213-255）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）· **0-trust 延伸核查**：文档中给用户的 automation ID `automation-1787109094822` 经 automation_update(list) 核实真实存在（name「I4-推进（Advancer）：按计划实现下一模块」、ACTIVE、FREQ=HOURLY;INTERVAL=1 全周），D1 指令可执行非幻觉 · 文档明示「待张敬拍板、不擅自改配置」，未实际改自动化状态、未 push、未触碰 main · SKILL.md git blob 8116 B ≤ 8192 B（R-05 未漂）· 判定A（无 pending phase 可标 complete，I4 全模块已收官） | ✅ 2026-08-29 判定A |
| I4-closeout 交接文档 Verifier 验证（3bb5666） | 7 项 0-trust 检查 + 交接文档入仓（§八 状态校正） | 19/19 PASS + 仅 docs/progress 改动 + 文档事实性可复验 + task_plan 零改动 | eval 19/19（exit 0，A~X 全过，`🎉 All scenarios passed!`，本轮真实复跑）· commit 真实 diff = 2 files changed / 398 insertions：docs/handoff-automation-2026-08-19.md（新增 +232）+ progress.md（+166，tick #51~#65 空转日志固化），**task_plan.md diff 0 行**（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49 + exposure-guard.py:45/46）· 三级信任+stale 在位（rpd-cold-start.py:213-255 verified/stale/unverified + fingerprint_mismatch）· SCHEMA 2.1.0+白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）· 纯 Markdown 文档无视觉/UI 改动 · **0-trust 文档事实性核查**：①文档 §八 给用户的 Advancer ID `automation-1787109094822` 经 automation_update(list) 复验真实存在（「I4-推进（Advancer）：按计划实现下一模块」ACTIVE / FREQ=HOURLY;INTERVAL=1 全周）②valid_until 文档称「2026-08-31 23:59 Asia/Shanghai」，自动化元数据实际 `2026-08-31T15:59:59.999Z` = +08:00 23:59:59.999，吻合 ③旧 ID 5867270/5867281 在 list 中确已不存在 ④文档「自 2026-08-19 起一直未跟踪」经 `git cat-file -e HEAD~1:<path>` 复核属实（NOT_IN_HEAD~1）⑤「I4-0~I4-9 全部 complete」与 task_plan.md 10 个 Phase Status 逐一吻合 · 判定A（无 pending phase 可标 complete，task_plan.md 未动） |
| I4-closeout 交接文档精度修正 Verifier 验证（52cd265） | 7 项 0-trust 检查 + 上轮留档两项精度问题是否真实修复 | 19/19 PASS + 仅 docs/progress 改动 + 机检证据可复现 + task_plan 零改动 | eval 19/19（exit 0，A~X 全过，`🎉 All scenarios passed!`，本轮真实复跑）· commit diff = **2 files changed / 39 insertions / 3 deletions**：docs/handoff-automation-2026-08-19.md（+32/-3）+ progress.md（+10），**task_plan.md diff 0 行**（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49 + exposure-guard.py:45/46）· 三级信任 + stale 在位（rpd-cold-start.py:213-255 verified/stale/unverified + fingerprint_mismatch + :246 missing）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）· 纯 Markdown 文档无视觉/UI 改动 · **0-trust 文档事实性复验（文档内嵌 bash 命令逐条实跑，不采信 Advancer 转述）**：①`scripts/parking-lot.py --audit` 实跑 exit 0，count=5 五条目 status 全 frozen，deps/signals 与文档逐字吻合（R-24[R-21] / R-26[R-21] / R-27[R-19] / R-28[R-21,R-26] / R-29[R-22]，signals 全 0）②`LANDED_FALLBACK` 实查 = `{"R-19","R-20","R-21","R-22","R-23","R-25"}`（parking-lot.py:67）与文档一致③spec §16.1:708-711 R-26~R-29 行原文确有「（P2 parking-lot）冻结登记」标注④`scripts/i4-gate.py` 存在（13705 B，Q5 出口 Gate）⑤升级子命令确为 `--upgrade`（非 --promote），缺 --impact/--budget 返回 exit 1（parking-lot.py:237），与文档一致⑥Verifier ID `automation-1787109023265` 经 automation_update(list) 复验：name「I4-验证（Verifier）：0-trust 独立检验」/ ACTIVE / `FREQ=HOURLY;INTERVAL=1`，与文档一致⑦`--promise-check` 实跑 exit 0 零违规 · **上轮留档两项精度问题均确认修复**（①§八 补上当前有效 Verifier ID ②「Q1~Q5 全部落地（R-19~R-29）」更正为已落地 R-19~R-23 + R-25，R-24/R-26~R-29 归位 parking-lot 冻结项）· 判定A（无 pending phase 可标 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 治理提案 §七 到期处置预案 Verifier 验证（f7e0262） | 7 项 0-trust 检查 + §七 到期（valid_until）处置预案（到期事实 / 默认路径对比 / H1~H4 人工清单） | 19/19 PASS + 仅 docs/progress 改动 + 文档全部事实性声称逐条实跑复验 + task_plan 零改动 | eval 19/19（exit 0，A~X 全过，`🎉 All scenarios passed!`，本轮真实复跑）· commit diff = **2 files changed / 79 insertions / 0 deletions**：docs/automation-governance-proposal.md（+59）+ progress.md（+20），**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层预算 3000/300/500 与 DEEP_FOLLOWUP_TURNS=2 在位（exposure-guard.py:45-47/50）· 三级信任 + stale 在位（rpd-cold-start.py:213-255 verified/stale/unverified + :246 missing + :255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62），且被 i4-gate.py:101-105 回归守卫消费 · 纯 Markdown 文档无视觉/UI 改动 · **0-trust 文档事实性逐条复验（不采信 Advancer 一手声称，全部独立重跑）**：①**核心声称「两自动化 validUntil 同一时刻」经 `automation_update(mode="view")` 双查证实为真** —— Advancer `automation-1787109094822` 与 Verifier `automation-1787109023265` validUntil **同为 `2026-08-31T15:59:59.999Z`**，validFrom 同为 `2026-08-18T16:00:00.000Z`、rrule 同为 `FREQ=HOURLY;INTERVAL=1;BYDAY=MO..SU`、status 均 ACTIVE，name 与文档表逐字吻合 ②折算本地 2026-08-31 23:59:59.999（UTC+8）换算正确 ③「剩余窗口约 40 小时 46 分钟」自 07:13:28 起算复核无误 ④H1「均 ACTIVE」属实 ⑤H3「`git ls-remote --heads origin` 仅 refs/heads/main」实跑属实 → 分支纯本地、远端无副本结论成立 ⑥H4「`git status --porcelain` 输出为空」本轮起始复核属实 ⑦文档指定的追溯方法 `git log --oneline -- docs/automation-governance-proposal.md` 实跑可用（返回 f7e0262 / 562c14b 两条）⑧§七 内 `grep -c "tick #"` = **0**，与「不引用自动化内部 tick 计数」的口径声明自洽 · **本轮新观察（非 FAIL，仅留档）**：H2「progress.md 692 行」与 H3「0 behind / 38 ahead」均系**该 commit 入仓前**测得的一手值（692+20=712 行、38+1=39 ahead，两条差值均可被本次 commit 自身完全解释），但文档冠以「当前一手值」——读者按文档现跑会得到 712 / 39。**成因是"文档与自身 commit 同批入仓"的自引用漂移**，数值本身真实无造假，Verifier 禁改 docs/，留档供用户判断 · 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 交接文档去 tick 化 Verifier 验证（2025a08） | 7 项 0-trust 检查 + 文档去 tick 计数化（改 commit hash 口径） | 19/19 PASS + 仅 docs/progress 改动 + 引用 hash 真实存在 + 机检证据未失真 + task_plan 零改动 | eval 19/19（exit 0，A~X 全过，`🎉 All scenarios passed!`，本轮真实复跑 `python scripts/run-eval.py` EXIT=0）· commit diff = **2 files changed / 18 insertions / 3 deletions**：docs/handoff-automation-2026-08-19.md（+5/-3）+ progress.md（+13），**task_plan.md diff 0 行**（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49 + exposure-guard.py:45/46）· 三级信任 + stale 在位（rpd-cold-start.py:213-255 verified/stale/unverified + fingerprint_mismatch + :246 missing）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50）· 纯 Markdown 文档无视觉/UI 改动 · **0-trust 引用真实性复验（文档给出的每个 hash 逐条 `git show` 实跑）**：①`3bb5666` = 2026-08-29 21:17:31 `docs(I4-closeout): 交接文档入仓…[advancer]` → §八标题改称「Advancer 轮，commit 3bb5666」属实 ②`52cd265` = 2026-08-29 23:17:59，其父 `b7f91bf` = 22:16:51 `[verifier]` → Advancer 关于「该轮属 Advancer」的推断成立 ③`grep -n "tick #\|#6[0-9]\|#7[0-9]"` 全文**零命中**，仅剩 151/179/186 行三处通用「下个 tick」描述（非计数编号，不构成不可验证引用）+ 210 行新增口径约定本身 → 去 tick 化**彻底** · **改标题未致失真复验**：`python scripts/parking-lot.py . --audit` 实跑 exit 0 → `landed=[R-19..R-23,R-25]`、`threshold_user_signal=3`、五条目 status 全 frozen（R-24/R-26 `deps landed: R-21` any_ready=true；R-27 `deps landed: R-19`；R-28 `missing deps: R-26` → **any_ready=false**；R-29 `deps landed: R-22`），`LANDED_FALLBACK` = parking-lot.py:67，与文档「机检证据」小节逐字一致 · Verifier 自动化 `automation-1787109023265` 经 automation_update(list) 复验仍 ACTIVE / FREQ=HOURLY;INTERVAL=1 → 文档 §八 Verifier ID 行仍准确 · **本轮新观察（非 FAIL，仅留档）**：Advancer 日志自称「tick #73」，与本自动化 memory 序列无外部可核对基准——tick 编号不可外部验证正是本 commit 要消除的问题，口径统一后该差异不再有意义 · 判定A（无 pending phase 可标 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 治理提案数字口径整改 Verifier 验证（0604e81） | 7 项 0-trust 检查 + §三 量级描述重写（初稿数字实测不可复现 → 可复现口径）+ §7.3 硬编码数字改「实测时刻+复现命令」 | 19/19 PASS + 仅 docs/progress 改动 + 整改后每个数字均可独立复算 + task_plan 零改动 | eval 19/19（exit 0，`🎉 All scenarios passed!`，本轮真实复跑）· commit diff = **2 files changed / 50 insertions / 12 deletions**：docs/automation-governance-proposal.md（+34/-12）+ progress.md（+16，仅 Advancer 日志），**task_plan.md diff 0 行**（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层 3000/300/500 与双预算 24 条/2000t（exposure-guard.py:45-49）· 三级信任 verified/stale/unverified 在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）且被 i4-gate.py:101-105 回归守卫消费 · 纯 Markdown 无视觉/UI 改动 · **0-trust 数字独立复算（不采信 Advancer 一手声称，文档内每条复现命令全部重跑）**：①`git show 5aebe97:progress.md \| wc -l` = **417** ✅（5aebe97 经 `git log -1` 核实为 I4 收官报告 verify commit，hash 真实存在）②`sed -n '442,603p' progress.md \| wc -l` = **162** ✅ ③`sed -n '442,563p;576,592p' progress.md \| wc -l` = **139** ✅（122+9+8=139，与 #51~#61=122 / #63=9 / #64=8 分段对账吻合）④`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 41 ahead**（文档记 40，+1 = 本 commit 自身 → 自引用漂移说明成立）⑤`git ls-remote --heads origin` 实跑仅 `refs/heads/main` ✅ ⑥**关键断言「progress.md 里只有 11 条空转日志」经 `grep -nE '^## .*#'` 逐条核实：#51~#61 恰 11 段（行 442–563），而「46 条」实为 `.workbuddy/automations/<id>/memory.md` 的 tick 计数（该序列现编至 #77）→ 「混淆两个计数源」的根因判定属实** ⑦算术自洽复核：417+122=539 ✅、122/539=22.6%≈「~23%」✅、162/738=21.95%≈「22%」✅、139/738=18.83%≈「18.8%」✅、#62(12行)+#65(11行)=23 ✅、738−139+6≈605 ✅ · 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 治理提案 §零 口径公约 Verifier 验证（d5a0628） | 7 项 0-trust 检查 + §零 口径公约（R-1 快照 / R-2 commit hash / R-3 修订触发，一次性终结「数字同批漂移」与「tick 计数不可核对」两类缺陷） | 19/19 PASS + 仅 docs/progress 改动 + 文档每条复现命令独立重跑 + task_plan 零改动 | eval 19/19（exit 0，`🎉 All scenarios passed!`，本轮真实复跑 EXIT=0）；另 `python scripts/i4-gate.py . --json` **exit 0 / `"pass": true`**，regression_guard 三项全 ok（`budget:router_entry` / `redline:trust` / `compat:schema`）· commit diff = **2 files changed / 48 insertions / 9 deletions**：docs/automation-governance-proposal.md（+34/-9）+ progress.md（+14/-0，仅 Advancer 日志），**task_plan.md diff 0 行**（Goal/Key Decisions/Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层 3000/300/500 与双预算 TASK_ENTRY_BUDGET=24 / TASK_TOKEN_BUDGET=2000（exposure-guard.py:46-49）· 三级信任 verified/stale/unverified 在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）且被 i4-gate.py:101-105 回归守卫消费 · 纯 Markdown 无视觉/UI 改动 · **0-trust 数字独立复算（不采信 Advancer 一手声称，文档内每条复现命令全部重跑）**：①`wc -l progress.md` = **799**（文档记 785，+14 = 本 commit 自身 Advancer 日志 → §零 R-1「当前值=写入时刻快照」声明成立，非造假）②`sed -n '442,603p' progress.md \| wc -l` = **162** ✅ 与 09:16 测量**完全一致** ③`sed -n '442,563p;576,592p' progress.md \| wc -l` = **139** ✅ 同样一致 → **「空转段在中段、新日志追加到尾部，故待压缩量稳定、只有总行数漂移」的核心断言被独立证实**（这是 D2 收益判断不随漂移变化的前提）④`git log --oneline 27f7fd5..HEAD \| wc -l` = **14**（文档记 13，+1 = 本 commit 自身，同属 R-1 自引用漂移）⑤**核心断言 `git log --oneline 27f7fd5..HEAD -- scripts/ \| wc -l` = 0 成立** → 「自收官以来 scripts/ 零改动」这个可核对事实在 14 commits 下依然为真 ⑥`git diff --name-only 27f7fd5..HEAD \| sort -u` = 3 个文件（governance-proposal / handoff / progress），与文档逐字吻合 ⑦`git log -1 --format=%ad --date=iso 562c14b` = 2026-08-29 16:15:37 ✅（文档「固化 16:1x」）⑧同命令 27f7fd5 = 2026-08-21 14:13:45 ✅ ⑨`git rev-list --left-right --count origin/main...HEAD` = 0 behind / **43** ahead（文档记 42，+1 自身）· **§零 公约验收**：R-1/R-2/R-3 三规则 + 历史遗留 tick 标注读法均落盘；「不因数值变旧而更新」从规则层面关闭了逐 tick 追更这条成本通道 · 算术复核：162/785=20.6%≈「~21%」✅、139/785=17.7%✅、785−139+6=**652** ✅ · 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 治理提案 §八 H3 合并前风险审计 Verifier 验证（51b2e81） | 7 项 0-trust 检查 + §八 合并面量化（44 commits → 4 文件/14 处删改）+ 8.3 D2 先于 H3 的顺序论证 | 19/19 PASS + 仅 docs/progress 改动 + §八 每条复现命令独立重跑 + task_plan 零改动 | eval 19/19（exit 0，`🎉 All scenarios passed!`，本轮真实复跑 **REAL_EXIT=0**，PASS 计数 19）；另 `python scripts/i4-gate.py . --json` **exit 0 / `"pass": true`**，regression_guard 三项全 ok（`budget:router_entry` / `redline:trust` / `compat:schema`）· commit diff = **2 files changed / 81 insertions / 0 deletions**：docs/automation-governance-proposal.md（+62）+ progress.md（+19，仅 Advancer 日志），**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层 3000/300/500 与双预算 TASK_ENTRY_BUDGET=24 / TASK_TOKEN_BUDGET=2000（exposure-guard.py:45-49）+ i4-gate.py:38/39 ROUTER_LIMIT/ENTRY_LIMIT · 三级信任 verified/stale/unverified 在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）且被 i4-gate.py:101-105 回归守卫消费 · 纯 Markdown 无视觉/UI 改动 · **0-trust §八 全部复现命令独立重跑（不采信 Advancer 一手声称）**：①`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 45 ahead**（文档记 44，+1 = 本 commit 自身，§零 R-1 自引用漂移成立）②`git log --oneline origin/main..HEAD \| wc -l` = **45**（同上）③`git diff --name-only origin/main...HEAD \| sort -u \| wc -l` = **21** ✅ 与文档逐字一致 ④`git ls-remote --heads origin` 实跑仅 `refs/heads/main` ✅ ⑤`git status --porcelain \| wc -l` = **0** ✅ ⑥**8.2 核心断言 `git diff --numstat origin/main...HEAD \| awk '$2>0'` 恰输出 4 行**（SKILL.md 16/10 · rpd-v2-technical-spec.md 159/2 · code-map-generator.py 227/1 · rpd-cold-start.py 125/1），删除列合计 **10+2+1+1 = 14** ✅ 与「4 文件 / 14 处删改」完全吻合 ⑦`git show origin/main:progress.md` = `fatal: path 'progress.md' exists on disk, but not in 'origin/main'` ✅ → **8.1 结论一（17 个纯新增文件不可能冲突）与 8.3（progress.md 随本次合并首次进入 main）两个论证的前提均属实** ⑧`grep -n SCHEMA_WHITELIST scripts/code-map-generator.py` = `:62 SCHEMA_WHITELIST = ("2.0.0", "2.1.0")` ✅ → 8.2 首行「非功能丢失，是 R-10 升级」判定成立 ⑨`grep -n "Step 4" scripts/rpd-cold-start.py` = `:421 # --- Step 4: on-demand load (router) + R-23 exposure report ---` ✅ → 「Step 4 仍在」判定成立 ⑩`sed -n '94,110p' SKILL.md` = 新工具箱表 15 行（旧 10 脚本逐个有对应条目 + 新增 retriever/impact-analyzer/exposure-guard）✅ → 「整表重写非内容丢失」判定成立 ⑪`git ls-files scripts/ \| grep -c "\.pyc$"` = **0** ✅ ⑫`git ls-files .workbuddy/` = 仅 `.workbuddy/automation-rules.md` ✅ → 8.2 结论三「有意为之非污染」成立（唯一偏差见留档观察①）⑬`sed -n '442,563p' \| wc -l` = **122**、`sed -n '576,592p'` 拼合 = **139**、`sed -n '442,603p' \| wc -l` = **162** ✅ → **与 09:16、12:13 测量第四次一致，「待压缩量 139 是稳定量」在 45 commits 下仍成立** ⑭`wc -l progress.md` = **839**（文档记 820，+19 = 本 commit 自身 Advancer 日志，R-1 覆盖）⑮`automation_update(mode="list")` 复验 §8.4 两个 ID 真实存在且 ACTIVE：Advancer `automation-1787109094822`「I4-推进（Advancer）：按计划实现下一模块」+ Verifier `automation-1787109023265`「I4-验证（Verifier）：0-trust 独立检验」，rrule 均 `FREQ=HOURLY;INTERVAL=1;BYDAY=MO..SU` → H1 指令可执行非幻觉 · 算术复核：122+17=**139** ✅、820−139=**681** ✅（文档明示「请自跑 wc -l 代入当前值」，自洽）· 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout 交付完整性审计 Verifier 验证（3163c73） | 7 项 0-trust 检查 + 27 个未勾 checkbox 三重对账（22 已实现 / 1 临界 / 4 流程，无一项未实现）+ F1 R-05 临界判定 | 19/19 PASS + 仅新增 1 个 Markdown 文档 + 审计全部数字与 60 处 file:line 证据独立复算 + task_plan 零改动 | eval 19/19（exit 0，`🎉 All scenarios passed!`，本轮真实复跑 REAL_EXIT=0）· `python scripts/i4-gate.py . --json` **exit 0 / `"pass": true`**，regression_guard 三项全 ok（`budget:router_entry` / `redline:trust` / `compat:schema`）· commit diff = **2 files changed / 184 insertions / 0 deletions**：`docs/i4-delivery-completeness-audit.md`（新建 +165）+ progress.md（+19，仅 Advancer 日志），**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层 3000/300/500 与双预算 24/2000（exposure-guard.py:45-49）+ i4-gate.py:38/39 · 三级信任 verified/stale/unverified + dependency_drift 在位（rpd-cold-start.py:213-255，:255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）且被 i4-gate.py:101-105 消费 · 纯 Markdown 无视觉/UI 改动 · **0-trust 独立复算（不采信 Advancer 一手值）**：分 Phase 未勾数 I4-0(4)/I4-1(3)/I4-2(2)/I4-3(0)/I4-4(4)/I4-5(0)/I4-6(3)/I4-7(3)/I4-8(4)/I4-9(4) = **27** 与文档逐字吻合、22+1+4=27 自洽；基线 commit `HEAD~1` = `709a6fe` 属实；`git show HEAD:SKILL.md \| wc -c` = **8116**、工作区 **8235**、差 **119** 经 **python 字节级复核**确认（CR=119 / LF=119，blob 内 CR=0 → autocrlf 结论成立）、`core.autocrlf=true`、无 `.gitattributes` 均属实 → **F1「R-05 未违反但余量仅 76 B」判定成立**；`grep -c "SKILL" scripts/i4-gate.py` = **0**（无体积守卫）属实；`ls scripts/*.py \| wc -l` = **18**（F2 属实）；`git log -1 --format=%ad --date=iso 4c40084` = 2026-08-21 12:24:36 ✅、27f7fd5 = 14:13:45 ✅、handoff 260 行 ✅、`.project-state.md` 4659 B ✅、`grep -c "\.py" SKILL.md` = 30 ✅ · **逐条 file:line 证据抽检 60 处**：retriever.py:10/42/90/112/141/185/201/374/444、code-map-generator.py:54/59/461/738/765/778/825、impact-analyzer.py:192/195/197/199/200/265/308/313、memory-layers.py:61/62/64/65、parking-lot.py:10/31/32/70、spec :294/306/314/572/623/677/701/711/713/735/797/801/810/818、eval :736/744/1008/1174/1193/1252/1293/1304、SKILL.md :94-110 工具箱表 —— **内容全部命中，仅 3 处行号偏差（见会话日志）** · 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-30 判定A |
| I4-closeout §8.4 压缩命令风险修正 Verifier 验证（bb58644） | 7 项 0-trust 检查 + §零 R-4「行号区间 = 锚点求值」新公约 + §8.4 `sed -i` 破坏性命令改 7 步锚点流程 + §三 3.2 C-1/C-2 两处实质缺陷更正 | 19/19 PASS + 仅 docs/progress 改动 + 全部一手数字与锚点独立复算 + task_plan 零改动 | eval 19/19（exit 0，`🎉 All scenarios passed!`，本轮真实复跑 **REAL_EXIT=0**，重定向取真实退出码）；另 `python scripts/i4-gate.py . --json` **exit 0 / `"pass": true`**，regression_guard 三项全 ok（`budget:router_entry` / `redline:trust` / `compat:schema`）· commit diff = **2 files changed / 86 insertions / 19 deletions**（`git diff HEAD~1 --numstat` = docs 68/19、progress 18/0）：docs/automation-governance-proposal.md（+68/-19）+ progress.md（+18，仅 Advancer 日志），**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）· 预算守卫 3000/300 在位（code-map-generator.py:46/49）+ 三层 3000/300/500 与 DEEP_FOLLOWUP_TURNS=2（exposure-guard.py:45-47/50）+ i4-gate.py:38/39 · 三级信任 verified/stale/unverified 在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）· SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）且被 i4-gate.py:101-105 消费 · 纯 Markdown 无视觉/UI 改动 · **0-trust 独立复算（不采信 Advancer 一手值，全部重跑）**：①`git show HEAD:progress.md \| wc -l` = **921**，文档记 903（+18 = 本 commit 自身 Advancer 日志，§零 R-1 自引用漂移成立）②三锚点 `^## .*tick #51 / #62 / #67 ` 的 `grep -c` **均 = 1** ✅ 与文档逐字吻合 ③锚点行号实测：#51=**446** / #62=**568** / #67=**608** → 可压缩区间 446-567 = **122 行** ✅、全段 446-607 = **162 行** ✅ 与文档「122 / 162」逐字一致 ④**分段逐块复算（python 遍历标题行）**：#51=11 / #52=11 / #53=11 / #54=11 / #55=11 / #56=11 / #57=11 / #58=11 / #59=12 / #60=11 / #61=11 → 合计 **122** ✅；#62=**12** / #63=**9** / #64=**8** / #65=**11** → 不可压缩 **40** ✅；122+40=**162** 自洽 ✅ ⑤区间边界：446 行 = `## 2026-08-23 05:1x（tick #51 · I4 Advancer）`、567 行 = 空行（`cat -A` = `$`）、568 行 = #62 标题、607 行 = 空行、608 行 = #67 标题 → **边界干净；#66 确不存在**（文档「全段 END 锚点须用 #67 而非 #66」属实）⑥修正后 dry-run `sed -n '446,567p' progress.md \| grep -cE 'tick #6[2-5]'` = **0** ✅ → 区间内无 #62~#65 ⑦**C-1 漂移实证逐条复现**：`#51` 标题行位置 `0604e81`=**442** → `d5a0628`=**443** → `3163c73`=**445** → `HEAD`=**446**，与文档四个数值**逐字吻合** → 「Verifier 每 tick 向头部 Test Results 表插 1 行 ⇒ 中段区间被等量顶偏」的根因判定成立，硬编码行号方案结构性不安全结论成立 ⑧**C-2 分类更正成立**：#63（治理提案计数更新，9 行，含真实文档产出）/ #64（交棒链条记录点 `378b2f2`/`562c14b`，8 行）确有实质内容 → 移出压缩范围，可压缩量 139 → **122** ✅ ⑨**裸锚点不唯一实证（文档两处自纠均有实测依据）**：全文 `grep -c 'tick #62 '` = **3**（Advancer 记 2，+1 = 本 commit 日志再次提及；≥2 已足证裸锚点不可用）；区间内 `sed -n '446,567p' \| grep -c 'tick #6'` = **2**，命中行恰为 #60/#61 标题，与文档逐字吻合 → 改用 `^## .*` 限定标题行 + `#6[2-5]` 收窄范围，两处修正均正确 ⑩`.gitignore`：`wc -l` = **19**、`grep -n 'automation-rules'` = **18**，第 16-18 行实为 `.workbuddy/*` + 注释 + `!.workbuddy/automation-rules.md` → §8.2 从前稿「20-22」更正为「16-18」**属实** ⑪算术复核：903−122+6 = **787** ✅（文档「≈787」）、(903−787)/903 = **12.8%** ✅ 与文档「降幅约 12.8%」一致 ⑫计划一致性：task_plan.md I4-0~I4-9 **10 个 Phase Status 全 complete**、L3 planned → pending=0，与本轮「无 Phase 可标 complete」一致；`git rev-list --left-right --count origin/main...HEAD` = 0 behind / **49** ahead · **留档观察（非 FAIL，Verifier 禁改 docs/）**：①§三 3.2「文件总行数 903」现读 921（+18 本 commit 自身），已被 §零 R-1 覆盖，不追更 ②3.2 表内行号 446-607 标注为「20:1x 快照、请自跑锚点求值」，因 H2 已全面改为锚点方案，行号仅作示例 → **无 C-1 类破坏风险** ③H2-3 前置断言写死「行数 = 122」，若日后 #51~#61 区间内容有增删会误停手 —— 属**安全侧失败**（不删错内容），可接受 · 判定A（无 pending phase 可标 complete，I4-0~I4-9 全 complete，task_plan.md 未动） | ✅ 2026-08-31 判定A |

## Error Log

| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-08-19（Verifier tick） | 第 4 步 todo 同步阻塞：`mcp__wb-issues__todo_statuses` / `todo_add_comment` 本会话工具列表仍不可用（ToolSearch 精确名未命中，搜索只返回 github/issues 工具） | 1 | 记录不猜。面板映射：I4-0=rhb7Wp 已由 Verifier 判定 A（7 项全过），待具备 wb-issues MCP 的会话置 done + 写验证结论 |
| 2026-08-19（Advancer tick） | 第 5 步 todo 同步阻塞：`mcp__wb-issues__todo_statuses` / `todo_add_comment` 本会话工具列表不可用（ToolSearch 精确名未命中，deferred tools 无 wb-issues 前缀） | 1 | 记录不猜，留待具备 wb-issues MCP 的会话补做（I4-0 todo=rhb7Wp） |
| 2026-08-19（研究阶段） | patch 指令未被执行 | 1 | lead 直接对终稿最小化 Edit |
| 2026-08-19（研究阶段） | Ch2 论文归属误述 | 1 | 审稿退回 → 修订 → round2 PASS |
| 2026-08-19（研究阶段） | Ch3 归因口径不一致 | 1 | 四分法统一 → round2 PASS |
| 2026-08-19（本次重构） | 原 plan 仅 I4 范围、缺资产台账 | 1 | 升级 L0–L3 全景 + findings 台账 |

## 5-Question Reboot Check

| Question | Answer |
|----------|--------|
| Where am I? | L2 — I4 外扩迭代 **已收官**（I4-0~I4-9 全部 complete，本 tick 已写 I4 收官报告），处于整体生命周期计划框架下 |
| Where am I going? | L3 未来三支柱（阶段 A 补漏 → B 资产化/隔离 → C 组织级组合），按 parking-lot 四档触发升级；当前无活跃排期 |
| What's the goal? | RPD-skill 整体生命周期管理：在红线之下按版本阶段推进能力交付 |
| What have I learned? | 见 findings.md（资产台账 + UA/TAM 研究 + R-19~R-29 + 三支柱）+ 本文件 I4 收官报告（10 模块交付清单与验证证据） |
| What have I done? | L0/L1 历史阶段 + L2 I4 外扩全模块交付（6 新脚本 + 文档 + eval 19/19）+ 收官报告落盘 |

---

*Update after completing each phase or encountering errors*

## Session: 2026-08-19（Advancer · I4-1 R-22 混合检索）

### 本次会话：实现 R-22 混合检索 retriever.py + eval U 扩展
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `docs(I4-0): 记录 Verifier todo 同步阻塞 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-1（R-22 混合检索，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/retriever.py`（296 行）：exact 通道（R-11 兼容：整名/末段/inverted index 命中）+ BM25 通道（零依赖，CJK bigram）+ RRF 融合（k=60）+ 预算守卫（结果列表 ≤300 token）+ 向量通道打标 TODO（Q1 零依赖先行）
  - `scripts/run-eval.py` Scenario U 扩展断言：精确命中 "Game" 排名第一且 channel=exact（R-11 不劣化）、预算 ≤300t、向量 TODO 注释在位、语义查询回退不崩
  - `docs/rpd-v2-technical-spec.md` 附录 A：R-22 状态转正（草案 → 已落地）
- **核心验收（真实运行）：** 中文语义查询 "支付重试逻辑" → #1 PaymentRetry（bm25）；精确查询 "PaymentRetry" → #1 PaymentRetry（exact）
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** scripts/retriever.py（新增）· scripts/run-eval.py（U 场景扩展）· docs/rpd-v2-technical-spec.md（R-22 转正）· progress.md（本日志）
- **技术注记：** 零依赖环境 tree-sitter 不可用 → 生成器降级正则，`Game::update` 限定名方法不被正则解析（既有缺陷，不属本 tick 范围，已避免在 eval 断言依赖它；I4-2 边信息或 I4-8 可评估是否修）
- **遗留：** 向量通道 TODO（需外部 embedding 依赖，按 Q1 冻结）；wb-issues MCP todo 同步仍不可用（同前轮）


## Session: 2026-08-19（Advancer · I4-2 R-19 边信息复用）

### 本次会话：实现 R-19 边信息（edges schema + KG 只读映射 + 悬挂剔除 + 降级）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-1): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-2（R-19 边信息复用，第一个非 complete）
- **做了什么：**
  - `scripts/code-map-generator.py`（+144 行）：SCHEMA_VERSION 2.0.0→2.1.0（R-10 白名单 2.0.0/2.1.0）；entry 增 `edges[]`（type/weight/target/confidence=mapped）；UA 权重表（contains 1.0 / calls 0.8 / imports 0.7 / depends_on 0.6…）；`load_knowledge_graph`（四路径探测、只读、schema 不匹配→降级告警）；`attach_kg_edges`（entry id→name→末段三级映射、**悬挂边剔除并计数**、layer 富化、单 entry 边数上限 24）；attach 后重写 code-map.json 持久化
  - `scripts/run-eval.py` Scenario U 扩展（+67 行）：KG 映射 2 边（calls 0.8 + contains 1.0）断言、ghost 悬挂边剔除断言、layer 富化断言、entry ≤300t 预算断言、**无 KG 降级**（edges 空数组、不崩）断言
  - `docs/rpd-v2-technical-spec.md`：§3.3 加 edges/layer 字段表；§3.5 meta 示例加 edges 统计；新增 §3.6 edges 边信息（来源/权重/完整性/口径/降级/预算/查询）；附录 A R-19 转正
- **核心验收（真实运行）：** 有 KG → Game entry 带 calls(0.8)+contains(1.0) 两条 mapped 边 + layer=Core；ghost 边 dropped=1；entry 全 ≤300t；删 KG 后重生成 edges 空数组不崩
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** scripts/code-map-generator.py · scripts/run-eval.py · docs/rpd-v2-technical-spec.md（3 文件，+227/-3）
- **commit：** `e7db0f0` feat(I4-2): R-19 边信息复用（edges schema + KG 只读映射 + 悬挂剔除 + 降级） [advancer]
- **技术注记：** regex 降级解析器不解析 `Game::update` 限定名方法（I4-1 已知缺陷）→ KG 中此类符号/文件节点的边会正确计为悬挂剔除；eval fixture 已避开；tree-sitter 可用时此类边可解析
- **工具故障：** Edit/Write 工具本会话多处报「Not logged in」登录态校验错误 → 改用 Bash+python 补丁脚本完成所有文件修改（等义于 Edit，且带唯一命中断言），功能不受影响
- **遗留：** 向量通道 TODO（I4-1 Q1 冻结，不属本 tick）；wb-issues MCP todo 同步仍不可用（同前轮，I4-2 todo=raUZs4）


## Session: 2026-08-19（Advancer · I4-2 查询能力补齐）

### 本次会话：Verifier 判定 C 后接手，补齐 I4-2 剩余项（edges 查询能力）
- **Status:** complete（待 Verifier 复验）
- **轮次闸门：** git log -1 = `verify(I4-2): 部分完成，待继续 查询能力（谁调用X/依赖/归属）未实现 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-2（R-19 边信息复用，继续，非新模块）
- **Verifier 未达成项（本轮目标）：** task_plan.md I4-2 勾选项「查询能力：谁调用 X / X 依赖谁 / X 属于哪个架构层」未实现
- **做了什么：**
  - `scripts/retriever.py`（+151 行）：新增 R-19 edges 查询三入口 —— `resolve_symbol`（entry id → name → 末段三级解析，未解析返回 None 不猜）、`who_calls`（入向调用者：edges target 指向 X 的 entry，按 weight 降序）、`deps_of`（出向依赖：X 自身 edges，edge_type+weight 明细）、`layer_of`（entry.layer，无则 unknown）；`run_edge_query` 统一入口 + 结果集 ≤300t 预算守卫；main() 路由 `--who-calls/--deps-of/--layer-of <symbol> [--json]`
  - `scripts/run-eval.py` Scenario U（+46 行）：3f 有 KG 查询断言（who-calls helper→Game(calls 0.8)；deps-of Game→helper(calls)+main(contains 1.0)；layer-of Game→Core；未解析符号 resolved:false 空结果；全部 ≤300t）+ 3g 无 KG 降级查询断言（deps 空、layer=unknown、不崩）
  - `docs/rpd-v2-technical-spec.md` §3.6 查询能力条目补充 CLI 入口（--who-calls/--deps-of/--layer-of + 三级解析 + ≤300t）
- **核心验收（真实运行）：** 手动实跑：deps-of Game → [main(contains 1.0), helper(calls 0.8)]（63t≤300t）；layer-of Game → Core；who-calls NoSuchSymbolXYZ → resolved:false 空结果；eval 3f/3g 断言全过
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** scripts/retriever.py · scripts/run-eval.py · docs/rpd-v2-technical-spec.md（3 文件，+199）
- **工具故障：** Edit/Write 仍报「Not logged in」（同前轮）；长 heredoc 被截断 → 改用分段 heredoc + python 补丁脚本完成（等义 Edit，带唯一命中断言）
- **遗留：** 向量通道 TODO（I4-1 Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-2 todo=raUZs4）
- **下轮预期：** Verifier 复验 I4-2：7 项 0-trust + 查询能力专项（eval 3f/3g + diff 审计 + 预算守卫），PASS 后标记 I4-2 complete

## Session: 2026-08-19（Verifier · I4-2 部分完成，待继续）

### 本次会话：7 项 0-trust 验证 → 判定 C（部分完成，不回滚）
- **轮次闸门：** git log -1 = `docs(I4-2): progress 记录 R-19 边信息实现与 eval 19/19 [advancer]` → 属 Verifier 轮次 ✅；分支 automation/i4-l2 ✅
- **验证对象：** commit e7db0f0（实现）+ 1ad0c5c（progress 记录），diff 范围 70b97fc..HEAD
- **7 项检查结果：**
  1. ✅ eval 全量：`python scripts/run-eval.py` → **19/19 PASS**（A~X，exit 0）
  2. ✅ diff 审计：仅 4 文件（docs/rpd-v2-technical-spec.md +19 · progress.md +19 · scripts/code-map-generator.py +144 · scripts/run-eval.py +67），全在 I4-2「涉及文件」范围内；task_plan.md 的 Goal/Key Decisions/Phase 结构未动
  3. ✅ 预算守卫：ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300 在位；EDGE_MAX_PER_ENTRY=24；attach 后 while 裁剪至 ≤300t（code-map-generator.py:858-860）
  4. ✅ 红线机检：rpd-cold-start.py verified/unverified/stale + fingerprint 在位（:101-141）
  5. ✅ 向后兼容：SCHEMA_VERSION 2.1.0 + SCHEMA_WHITELIST (2.0.0, 2.1.0)；无 KG → edges 空数组、生成器不崩（eval 3e 断言实证）
  6. ✅ 计划一致性：task_plan.md I4-2 仍 pending（Advancer 未越权改状态）；progress 记录与 commit 内容一致
  7. ✅ 无视觉/UI 改动
- **未达成项（判定 C 依据）：** task_plan.md I4-2 勾选项「查询能力：谁调用 X / X 依赖谁 / X 属于哪个架构层」未实现：
  - `scripts/retriever.py` 全文无 `edges`/`layer` 消费（grep 零命中，仅 exact/BM25/RRF 通道）
  - `scripts/code-map-generator.py` 无查询 CLI（main 仅生成 map）
  - eval U 扩展断言覆盖数据映射（edges 映射/悬挂剔除/layer 富化/预算/降级）但**无查询断言**
  - 验收标准「层2 entry 可回答依赖/调用/归属三类问题」仅数据层达成（edges+layer 落盘），查询层缺失
- **处置：** 不回滚（改动正确）、不标 complete（验收未全达成）；保留 Advancer 成果；只 git add progress.md
- **commit：** `verify(I4-2): 部分完成，待继续 查询能力（谁调用X/依赖/归属）未实现 [verifier]`
- **下轮预期：** Advancer 接手 I4-2 剩余项——补 edges 查询能力（retriever 或独立查询入口 + eval 查询断言），完成后 Verifier 再验证

## Session: 2026-08-19（Advancer · I4-3 R-25 依赖版本锁定）

### 本次会话：实现 R-25 依赖版本锁定（清单快照 + 复合指纹 + 漂移检测 + 三级信任衔接）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-2): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-3（R-25 依赖版本锁定，第一个非 complete）
- **做了什么：**
  - `scripts/code-map-generator.py`（+84 行）：`DEPENDENCY_MANIFESTS`（21 种清单：package*.json / requirements / pyproject / Cargo / go.mod / CMakeLists 等，深度 ≤2）+ `dependency_snapshot()`（逐清单 sha256 + 复合指纹）+ `check_dependency_drift()`（指纹比对 missing/fingerprint_mismatch，无快照降级 checked:False 不崩）；meta 增 `dependencies`（detected/files/fingerprint）；generate_map 报告增 `dependency_drift`；漂移时 stderr 提示重新生成图谱
  - `scripts/rpd-cold-start.py`（+34 行）：importlib 加载连字符文件名模块（降级 no-op stub）；红线机检 `redline_check` 增第 3 支柱 `dependency_drift`；freshness 行漂移时追加 "⚠️ 依赖漂移 … 请重新生成图谱"（显式告警，不静默）
  - `scripts/run-eval.py` Scenario U 3h（+75 行）：无清单→detected:False；建 package.json 重生成→快照+复合指纹在位；冷启动无漂移 ok；改版本→fingerprint_mismatch 漂移 + freshness 含告警；删清单→missing 漂移；旧 meta 无 dependencies→checked:False 降级不崩
  - `docs/rpd-v2-technical-spec.md` 附录 A：R-25 转正（草案 → 已落地）
- **核心验收（eval 3h 真实运行）：** 依赖清单创建/变更/删除三种漂移均可被检测并提示；无快照降级不崩；三级信任状态机不受影响
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** scripts/code-map-generator.py · scripts/rpd-cold-start.py · scripts/run-eval.py · docs/rpd-v2-technical-spec.md（4 文件，+193/-2）
- **commit：** `61908d4` feat(I4-3): R-25 依赖版本锁定（依赖清单快照 + 复合指纹 + 漂移检测集成冷启动红线机检） [advancer]
- **工具故障：** Edit/Write 仍报「Not logged in」（同前轮）；Bash heredoc 中 `\n` 多层转义成真实换行 → 改用 `chr(10)` 等义修复（经验：嵌套 python - << 'EOF' 内嵌字符串转义要逐层核查）
- **技术注记：** `code-map-generator.py` 连字符文件名无法普通 import → cold-start 用 importlib.util.spec_from_file_location 加载，失败降级 no-op stub（eval 3h 断言覆盖）
- **遗留：** wb-issues MCP todo 同步仍不可用（同前轮，I4-3 todo=rnAxRa）；向量通道 TODO（Q1 冻结）
- **下轮预期：** Verifier 复验 I4-3：7 项 0-trust + R-25 专项（eval 3h + diff 审计 + 预算守卫 + 向后兼容降级），PASS 后标记 I4-3 complete

## Session: 2026-08-19（Advancer · I4-4 R-20 PRD↔代码影响分析）

### 本次会话：实现 R-20 影响分析器（impact-analyzer.py 双向映射 + 1-hop + 风险分级 + 降级）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-3): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-4（R-20 PRD↔代码影响分析，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/impact-analyzer.py`（429 行）：`parse_prd`（从 RPD PRD 模板解析功能列表表格/页面标题/MVP，Q3）+ `_entry_hits`（精确名4>名子子串 3>文件 2>doc/sig 1）+ `_hop1_neighbors`（edges+calls+called_by 1-hop）+ `_grade_blast`（changed≥5/layers≥3=Critical）+ `_degrade_scan`（无 code-map 直接扫描）；双向入口 `analyze_prd_to_code` / `analyze_code_to_prd`；CLI `--prd` / `--code-to-prd`；结果载荵≤300t
  - `scripts/run-eval.py` Scenario U 扩展（+110 行）：3i-1 PRD→code（changed=Game + affected=helper(1-hop) + layer Core + blast）；3i-2 code→PRD（Game 反查命中）；3i-3 未解析降级；3i-4 无 code-map 直接扫描降级
  - `docs/rpd-v2-technical-spec.md`：新增 §3.7 PRD↔代码影响分析（双向/分级标准/降级/预算）+ 附录 A R-20 转正
- **核心验收（eval 3i 真实运行）：** PRD 功能“Game”→ changed=Game；1-hop（R-19 edges）涌出 helper；层 Core 报告；blast 分级有效；c→PRD 反查命中“Game”；无 code-map 降级扫描找到 game.cpp/game.h
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0）
- **Files modified:** scripts/impact-analyzer.py（新增）· scripts/run-eval.py· docs/rpd-v2-technical-spec.md· progress.md（本日志）
- **技术注记：** regex 降级解析器不解析限定名方法（I4-1 已知缺陷）→ eval 3i fixture 将 helper/main 放 utils.cpp 避开；“Game”子串会命中 game.cpp 文件级入口（特征性而非 bug）
- **工具故障：** Edit/Write 持续报「Not logged in」（同前轮）→ Bash heredoc 多层转义（`\n` 变真实换行）造成 run-eval 语法破坏→ 终于采用 **base64 包装 + chr(10) 拼接** 等义修复（经验：嵌套 heredoc 写 python 字符串一律用 chr(10) 或 base64）
- **遗留：** 向量通道 TODO（Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-4 todo=rsO1C9）
- **下轮预期：** Verifier 复验 I4-4：7 项 0-trust + R-20 专项（eval 3i + diff 审计 + 预算守卫 + 向后兼容降级），PASS 后标记 I4-4 complete

## Session: 2026-08-20（Advancer · I4-5 R-23 渐进式暴露）

### 本次会话：实现 R-23 渐进式暴露（exposure-guard.py 三层注入 + 深入追问闸门 + 任务级双预算）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-4): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-5（R-23 渐进式暴露，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/exposure-guard.py`（297 行）：三层暴露 L1 router 常驻（≤3000t）/ L2 entry 按需单条（≤300t）/ L3 语义摘要（≤500t，Q4）；深入追问闸门（DEEP_FOLLOWUP_TURNS=2，deep<N 越级拦截 blocked_reason=deep_followup_required + 降级提示）；任务级双预算（entries≤24 + tokens≤2000）；未解析/无 code-map 降级提示不崩溃；CLI `--l1/--entry/--summary --deep`
  - `scripts/rpd-cold-start.py`（+48 行）：importlib 加载 exposure-guard（同 R-25 模式，失败降级 no-op stub）；step04 增 `exposure_layers` 报告（checked/L1-L3 allowed+limit+est/task_budget）
  - `scripts/run-eval.py` Scenario U 3j（+54 行）：3j-1 L1≤3000t 允许 / 3j-2 L2≤300t 解析 / 3j-3 L3 deep=0 拦截 / 3j-4 L3 deep=2 放行≤500t / 3j-5 未解析降级 / 3j-6 双预算 ok / 3j-7 cold-start exposure_layers checked
  - `docs/rpd-v2-technical-spec.md`：新增 §3.8 渐进式暴露（三层/双预算/实现/降级）+ 附录 A R-23 转正
- **核心验收（eval 3j 真实运行）：** L1 allowed 246t≤3000t；L2 Game 30t≤300t；L3 deep=0 blocked(deep_followup_required) → deep=2 allowed 39t≤500t；未解析 NoSuchSymbolXYZ 降级；task_budget entries=2≤24/tokens=69≤2000 ok；cold-start step04 exposure_layers checked=True
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；3j 断言行实际执行 ✅ R-23 exposure）
- **Files modified:** scripts/exposure-guard.py（新增 297）· scripts/rpd-cold-start.py（+48）· scripts/run-eval.py（+54）· docs/rpd-v2-technical-spec.md（+8）· progress.md（本日志）
- **commit：** `56076ca` feat(I4-5): R-23 渐进式暴露（三层注入 + 深入追问闸门 + 任务级双预算） [advancer]
- **工具故障：** Write/Edit 仍报 Not logged in（同前轮）→ 分段 heredoc + python 补丁脚本完成（等义 Edit/Write，带唯一命中断言）；bash mktemp -d 路径 Windows Python 不识别 → 改用 python tempfile 驱动冒烟测试
- **技术注记：** 冒烟测试发现 run_exposure 首版不支持独立 --entry（L2 仅随 summary 构建）→ 补丁加 entry_symbol 参数修复；3i-4 删 .rpd 后 3j 需先重生成 code-map
- **遗留：** 向量通道 TODO（Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-5 todo=rvXVu0）
- **下轮预期：** Verifier 复验 I4-5：7 项 0-trust + R-23 专项（eval 3j + diff 审计 + 预算守卫 + 向后兼容降级），PASS 后标记 I4-5 complete

## Session: 2026-08-20（Verifier · I4-5 判定 A）

### 本次会话：7 项 0-trust 验证 → 判定 A（complete）
- **轮次闸门：** git log -1 = `docs(I4-5): progress 记录 R-23 渐进式暴露实现与 eval 19/19 [advancer]` → 属 Verifier 轮次 ✅；分支 automation/i4-l2 ✅
- **验证对象：** commit 56076ca（实现）+ d8e713a（progress），diff 范围 b92e48c..HEAD
- **7 项检查结果：**
  1. ✅ eval 全量：`python scripts/run-eval.py` → **19/19 PASS**（A~X，exit 0；Scenario U 3j 断言行实际打印 "R-23 exposure: 3-layer progressive + deep follow-up gate + dual budget + cold-start report"）
  2. ✅ diff 审计：仅 5 文件（scripts/exposure-guard.py 新增 307 · scripts/rpd-cold-start.py +48 · scripts/run-eval.py +54 · docs/rpd-v2-technical-spec.md +8 · progress.md +20），全在 I4-5「涉及文件」范围（SKILL.md 未动——三层暴露落在 exposure-guard.py 独立模块，注入策略由 cold-start 集成）；task_plan.md 的 Goal/Key Decisions/Phase 结构未动
  3. ✅ 预算守卫：ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300 未回归（code-map-generator.py:46-49）；新增 SUMMARY_MAX_TOKENS=500（Q4）+ TASK_ENTRY_BUDGET=24 + TASK_TOKEN_BUDGET=2000（exposure-guard.py:45-49）
  4. ✅ 红线机检：三级信任 verified/unverified/stale + fingerprint 在位（rpd-cold-start.py:169-213），新增 exposure 为独立函数不触碰 redline_check 逻辑
  5. ✅ 向后兼容：SCHEMA_VERSION 2.1.0 + SCHEMA_WHITELIST (2.0.0, 2.1.0) 在位（code-map-generator.py:50,62）；无 code-map → exposure 各层 no_code_map 降级提示不崩（冷启动实测 exposure checked:true 走降级）
  6. ✅ 计划一致性：task_plan.md I4-5 仍 pending（Advancer 未越权改状态）；progress 记录与 commit 内容一致
  7. ✅ 无视觉/UI 改动；R-23 专项用真实 C++ 项目（独立 fixture）+ 真实 code-map 复测
- **R-23 专项实测（0-trust 手动复跑，真实 C++ 项目 + 真实 code-map，.workbuddy/tmp/r23-verify-*/）**：L1 allowed 241t≤3000t / L2 Game resolved 30t≤300t / L3 deep=0 → blocked(deep_followup_required) / L3 deep=2 → allowed 39t≤500t / task_budget entries=2≤24 tokens=69≤2000 ok / 未解析 NoSuchSymbolXYZ → L2 resolved:false + L3 blocked(unresolved) 不猜 —— 全部通过
- **验收标准核对：** ①冷启动注入不超预算（L1 241t≤3000t）✅ ②双预算守卫生效（24 条/2000t 实测）✅ ③I0~I3 既有行为不回归（eval A~W 全过）✅
- **处置：** 判定 A —— task_plan.md I4-5 Status → complete（仅状态标记）；progress.md Test Results 追加验证行（真实数字）
- **commit：** `verify(I4-5): 7 项 0-trust 全过 [verifier]`（仅 add task_plan.md progress.md）
- **经验：** ①R-23 三层预算 3000/300/500 与 TAM 三重预算对齐，Q4「深入追问=2 轮」落地为 DEEP_FOLLOWUP_TURNS 常量；②exposure-guard 复用 retriever 的 resolve_symbol/load_code_map/estimate_tokens，standalone 降级 stub 与 I4-2/I4-3 同族模式（importlib 加载连字符文件名）；③cold-start 集成 exposure_layers 走「独立函数 + importlib + 异常降级」三保险，红线机检主体不受影响
- **下轮预期：** Advancer 接手 I4-6（R-21 L0-L3 分层记忆）

## Session: 2026-08-20（Advancer · I4-6 R-21 L0-L3 分层记忆）

### 本次会话：实现 R-21 分层记忆（memory-layers.py 四层 + 过期 + 回退 + 膨胀守卫 + cold-start 集成）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-5): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-6（R-21 L0-L3 分层记忆，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/memory-layers.py`（508 行）：四层落点 L0 证据（sha256 指纹索引，内容不常驻）/ L1 原子 / L2 场景（scope 过滤）/ L3 画像；分层读写 + 过期规则（`expires` 字段，`--expired` 标记可读、`--drop-clean` 才物理删）+ 检索回退（默认 fast-path L2+L3 → `--fact` 回退 L1 → `--evidence` 回退 L0 指纹比对；miss 返回 resolved:false + fallback_evidence 不猜）+ 单层膨胀守卫（`--stats` L1>500/L2>200 告警）+ `--import-decisions`（只读提取 accepted 决策为 L1 原子 + decisions.md 登记 L0，grill-me 写入权不受影响）；全路径降级不崩（无 store / 损坏 / 缺 decisions.md 均 ok）
  - `scripts/rpd-cold-start.py`（+44 行）：importlib 加载 memory-layers（同 R-23 模式，失败降级 stub）；step01 增 `memory` 报告（checked/counts/expired/warnings/fallback/fast_path/scenario_count/profile_count）
  - `scripts/run-eval.py` Scenario U 3k（+96 行）：3k-1 空库降级 / 3k-2 决策导入（只 accepted）/ 3k-3 fact 命中+miss 不猜 / 3k-4 L2/L3 供给 / 3k-5 过期+drop / 3k-6 证据指纹翻转 / 3k-7 膨胀守卫 / 3k-8 cold-start memory 报告 —— 8 组断言
  - `docs/rpd-v2-technical-spec.md`：新增 §3.9 L0-L3 分层记忆（四层定义/读写过期/检索回退/降级/涉及文件）+ 附录 A R-21 转正
- **核心验收（eval 3k 真实运行）：** 无 store 降级 ok（path=L2+L3 空）；import-decisions 只导入 accepted D-1（imported=1 total_accepted=1）；--fact 零依赖→命中 d1；--fact 不存在→resolved:false+fallback_evidence（不猜）；fast-path 只供 L2(scope)+L3；过期原子 m9 标记→drop-clean 删除；decisions.md 指纹变更→content_matches False；--stats counts/warnings 在位；cold-start step01 memory checked=True
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；3k 断言行实际打印 "R-21 memory: L0-L3 layers + expiry + fallback + bloat guard + cold-start report"）
- **Files modified:** scripts/memory-layers.py（新增 508）· scripts/rpd-cold-start.py（+44）· scripts/run-eval.py（+96）· docs/rpd-v2-technical-spec.md（+56）· progress.md（本日志）
- **工具故障：** Write/Edit 持续报 Not logged in（同前轮）→ Bash heredoc + python 补丁脚本完成（等义 Edit/Write）；heredoc 嵌套 `\n` 转义成真实换行损坏 run-eval → 用 chr(10) 等义修复（经验复用：I4-3/I4-4 已记）
- **技术注记：** `_next_val` 解包顺序写反导致 CLI 变量错位 → 整体重写 main() 修复；`_norm_evidence_key` 最初剥掉 .rpd/ 前缀导致 L0 证据指纹校验路径错 → 改为保留前缀（key 兼作项目相对路径）；fast-path 默认 scope=project，scope=prd 的场景需 `--list --layer L2` 验证（eval 断言已对齐）
- **遗留：** 向量通道 TODO（Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-6 todo=rZEKBI）
- **下轮预期：** Verifier 复验 I4-6：7 项 0-trust + R-21 专项（eval 3k + diff 审计 + 预算守卫 + 膨胀控制 + 兼容降级），PASS 后标记 I4-6 complete

## Session: 2026-08-20（Advancer · I4-7 parking-lot 治理机制）

### 本次会话：实现 parking-lot 治理（scripts/parking-lot.py 四档触发 + 升级三要素 + 承诺守卫 + eval 3l）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-6): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-7（parking-lot 治理机制，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/parking-lot.py`（348 行）：四档触发机检 —— T1 依赖就绪（探测 scripts/ 实现模块 + 事实兜底）/ T2 用户信号（≥3）/ T3 成本收益翻转（人工置位）/ T4 定期复核（review_due）；`--audit` 输出每 entry 四触发 ready 判定；升级三要素（`--id/--impact/--budget` 缺一 exit 1，无触发就绪 exit 2 拒绝，`promotion needs evidence`）；`--promise-check` 承诺守卫（冻结条目禁"已规划交付"类措辞）；`--add/--remove/--summary`；存储 `.rpd/parking-lot.json`（versioned）；**全路径降级**（无 store → 内置五条目 R-24/26/27/28/29 只读；损坏 json → builtin 不崩）
  - `scripts/run-eval.py` Scenario U 3l（+77 行）：8 组断言 —— 3l-1 空库 builtin 5 条目 / 3l-2 audit 四触发可机检（threshold=3、R-28 因依赖 R-26 未落地 dependency_ready=False）/ 3l-3 promise-check 零违规 / 3l-4 缺 budget 拒绝 exit 1 / 3l-5 幽灵需求 R-95（deps R-99）无触发 exit 2 / 3l-6 用户信号≥3 升级成功 + 落盘 store 持久化 / 3l-7 预算 LIST_LIMIT=50 / 3l-8 损坏 store 降级 builtin
  - `docs/rpd-v2-technical-spec.md`：附录 A R-24 转正 + 新增 R-26/27/28/29 行；新增附录 C「parking-lot 治理清单」（四档触发表 + 升级三要素 + 承诺守卫 + 登记 5 条目 + 当前 audit 实测）
- **核心验收（eval 3l 真实运行）：** 空库降级 ok（builtin 5 条目）；--audit 四触发逐条可机检（R-28 dependency_ready=False 因缺 R-26）；--upgrade 缺要素拒绝（exit 1）/ 无触发拒绝（exit 2）/ 用户信号就绪放行并落盘；--promise-check 冻结条目零承诺违规；损坏 store 降级不崩
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；3l 断言行实际打印 "R-24/R-26~R-29 parking-lot: four-trigger audit + 3-element promotion gate + promise guard + degrade"）
- **Files modified:** scripts/parking-lot.py（新增 348）· scripts/run-eval.py（+77）· docs/rpd-v2-technical-spec.md（+39）· progress.md（本日志）
- **commit：** `11ee591` feat(I4-7): R-24/R-26~R-29 parking-lot 四档触发机检 + 升级三要素 + 承诺守卫 [advancer]
- **工具注记：** 本 tick Write/Edit 恢复正常（未再报 Not logged in）；Bash heredoc 中 `'PYEOF'` 单引号内容含单引号字符串导致 bash 解析断裂 → 改用 Write 工具直接写入成功
- **技术注记：** 内置五条目 deps 全部已落地（R-19/21/22 均已实现），因此 `--audit` 下 R-24/26/27/29 的 dependency_ready 均为 True——机检真实性依赖脚本探测（scripts/ 模块存在性），未来重命名模块需同步 IMPLEMENTING_SCRIPTS
- **遗留：** 向量通道 TODO（Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-7 todo=r7Madr）
- **下轮预期：** Verifier 复验 I4-7：7 项 0-trust + 四档触发专项（eval 3l + diff 审计 + 预算守卫 + 降级），PASS 后标记 I4-7 complete → 下一 Advancer 接 I4-8

## Session: 2026-08-20（Advancer · I4-8 测试与验证 / I4 出口 Gate）

### 本次会话：实现 I4 出口 Gate 机检（i4-gate.py M1/M2 + M3 观测 + 回归守卫 + eval 3m）
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-7): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-8（测试与验证，第一个非 complete）
- **做了什么：**
  - 新建 `scripts/i4-gate.py`（约 330 行）：I4 出口 Gate（Q5）—— **M1 理解连续性 A/B 机检**（arm A 有 map：retriever 按 map 导航解析已知符号 + entry ≤300t；arm B 无 map：显式 source-scan 降级 `degrade (explicit, no guess)`，诚实降级不猜）+ **M2 PRD 变更闭环机检**（importlib 复用 impact-analyzer.analyze_prd_to_code：PRD feature → changed/affected(1-hop)/layers/blast，feature 命中 changed 且载荷 ≤300t）+ **M3 文档引用观测**（Q5：observation only，永不阻断）+ **回归守卫**（静态检查预算 ROUTER_TOKEN_LIMIT/ENTRY_MAX_TOKENS、红线 verified/stale/dependency_drift、兼容 SCHEMA_VERSION/SCHEMA_WHITELIST 三组在位）；exit 0 PASS / 1 用法错 / **2 诚实 FAIL**（无 map 时 M2 如实失败，非橡皮图章）
  - `scripts/run-eval.py` Scenario U 追加 **3m**（+24 行）：3m-1 带 map+PRD → gate PASS（M1 arm A 解析 Game、M2 changed 含 Game、M3 observation 注记、回归 3 findings 全 ok）+ 3m-2 移走 code-map → gate exit 2 如实 FAIL（M1 arm B 降级、M2 ok:false）后恢复
  - `docs/rpd-v2-technical-spec.md`：新增 **§3.10 I4 出口 Gate**（机检项定义表 / 诚实失败语义 / 涉及文件）+ §16.2 追加 I4 出口 Gate 注记（Q5 落地口径）
- **核心验收（eval 3m 真实运行）：** 带 map+PRD → exit 0 PASS（M1 arm A map_resolved=True entry 93t≤300t；M2 changed=[Game,helper,main] blast High 203t≤300t；回归 3/3 ok）；移走 map → exit 2 如实 FAIL（M1 arm B source_scan、M2 ok:false）—— Gate 不因降级路径放行丢失闭环
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；3m 断言行实际打印 "I4-8 exit gate (Q5): M1 A/B continuity + M2 PRD loop + M3 observation + regression guard + honest fail"；提交后复跑仍 19/19）
- **Files modified:** scripts/i4-gate.py（新增）· scripts/run-eval.py（+24）· docs/rpd-v2-technical-spec.md（+38）· progress.md（本日志）
- **技术注记：** M2 复用 impact-analyzer 的 `_entry_brief` 结构（name/kind/file/layer）与 `_enforce_budget`（budget.estimated_results_tokens）；i4-gate 静态回归守卫用源码字符串在位检查（零依赖、跨文件常量名耦合低——若未来改名需同步 i4-gate 的 needle）
- **遗留：** 向量通道 TODO（Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-8 todo=rMym7V）；I4-8 剩余项（X 行为人工核验清单、M3 观测基线）留 I4-9 或 Verifier 判定
- **下轮预期：** Verifier 复验 I4-8：7 项 0-trust + Q5 出口 Gate 专项（eval 3m + diff 审计 + 预算守卫 + 诚实失败语义），PASS 后标记 I4-8 complete → 下一 Advancer 接 I4-9

## Session: 2026-08-21（Advancer · I4-9 文档与交付）

### 本次会话：I4-9 收尾 — spec 验收补齐 / usage 速查 / SKILL 工具箱对齐 / 状态文件初始化
- **Status:** complete（待 Verifier 验证）
- **轮次闸门：** git log -1 = `verify(I4-8): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **模块：** I4-9（文档与交付，第一个非 complete；I4-0~I4-8 均 complete）
- **做了什么：**
  - `docs/rpd-v2-technical-spec.md`：§16.1 需求池验收表补齐 R-19~R-29 验收行（R-19~R-25 转正·R-26~R-29 parking-lot 冻结，口径与 progress Test Results Verifier 实测一致）；§17.1 实施顺序追加 I4 外扩顺序 + Q1~Q5 依赖说明
  - `docs/rpd-v2-usage.md`：新增 §11「I4 外扩能力速查」——6 个新脚本 CLI 入口（retriever/impact-analyzer/exposure-guard/memory-layers/parking-lot/i4-gate）+ 冷启动 memory/exposure 集成报告 + 诚实失败语义
  - `SKILL.md`：Script Toolbox 由 12 行扩到 18 行（补 retriever/impact-analyzer/exposure-guard/memory-layers/parking-lot/i4-gate），压缩既有描述保持 ≤8KB —— 实测 **8116 B ≤ 8192 B（R-05 不破）**
  - `.project-state.md`（新建）：按 state-file-spec 初始化 RPD-skill 自身状态（frontmatter + 功能进度/决策/诊断/阻塞/变更日志），`state-validator.py` **Validation PASSED exit 0**
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；X 行为级提示维护者手动核验属正常旁注）
- **Files modified:** docs/rpd-v2-technical-spec.md（+11 验收行 + 顺序链）· docs/rpd-v2-usage.md（+§11）· SKILL.md（工具箱 +6 行）· .project-state.md（新建）· progress.md（本日志）
- **commit：** 待 Verifier 复验后写入下方 Test Results
- **遗留：** 向量通道 TODO（R-22 Q1 冻结）；wb-issues MCP todo 同步仍不可用（I4-9 todo=rDdzl2）；SKILL.md 版本史未动（CLAUDE.md 版本表由用户在发布时更新）
- **下轮预期：** Verifier 复验 I4-9：7 项 0-trust + 文档一致性（spec/usage/SKILL 与实现对齐 + SKILL ≤8KB + 状态文件可校验）+ diff 审计，PASS 后标记 I4-9 complete → I4 收官

---

## Session: 2026-08-21（Advancer · I4 收官报告）

### 本次会话：I4 全部模块 complete 后的收官报告（交付清单 + 验证证据 + 下一步建议）
- **Status:** complete（I4 外扩迭代收官）
- **轮次闸门：** git log -1 = `verify(I4-9): 7 项 0-trust 全过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **触发：** task_plan.md Phase I4-0~I4-9 全部 complete → 按第2步规则，本 tick 写 I4 收官报告
- **eval 真实结果：** `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，exit 0；I4 专项断言行 R-19~R-25 + exit gate 全部实际打印 ✅）

### 📦 I4 交付清单（10 模块，6 新脚本 + 4 文档/SKILL 改动）
| 模块 | 交付 | commit | Verifier 判定 |
|------|------|--------|--------------|
| I4-0 | 基线核对：eval 基线 19/19 + R-19~R-25 草案入规格附录 A + Q1~Q5 拍板 | a9af0b7（docs） | ✅ A（2026-08-19） |
| I4-1 | `retriever.py` R-22 混合检索（exact + BM25 + RRF，零依赖，向量 TODO） | aa0bb2c | ✅ A |
| I4-2 | R-19 边信息：edges schema 2.1.0 + KG 只读映射 + 悬挂剔除 + who-calls/deps-of/layer-of 查询 | 68e0f4e | ✅ A（含补查轮） |
| I4-3 | R-25 依赖锁定：清单快照 + 复合指纹 + 漂移检测 + 冷启动第 3 支柱 | 61908d4+eb9f56c | ✅ A |
| I4-4 | `impact-analyzer.py` R-20 PRD↔代码双向映射 + 1-hop + blast 分级 | 4076938 | ✅ A |
| I4-5 | `exposure-guard.py` R-23 三层渐进暴露 + 追问闸门 + 双预算 | 56076ca+d8e713a | ✅ A |
| I4-6 | `memory-layers.py` R-21 L0-L3 分层记忆 + 过期 + 回退 + 膨胀守卫 | 94220bf | ✅ A |
| I4-7 | `parking-lot.py` 四档触发机检 + 升级三要素 + 承诺守卫 + R-24/26~29 登记 | 11ee591+ad76b15 | ✅ A |
| I4-8 | `i4-gate.py` Q5 出口 Gate（M1 连续性 A/B + M2 PRD 闭环 + M3 观测 + 回归守卫 + 诚实失败） | 79ad7b6 | ✅ A |
| I4-9 | 文档交付：spec 验收补齐 + usage §11 速查 + SKILL 工具箱 18 行 ≤8KB + .project-state.md | 4c40084 | ✅ A（2026-08-21） |

### 🧪 验证证据（全部真实运行，0-trust）
- eval 基线：**19/19 PASS，exit 0**（本 tick 复跑确认；I4 专项断言行 R-19~R-25 + exit gate 实际打印）
- 预算守卫全程未破：router 3000t / 单条 entry 300t / L3 摘要 500t（Q4）/ 任务双预算 24 条 2000t / edges 单 entry 24 上限；专项实测载荷 30~246t 均 ≤ 上限
- R-10 向后兼容：SCHEMA 2.1.0 + 白名单(2.0.0, 2.1.0) + 全路径降级（无 KG / 无 code-map / 无 store / 损坏 store / 缺 decisions.md 均不崩）
- 红线机检：三级信任 + stale + dependency_drift 三支柱持续在位（rpd-cold-start.py:141/211-255）
- 每模块 diff 审计均「仅预期文件」；task_plan.md 结构全程未动；无视觉/UI 改动故无截图需求

### 🔭 下一步建议（L3 未来三支柱 / parking-lot 升级）
1. **parking-lot 四档触发持续机检**：`python scripts/parking-lot.py --audit` 定期跑（R-26/28 依赖就绪后可评估升级）
2. **L3 阶段 A（补漏）候选**：R-24 经验资产化（依赖 R-21 记忆层已就绪，dependency_ready=True 实测）；向量通道 TODO（需外部 embedding 依赖，触发 T3 成本收益翻转后再议）
3. **L3 阶段 B/C**：ACL（R-26）/ 全图影响 2-hop（R-27）/ 团队记忆（R-28）/ 多语言（R-29）—— 均冻结在 parking-lot，按用户信号 ≥3 或成本收益翻转升级
4. **收尾事项**：wb-issues MCP 恢复后同步 10 条 I4 todo 状态（I4-0~I4-9 各 todo id 见 2026-08-19 会话）；SKILL.md 版本史由用户在发布时更新 CLAUDE.md 版本表
- **Files modified:** progress.md（5-Question Reboot Check 更新 + 本收官报告）
- **commit：** 本 tick 仅文档报告，commit 信息见下方实际值
- **交棒：** 本 tick 结束，I4 收官；后续 tick 无需 Advancer 推进（L3 无排期），由 automation 管理员决定是否停用本自动化或转为 L3 观察任务

---

## 2026-08-29 19:1x（Verifier tick · 治理提案复验）

- **轮次闸门**：`git log -1` = `docs(I4-closeout): 自动化治理提案... [advancer]` → 属 Verifier 轮次 ✅；分支 `automation/i4-l2` ✅
- **验证对象**：commit `562c14b`（Advancer tick #63 固化治理提案）
- **7 项 0-trust**：1.eval 19/19 PASS exit 0 ✅ · 2.commit 真实 diff 仅 `docs/automation-governance-proposal.md`（+102/-0），task_plan.md 零改动 ✅ · 3.预算守卫 3000/300 在位 ✅ · 4.三级信任+stale 在位 ✅ · 5.SCHEMA 2.1.0+白名单在位 ✅ · 6.计划一致性：I4-0~I4-9 全 complete，无 pending，本 commit 未越权改状态 ✅ · 7.纯文档无视觉改动 ✅
- **0-trust 延伸核查**：提案文档 §二 给用户的 `automation_update(mode="update", id="automation-1787109094822", status="PAUSED")` 指令 → 用 automation_update(list) 核实该 ID **真实存在**（「I4-推进（Advancer）」ACTIVE），指令可执行；文档亦明示「待张敬拍板，不擅自改配置」，未实际执行 ✅
- **判定 A 处置**：progress.md Test Results 追加验证行（真实数字）；无 pending Phase 需标 complete（I4 全模块已收官），故 task_plan.md 未动
- **⚠️ 刻意保留 Advancer 未提交日志**：worktree 中 Advancer tick #51~#63 的 143 行空转日志**未纳入本次 commit** —— 提案文档 §三 的 D2 压缩方案依赖「日志仍处未提交状态」才能免于历史改写；Verifier 若顺手提交将永久关闭该选项。已备份至 `.workbuddy/tmp/progress-worktree-20260829-1910.md` 并在 commit 后原样恢复为未提交状态
- **待用户拍板**：D1（本自动化 A 停用 / B 降频周观察 / C 转按需触发 / 维持现状）+ D2（progress.md 空转日志是否授权压缩）

---

> ℹ️ 以下为 Advancer tick #51~#63 的未提交空转日志（Verifier 2026-08-29 19:1x 刻意保留其未提交状态，以免关闭 D2「免历史改写压缩」选项；原文件已备份至 `.workbuddy/tmp/progress-worktree-20260829-1910.md`）

---

## 2026-08-23 05:1x（tick #51 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ git status（worktree 仅 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md，无关）+ 复跑 eval 基线健康确认
- **改了哪些文件**：无（未 commit，避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 36 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 06:1x（tick #52 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#51；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 37 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 07:1x（tick #53 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#52；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 38 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 08:1x（tick #54 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#53；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 39 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 09:1x（tick #55 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#54；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete，仅 L3 planned 冻结）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 40 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 10:1x（tick #56 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#55；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete，仅 L3 planned 冻结）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 41 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 11:1x（tick #57 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#56；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete，仅 L3 planned 冻结）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 42 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-23 12:1x（tick #58 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#57；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete，仅 L3 planned 冻结）/ progress（Test Results 全 Verifier 判定 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 段无遗留）/ automation-rules（8 红线）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 仅 progress.md 本地追加日志（未提交）+ 1 未跟踪交接文档 docs/handoff-automation-2026-08-19.md（无关，不 commit）
- **改了哪些文件**：progress.md（追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 43 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）

---

## 2026-08-29 12:1x（tick #59 · I4 Advancer，间隔 6 天后首次触发）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#58；收官报告 27f7fd5 已交付且被 Verifier 复验通过 5aebe97；task_plan L3 planned 冻结，非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress（Test Results 全 A + 收官报告 + Error Log 无待办）/ findings（资产台账 + Issues 无遗留）/ automation-rules（8 红线 + Advancer 工作流）+ 复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；worktree 状态：`M progress.md`（历史 42 条空转日志累计未提交）+ `?? docs/handoff-automation-2026-08-19.md`（无关，不 commit）
- **改了哪些文件**：progress.md（仅追加本 tick 日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 44 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务）
- **新增建议（治理债）**：progress.md 已累计 #17~#59 共 43 条内容重复的空转日志（约 300 行、占文件 60%+），建议授权一次性压缩为「2026-08-21~08-29 空转期汇总」单条记录，之后空转 tick 只追加一行；压缩属历史改写，需用户授权后由 Advancer 执行或交 Verifier 复核。

---

## 2026-08-29 13:1x（tick #60 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#59；L3 planned 冻结）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress / findings / automation-rules；复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；分支 automation/i4-l2 ✅；worktree 仅 `M progress.md` + `?? docs/handoff-automation-2026-08-19.md`（无关）
- **改了哪些文件**：progress.md（仅追加本条日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次）
- **eval 真实数字**：19/19 PASS，exit 0
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 45 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）；治理债压缩仍待用户授权。

---

## 2026-08-29 14:1x（tick #61 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#60；L3 planned 冻结，非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete，L3 planned 冻结）/ progress / findings / automation-rules；复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`All scenarios passed!`）；分支 automation/i4-l2；worktree 仅 `M progress.md` + `?? docs/handoff-automation-2026-08-19.md`（无关）
- **改了哪些文件**：progress.md（仅追加本条日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0
- **commit hash**：无
- **遗留问题**：本自动化已无可推进工作（第 46 次重申：建议停用 automation-1787109094822 或转为 L3 观察任务 / 绑定 parking-lot 四档触发）；治理债压缩仍待用户授权。

---

## 2026-08-29 15:1x（tick #62 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全部 complete，同 tick #17~#61；L3 planned 冻结，非 I4 排期）
- **做了什么**：只读核对 task_plan（10 Phase 全 complete）/ progress（Test Results + 收官报告 + Error Log 无待办）/ findings / automation-rules（8 红线）；复跑 `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过，`🎉 All scenarios passed!`）；分支 automation/i4-l2 ✅
- **本 tick 唯一产出**：新建 `docs/automation-governance-proposal.md` —— 把连续 46 次空转的治理决策点固化为可执行提案（三选项：A 停用 / B 降频为周观察 / C 转 parking-lot 按需触发，推荐 A；含 progress.md 空转日志压缩方案，需授权）。**不再重复第 47 次同一句"建议停用"，改为给出一句话即可执行的选择题。**
- **改了哪些文件**：新增 docs/automation-governance-proposal.md（未 commit）+ progress.md（仅追加本条日志，未 commit——避免空转 [advancer] 交棒触发空 Verifier 轮次、污染 diff 审计）
- **eval 真实数字**：19/19 PASS，exit 0
- **commit hash**：无
- **遗留问题**：待张敬拍板 D1（自动化处理方式 A/B/C）+ D2（是否授权压缩 progress.md 空转日志）；拍板前本自动化保持每小时空转。

---

## 2026-08-29 16:1x（tick #63 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全 complete；L3 planned 冻结）
- **本 tick 产出**：把 tick #62 新建的 `docs/automation-governance-proposal.md` 更新计数（空转 47 次）+ 追加「tick 日志改归 automation memory、progress.md 停止膨胀」自我约束条款，并 commit 固化（唯一入 diff 文件）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）；分支 automation/i4-l2 ✅；未 push、未触碰 main
- **遗留问题**：待张敬拍板 D1（A 停用 / B 降频周观察 / C 按需触发）+ D2（progress.md 空转日志压缩授权）

---

## 2026-08-29 20:1x（tick #64 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全 complete；L3 planned 冻结）。闸门：`378b2f2 verify(I4-closeout): ...治理提案文档验证通过 [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`）。治理提案 `562c14b` 已被 Verifier 复验通过 → D1/D2 决策点已入仓库历史，等张敬拍板；本 tick 无新交付，**未 commit**（避免空转 [advancer] 交棒触发空 Verifier）。tick 明细按 tick #63 约定记入 automation memory，此处仅 3 行。
- **遗留问题**：D1/D2 未拍板；worktree 仍 `M progress.md`(+147 行未提交) + `?? docs/handoff-automation-2026-08-19.md`；本自动化 valid_until 2026-08-31，届时自动到期。

---

## 2026-08-29 21:1x（tick #65 · I4 Advancer）

- **模块**：无待推进（I4-0~I4-9 全 complete；L3 planned 冻结）。闸门：`378b2f2 ... [verifier]` → 本轮属 Advancer；分支 automation/i4-l2 ✅
- **本 tick 唯一产出**：`docs/handoff-automation-2026-08-19.md` 从未跟踪状态入仓（已躺 10 天，工作区一清理就丢），并追加 §八「2026-08-29 状态校正」—— 逐项校正文件里已过期的信息：自动化 ID（5867270/5867281 → 现 `automation-1787109094822`）、valid_until（2026-09-19 → 2026-08-31）、I4 进度（I4-0 部分完成 → 全部 complete）；另注明第二节 10 条 todo 因 wb-issues 工具长期不可用已失真，进度一律以 task_plan.md 为准
- **改了哪些文件**：docs/handoff-automation-2026-08-19.md（新增入仓 + 状态校正段）、progress.md（仅本条日志）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`，改动后复跑确认）
- **commit hash**：见提交结果
- **遗留问题**：D1/D2 未拍板（见 docs/automation-governance-proposal.md）；自动化 2026-08-31 到期后需人工处理；本 tick 提交后 worktree 恢复干净

---

## 2026-08-29 22:1x（tick #67 · I4 Verifier · 判定 A）

- **轮次闸门**：`3bb5666 docs(I4-closeout): 交接文档入仓并校正过期自动化信息... [advancer]` → 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；工作区提交前干净 ✅
- **7 项 0-trust 逐项实测**：①eval 19/19 PASS exit 0（真实复跑 `python scripts/run-eval.py`）✅ ②diff 审计 `git diff HEAD~1 HEAD --stat` = 2 files / +398（docs/handoff-automation-2026-08-19.md 新增 +232、progress.md +166），全在 Advancer 写入范围（docs/ + progress.md），task_plan.md diff 0 行 ✅ ③预算守卫 3000/300 在位（code-map-generator.py:46/49；exposure-guard.py:45/46 未回归）✅ ④三级信任 + stale 在位（rpd-cold-start.py:213-255 verified/stale/unverified + fingerprint_mismatch）✅ ⑤SCHEMA 2.1.0 + 白名单(2.0.0,2.1.0) 在位（code-map-generator.py:50/62）✅ ⑥计划一致性：I4-0~I4-9 全 complete、L3 planned 冻结，无 pending 模块 ✅ ⑦纯 Markdown 文档，无视觉/UI 改动，不适用截图证据 ✅
- **0-trust 文档事实性核查（文档给了可执行 ID，必须核实）**：Advancer ID `automation-1787109094822` 真实存在且 ACTIVE ✅；valid_until 文档称 2026-08-31 23:59（Asia/Shanghai），元数据 `2026-08-31T15:59:59.999Z` 换算一致 ✅；旧 ID 5867270/5867281 确已不存在 ✅；「未跟踪 10 天」经 `git cat-file -e HEAD~1:...` 复核属实 ✅
- **判定 A 处置**：7 项全过 → Test Results 追加验证行（真实数字）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4 全模块已收官）
- **⚠️ 两项文档精度观察（非 FAIL，不阻断，留档供张敬/接手者判断）**
  1. 交接文档 §八「Verifier 自动化 ID → 已不存在」字面指旧 ID `5867281`，但**未给出当前 Verifier ID `automation-1787109023265`（ACTIVE）**——易被读成"Verifier 自动化整体没了"。轮次机制本身（git log 尾标推导）描述无误，可照常使用
  2. 同节「Q1~Q5 全部落地（R-19~R-29 + Q5 出口 Gate）」中 R-24/26/27/28/29 实为 **parking-lot 冻结项（Charter 明载"维持冻结、按需升级"）**，并非已落地；已落地的是 R-19~R-23 + R-25。文档另有「进度一律以 task_plan.md 为准」的兜底说明，风险已部分缓解
- **📌 D2 状态更正（0-trust 复核上轮 Verifier 结论）**：tick #64 曾记「顺手提交会**永久关闭** D2 免改写压缩选项」。本轮实测 `git ls-remote --heads origin` 仅 `refs/heads/main` → `automation/i4-l2` **纯本地分支**（领先 33 commit / 落后 0），本地历史改写仍可行 → **D2 选项并未永久关闭**，上轮表述偏重。当前 166 行空转日志已随 3bb5666 入仓，压缩需走本地 amend/rebase（可行），不再依赖"未提交"状态
- **本 tick 改动**：仅 progress.md（Test Results +1 行、本条日志 +1 段）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留问题**：D1/D2 仍未拍板（见 docs/automation-governance-proposal.md）；自动化 2026-08-31 23:59 到期后需人工处理

---

## 2026-08-29 23:1x（tick #68 · I4 Advancer · 修复上轮留档的两项文档精度问题）

- **模块**：无待推进（I4-0~I4-9 全 complete；L3 planned 冻结）。闸门：`verify(I4-closeout): 7 项 0-trust 全过，交接文档入仓验证通过 [verifier]` → 本轮属 Advancer；分支 `automation/i4-l2` ✅
- **本 tick 唯一产出**：落实上轮 Verifier 留档的两项精度观察（docs/ 属 Advancer 写入范围）：①§八 Verifier ID 行补上当前有效 ID `automation-1787109023265`（ACTIVE，`FREQ=HOURLY;INTERVAL=1`，经自动化列表实查）②把「Q1~Q5 全部落地（R-19~R-29）」更正为**已落地 R-19~R-23 + R-25**，R-24/R-26~R-29 为 parking-lot 冻结项，并新增「机检证据」小节——`scripts/parking-lot.py --audit` 五条目 `status=frozen`、`LANDED_FALLBACK={R-19~R-23,R-25}`、spec §16.1 R-26~R-29 行原文标注「（P2 parking-lot）冻结登记」，三条一手证据互证；另补「验收行占位 ≠ 能力已实现」的防错注记（升级子命令实为 `--upgrade`，非 `--promote`）
- **改了哪些文件**：docs/handoff-automation-2026-08-19.md（+39 行）、progress.md（仅本条日志）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`，改动后复跑确认；Markdown-only 改动，未触碰 scripts/）
- **遗留问题**：D1/D2 仍未拍板；自动化 2026-08-31 23:59（Asia/Shanghai）到期后需人工处理

---

## 2026-08-30 03:1x（tick #69 · I4 Verifier · 交接文档精度修正 判定 A）

- **闸门**：`git log -1 --format=%s` 尾标含 `[advancer]`（`docs(I4-closeout): 修正交接文档两项事实精度...`，commit `52cd265`）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅
- **⚠️ 0-trust 前置发现**：工作区存在一行**未提交**的 progress.md 改动（Test Results 表 +1 行，自称已完成 52cd265 的验证、判定 A）——上一轮 Verifier tick 写入后未落 commit。**按 0-trust 不采信该行任何声称**，本轮 7 项检查与文档机检证据全部从头实跑；复核后其证据与实测一致，故保留该行并随本 tick 一并入仓（若不一致则本轮改写）
- **7 项 0-trust 逐项实测（本轮真实复跑，非继承）**：
  1. eval 全量 `python scripts/run-eval.py` → **19/19 PASS**（A~X 全过，`🎉 All scenarios passed!`）**exit 0** ✅
  2. diff 审计 `git show HEAD --name-only` / `git diff HEAD~1 HEAD --stat` = **2 files / +39 -3**（docs/handoff-automation-2026-08-19.md +32/-3、progress.md +10），全在 Advancer 写入范围（docs/ + progress.md）；**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）✅
  3. 预算守卫在位：ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300（code-map-generator.py:46/49）+ L3 500（exposure-guard.py:45-47），未回归 ✅
  4. 红线机检在位：三级信任 verified/stale/unverified + fingerprint_mismatch（rpd-cold-start.py:211-255，含 :246 missing 分支）✅
  5. 向后兼容在位：SCHEMA_VERSION="2.1.0" + SCHEMA_WHITELIST=("2.0.0","2.1.0")（code-map-generator.py:50/62）✅
  6. 计划一致性：task_plan.md I4-0~I4-9 **10 个 Phase 全 complete、pending=0**、L3 = planned 冻结，与实际产物一致 ✅
  7. 纯 Markdown 文档改动，无视觉/UI 改动，不适用截图证据 ✅
- **0-trust 文档事实性复验（文档内嵌命令逐条实跑，不采信 Advancer 转述）**：
  1. `scripts/parking-lot.py . --audit` 实跑 exit 0 → count=5，五条目 `status=frozen` 全中；deps/signals 与文档逐字吻合（R-24[R-21 landed] / R-26[R-21 landed] / R-27[R-19 landed] / R-28[missing deps: R-26] / R-29[R-22 landed]，signals 全 0，threshold=3）✅
  2. `LANDED_FALLBACK = {"R-19","R-20","R-21","R-22","R-23","R-25"}`（parking-lot.py:67）与文档一致 ✅
  3. `--upgrade` 缺 `--impact`/`--budget` **实跑 exit 1**（`missing: ["impact","budget"]`），子命令名确为 `--upgrade` 非 `--promote`（parking-lot.py:32/237/310）✅
  4. spec §16.1 :708-711 R-26~R-29 行原文确有「（P2 parking-lot）冻结登记」标注 ✅
  5. Verifier 自动化 ID `automation-1787109023265` 经 automation_update(list) 复验：name「I4-验证（Verifier）：0-trust 独立检验」/ **ACTIVE** / `FREQ=HOURLY;INTERVAL=1`，与文档一致 ✅
  6. `--promise-check` 实跑 exit 0，`scanned=5 / violations=[]` 零违规 ✅
  7. valid_until：文档「2026-08-31 23:59（Asia/Shanghai）」↔ 元数据 `2026-08-31T15:59:59.999Z` 换算一致 ✅
- **上轮留档两项精度问题确已修复**：①§八 Verifier ID 行补上当前有效 ID `automation-1787109023265` ②「Q1~Q5 全部落地」更正为**已落地 R-19~R-23 + R-25**，R-24/R-26~R-29 归位 parking-lot 冻结项，并新增「机检证据」小节 +「验收行占位 ≠ 能力已实现」防错注记 ✅
- **⚠️ 新观察（非 FAIL，仅标签精度，留档不改 docs/）**：新增「机检证据」小节标题写「**2026-08-29 tick #68** 一手复跑校正」，但按本自动化 memory，tick #68（23:1x）实为**跳过轮**（当时 HEAD 为 `[verifier]`）；本 commit 52cd265 落地于 23:17:59，属其后的 Advancer tick。tick 编号标注有偏差，但小节内的机检证据本身全部真实可复现，不影响可执行性
- **📌 D2 状态本轮复核（0-trust，不继承上轮结论）**：`git ls-remote --heads origin` 仅 `refs/heads/main`；`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 35 ahead** → `automation/i4-l2` 仍是**纯本地分支**，本地 amend/rebase 可行 → **D2 压缩选项仍开放**（上轮 tick #67 的"未永久关闭"更正成立）。本 tick 只提交 1 行验证记录，不压缩历史
- **判定 A 处置**：7 项全过 → Test Results 追加验证行（随未提交的上轮记录一并入仓）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4-0~I4-9 全 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留问题**：D1/D2 仍未拍板（见 docs/automation-governance-proposal.md）；自动化 2026-08-31 23:59（Asia/Shanghai）到期，距今不足 2 天，需人工处理

---

## 2026-08-30 05:1x（tick #73 · I4 Advancer · 兑现上轮 Verifier 留档的 tick 编号口径问题）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，交接文档精度修正验证通过 [verifier]`（HEAD `3e13ae3`）→ 本轮属 Advancer；分支 `automation/i4-l2` ✅；起始 worktree **clean**（上轮 Verifier 已入仓，无残留未提交行）
- **模块**：无待推进（task_plan.md I4-0~I4-9 **10 个 Phase 全 complete**、pending=0；L3 planned 冻结）→ 不空转，改为兑现上轮 Verifier 留档的具体缺陷项（docs/ 属 Advancer 写入范围）
- **本 tick 唯一产出**：消除 `docs/handoff-automation-2026-08-19.md` 中**不可外部验证**的 tick 计数引用——§八标题「（Advancer tick #65）」→「（Advancer 轮，commit `3bb5666`）」、「机检证据」小节「（2026-08-29 tick #68 一手复跑校正）」→「（2026-08-29 一手复跑校正；来源 commit `52cd265`）」，并在 §八 开头新增**口径约定**（本文件一律以 commit hash + 日期标注来源，不引用自动化内部 tick 计数；追溯用 `git show --date=iso <hash>`）
- **为什么这么修（而非去争哪个编号对）**：Verifier 观察「tick #68 实为跳过轮」与本自动化 memory 记载冲突——memory L495 明确记 `#68 = Advancer 轮、交付 52cd265`，且 `git show -s --format=%ad 52cd265` = **2026-08-29 23:17:59**，前一条 `b7f91bf`（[verifier]，22:16:51）→ 该轮闸门确为 Verifier 尾标，#68 属 Advancer 成立。但**争编号没有价值**：tick 计数只活在 `.workbuddy/automations/<id>/memory.md`，外部读者无法核对，本身就是不可验证信息源。改为 commit hash 后该类错误从根上消除，Verifier 的方向判断是对的
- **0-trust 一手证据（本轮实跑，不继承）**：`python scripts/parking-lot.py . --audit` exit 0 → `landed=[R-19..R-23,R-25]`、`threshold_user_signal=3`、五条目 `status=frozen`（R-24/R-26 `deps landed: R-21`；R-27 `deps landed: R-19`；R-28 `missing deps: R-26` → `any_ready=false`；R-29 `deps landed: R-22`），`grep LANDED_FALLBACK scripts/parking-lot.py:67` 与文档逐字一致 → **文档中「机检证据」小节内容全部复现，改标题未致失真**
- **改了哪些文件**：docs/handoff-automation-2026-08-19.md（+4/-2）、progress.md（仅本条日志）
- **eval 真实数字**：19/19 PASS，exit 0（`🎉 All scenarios passed!`；改动后复跑两次，`grep -c "✅ PASS"` = 19，第二次 `FINAL_EXIT=0`）；Markdown-only，未触碰 scripts/
- **遗留问题**：D1/D2 仍未拍板（docs/automation-governance-proposal.md）；自动化 2026-08-31 23:59（Asia/Shanghai）到期，剩不足 2 天

---

## 2026-08-30 06:1x（tick #74 · I4 Verifier · 0-trust 验证交接文档去 tick 化）

- **闸门**：`git log -1 --format=%s` = `docs(I4-closeout): 交接文档去除不可外部验证的 tick 计数引用（改用 commit hash + 日期口径约定） [advancer]`（HEAD `2025a08`，08-30 05:14:54）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空，与 Advancer 声称一致，无上轮遗留未提交行）
- **验证对象**：commit 2025a08，diff 范围 `3e13ae3..2025a08`
- **7 项 0-trust 逐项实跑结果**：
  1. **eval 全量** ✅ —— `python scripts/run-eval.py` 真实复跑，19/19 PASS（A~X 全绿）、`🎉 All scenarios passed!`、exit 0
  2. **diff 审计** ✅ —— `git diff HEAD~1 --stat` = 2 files changed / 18 insertions(+) / 3 deletions(-)：`docs/handoff-automation-2026-08-19.md`（+5/-3）+ `progress.md`（+13，仅 Advancer 日志）；逐文件全文审阅确认改动仅限 §八标题、§八 口径约定新增两行、「机检证据」小节标题；**`git diff HEAD~1 -- task_plan.md` 输出为空**（Goal / Key Decisions / Phase 结构零改动）
  3. **预算守卫** ✅ —— code-map-generator.py:46 `ROUTER_TOKEN_LIMIT=3000` / :49 `ENTRY_MAX_TOKENS=300`；exposure-guard.py:45/46 三层 3000/300/500 均在位；本次纯文档改动未触碰脚本
  4. **红线机检** ✅ —— rpd-cold-start.py:213-255 `verified[]/stale[]/unverified[]` 三层结构在位，:253 verified / :246 stale(missing) / :255 stale(fingerprint_mismatch) 判定逻辑无回归
  5. **向后兼容** ✅ —— code-map-generator.py:50 `SCHEMA_VERSION="2.1.0"` + 读者白名单 2.0.0/2.1.0 在位；i4-gate.py:103 回归守卫（SCHEMA_VERSION + SCHEMA_WHITELIST）在位
  6. **计划一致性** ✅ —— task_plan.md 10 个 Phase Status 全 complete + 第 164 行 L3 planned（冻结），`grep -c pending` = 0，与「I4 已收官、无待推进模块」的 Advancer 判断一致；task_plan.md 本轮零改动
  7. **无 mock 注入** ✅ —— diff 文件列表无 png/jpg/html/css/js/tsx，纯 Markdown 文档改动，不涉及视觉/UI
- **0-trust 文档引用真实性复验（不采信 Advancer 转述，逐条实跑）**：
  - `git show -s 3bb5666` = 2026-08-29 21:17:31 `docs(I4-closeout): 交接文档入仓并校正过期自动化信息… [advancer]` → §八标题「（Advancer 轮，commit `3bb5666`）」引用属实
  - `git show -s 52cd265` = 2026-08-29 23:17:59，其父 `b7f91bf` = 22:16:51 `[verifier]` → Advancer 关于轮次归属的推断成立（上轮 Verifier 的「#68 实为跳过轮」观察**不成立**，本轮已用 git 事实自行推翻前轮结论，不继承）
  - `grep -n "tick #\|#6[0-9]\|#7[0-9]"` 全文**零命中** → 去 tick 计数化彻底；仅剩 151/179/186 行三处通用「下个 tick」措辞（非编号，可外部理解，不构成不可验证引用）
  - `python scripts/parking-lot.py . --audit` 实跑 exit 0 → `landed=[R-19..R-23,R-25]`、`threshold_user_signal=3`、五条目 `status=frozen`，R-24/R-26(R-21)/R-27(R-19)/R-28(**missing deps: R-26 → any_ready=false**)/R-29(R-22) 与文档「机检证据」小节逐字吻合 → **改标题未致失真**
  - `grep -n LANDED_FALLBACK scripts/parking-lot.py` = :67 `{"R-19","R-20","R-21","R-22","R-23","R-25"}` 与文档一致
  - automation_update(list) 复验 `automation-1787109023265`（「I4-验证（Verifier）」）仍 ACTIVE / FREQ=HOURLY;INTERVAL=1 → 文档 §八 Verifier ID 行仍准确
- **本轮新观察（非 FAIL，仅留档，不改 docs/）**：Advancer 日志自称「tick #73」，本自动化 memory 无对应外部可核对基准；鉴于本次改动已确立「文档一律用 commit hash + 日期」口径，该编号差异不影响任何外部可读性，不回滚、不追改
- **判定 A 处置**：7 项全过且验收标准（消除不可外部验证的 tick 计数引用）已达成 → Test Results 追加 1 行验证记录（真实数字）；**task_plan.md 未动**（无 pending Phase 需标 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留问题**：D1/D2 仍未拍板（docs/automation-governance-proposal.md）；自动化 2026-08-31 23:59（Asia/Shanghai）到期，剩不足 2 天，需人工处理

---

## 2026-08-30 07:1x（Advancer 轮 · 治理提案补「到期处置预案」§七）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，交接文档去 tick 化验证通过 [verifier]`（HEAD `4d2ee91`）→ 本轮属 Advancer；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空）
- **模块**：无待推进（task_plan.md I4-0~I4-9 **10 个 Phase 全 complete**、pending=0；L3 planned 冻结）→ 不空转，补当前唯一有实操价值的缺口
- **缺口定位**：`docs/automation-governance-proposal.md` 写了 D1/D2 怎么选、写了有效期是哪天，**唯独没写「到期不拍板会发生什么」和「到期不会自动处理哪些事」** —— 距到期仅 40 小时，这是当前最需要落到纸面的信息
- **本 tick 唯一产出**：治理提案新增 §七「到期（valid_until）处置预案」（7.1 到期事实 / 7.2 默认路径对比 / 7.3 四项人工清单 H1~H4 / 7.4 一句话最小行动），§四 决策表下加时效性指引指针
- **0-trust 一手证据（本轮实跑，不继承历史转述）**：
  1. `automation_update(view)` ×2 → Advancer `automation-1787109094822` 与 Verifier `automation-1787109023265` 均 ACTIVE / `FREQ=HOURLY;INTERVAL=1` / **validUntil 同为 `2026-08-31T15:59:59.999Z`** = 2026-08-31 23:59:59.999（Asia/Shanghai）
  2. `date` = 2026-08-30 07:13:28 → 剩余窗口约 **40 小时 46 分钟**（Python 按 ISO 时刻实算，非估算）
  3. `git rev-list --left-right --count origin/main...HEAD` = **0 behind / 38 ahead**；`git ls-remote --heads origin` **仅 `refs/heads/main`** → `automation/i4-l2` 纯本地、远端无副本（H3 风险的事实基础）
  4. `wc -l progress.md` = **692 行**（H2 压缩规模一手值）
  5. `git status --porcelain` 输出为空 → worktree clean（H4 基线）
- **关键结论（已写入文档）**：两自动化共用同一到期时刻 → 同时停、无错配；**不拍板 = 选项 A 自动生效（到期即停），但 status 仍为 `ACTIVE`，若有效期被延长会立即复活恢复每小时空转** → 建议仍显式 PAUSED；到期不会自动处理的 4 件事 = H1 显式停用 / H2 progress 压缩授权 / H3 分支归宿（推荐授权开 PR 并入 main，38 commit 仅存本地风险高）/ H4 无未落盘成果确认
- **改了哪些文件**：docs/automation-governance-proposal.md（新增 §七 + §四 指引行）、progress.md（仅本条日志）
- **eval 真实数字**：19/19 PASS，exit 0（改动前基线 + 改动后复跑，均 `🎉 All scenarios passed!`）；Markdown-only，未触碰 scripts/
- **commit**：`docs(I4-closeout): 治理提案补 §七 到期处置预案（两自动化 validUntil 同一时刻 + 默认路径对比 + H1~H4 人工清单） [advancer]` —— 本日志与该章节同一次提交入仓，**hash 取交棒时 `git log -1 --format=%h`**（定位：`git log --oneline -- docs/automation-governance-proposal.md`）；不写死 hash 值，避免"文件内引用自身 hash"的自引用悖论
- **遗留问题**：D1/D2 仍未拍板；新增 H1~H4 人工清单同待拍板（H3 分支合并需用户授权，agent 禁止自动 merge main / push）

---

## 2026-08-30 08:2x（Verifier 轮 · 治理提案 §七 到期处置预案验证）

- **闸门**：`git log -1 --format=%s` = `docs(I4-closeout): 治理提案补 §七 到期处置预案…[advancer]`（HEAD `f7e0262`）→ 属 Verifier 轮；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空）
- **验证对象**：commit f7e0262 —— 治理提案新增 §七「到期（valid_until）处置预案」（7.1 到期事实 / 7.2 默认路径对比 / 7.3 H1~H4 人工清单 / 7.4 最小行动），§四 加时效性指引指针
- **7 项 0-trust 逐项（全部拿到真实命令输出，无一项推测）**：
  1. eval 全量 ✅ —— `python scripts/run-eval.py` 真实复跑 = **19/19 PASS**（A~X，`🎉 All scenarios passed!`），**EXIT=0**
  2. diff 审计 ✅ —— `git diff HEAD~1 --stat` = 2 files changed / 79 insertions：docs/automation-governance-proposal.md(+59)、progress.md(+20)，全在 Advancer 写入范围（docs/ + progress.md）；**`git diff HEAD~1 -- task_plan.md` 零输出**（Goal / Key Decisions / Phase 结构未被动过）
  3. 预算守卫 ✅ —— ROUTER_TOKEN_LIMIT=3000（code-map-generator.py:46）、ENTRY_MAX_TOKENS=300（:49）、exposure-guard.py L1 3000 / L2 300 / L3 500（:45-47）、DEEP_FOLLOWUP_TURNS=2（:50）
  4. 红线机检 ✅ —— rpd-cold-start.py:213-255 `verified[] / stale[] / unverified[]`，stale 双触发（:246 missing、:255 fingerprint_mismatch）在位无回归
  5. 向后兼容 ✅ —— SCHEMA_VERSION="2.1.0" + SCHEMA_WHITELIST=("2.0.0","2.1.0")（code-map-generator.py:50/62），且被 i4-gate.py:101-105 回归守卫实际消费（不是死常量）
  6. 计划一致性 ✅ —— task_plan.md I4-0~I4-9 10 个 Phase 全 complete、pending=0、L3 planned 冻结；diff 0 行 → 状态与产物一致
  7. 无 mock 注入 ✅ —— 纯 Markdown 文档，无视觉/UI 改动，不适用截图要求
- **文档事实性延伸复验（沿用前几轮对文档类 commit 的 0-trust 重心：文档给出的每个 ID / 命令 / 数字是否真实可执行）**：
  - **核心声称证实**：「两自动化 validUntil 同一时刻」→ `automation_update(mode="view")` 双查，Advancer `automation-1787109094822` 与 Verifier `automation-1787109023265` 的 validUntil **均为 `2026-08-31T15:59:59.999Z`**、validFrom 均 `2026-08-18T16:00:00.000Z`、rrule 均 `FREQ=HOURLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR,SA,SU`、status 均 ACTIVE，name 与文档表逐字吻合 → 文档推论的「同时停、无错配」结论成立
  - 折算本地 2026-08-31 23:59:59.999（UTC+8）✅；「剩余窗口约 40 小时 46 分钟」自 07:13:28 起算复核 ✅
  - H1「均 ACTIVE」✅；H3 `git ls-remote --heads origin` 实跑**仅 `refs/heads/main`** → 「分支纯本地、远端无副本」成立 ✅；H4 `git status --porcelain` 本轮起始为空 ✅
  - 文档自述追溯方法 `git log --oneline -- docs/automation-governance-proposal.md` 实跑可用（返回 f7e0262 / 562c14b 两条）✅ —— 刻意不引自身 hash、规避自引用悖论的做法有效
  - §七 `grep -c "tick #"` = **0** → 与「不引用自动化内部 tick 计数」口径声明自洽 ✅
- **⚠️ 本轮新观察（非 FAIL，仅留档，Verifier 禁改 docs/）**：H2「progress.md 692 行」与 H3「0 behind / 38 ahead」两个「当前一手值」，实跑现值为 **712 行 / 0 behind 39 ahead**。两条差值均可被本次 commit 自身完全解释（+20 行日志、+1 个 commit），**数值本身真实无造假**，成因是「文档与自身 commit 同批入仓」的自引用漂移——写入时测得的是入仓前状态。读者按文档现跑会得到 712 / 39。属标签精度问题（同类于 tick 编号偏差），不构成回滚理由
- **判定 A 处置**：7 项全过且 §七 验收目标（到期事实准确、默认路径可判、人工清单可执行）已达成 → Test Results 追加 1 行验证记录（真实数字，含上述复验证据）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4-0~I4-9 全 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留**：D1（A 停用 / B 降频周观察 / C 按需触发 / 维持现状）+ D2（progress 压缩授权）+ 新增 H1~H4 全部待张敬拍板；**到期窗口剩约 39 小时**（自 2026-08-30 08:22 起算）

---

## 2026-08-30 09:1x（Advancer 轮 · 治理提案数字口径整改：§三 重写 + §7.3 自引用漂移）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，治理提案 §七 到期处置预案验证通过 [verifier]`（HEAD `3099912`，08-24-28）→ 本轮属 Advancer；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空）
- **模块**：无待推进（task_plan.md I4-0~I4-9 **10 个 Phase 全 complete**、pending=0；L3 planned 冻结）→ 不空转，兑现上轮 Verifier 留档的「H2/H3 数字自引用漂移」观察
- **根因（实测推翻初稿，非标签精度问题）**：顺着 Verifier 的漂移线索追查，发现 `docs/automation-governance-proposal.md` §三 的量级描述**本身是错的**——
  - `539 = 417（已入库，`git show 5aebe97:progress.md | wc -l`）+ 122（当时未提交的 #51~#61 空转段）` → 行数对得上 ✅
  - 但「tick #17~#62 共 **46 条**空转日志约 **300+ 行**占 **~60%**」**对不上**：progress.md 里实际只有 **11 条 / 122 行 / 占 23%**。46 是 `.workbuddy/automations/<id>/memory.md` 的 tick 计数，其日志自 §五 起**根本不进 progress.md** → **混淆两个计数源，高估约 2.5 倍**
  - 后果：D2（压缩授权）的收益预期被虚高（宣称 539→250，实测 738→约 605）→ 直接影响张敬的待拍板决策，必须改
- **本 tick 产出**：§三 全量重写为可复现口径（3.1 根因对照表 / 3.2 当前实测 + 复现命令 / 3.3 修订后压缩方案，明确**保留** #62 治理提案、#65 交接文档入仓、全部 Verifier 日志）；§7.3 H2/H3 硬编码数字 → 「实测时刻 + 复现命令」，新增自引用漂移说明（判断依据不依赖精确值：H2 看是否持续增长、H3 看 ahead>0 且远端无副本）；H3 去向「38 个提交」→ ahead 计数口径
- **0-trust 一手证据（本轮实跑，文档内每条复现命令均验证可用）**：`wc -l progress.md` = **738**；`sed -n '442,603p' progress.md | wc -l` = **162**（#51~#65）；`sed -n '442,563p;576,592p' progress.md | wc -l` = **139**（纯空转 #51~#61=122 / #63=9 / #64=8）；`git show 5aebe97:progress.md | wc -l` = **417**；`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 40 ahead**；`git ls-remote --heads origin` 仅 `refs/heads/main`
- **改了哪些文件**：docs/automation-governance-proposal.md（+34/-12）、progress.md（仅本条日志）
- **eval 真实数字**：19/19 PASS，exit 0（改动前基线 + 改动后复跑，均 `🎉 All scenarios passed!`）；Markdown-only，未触碰 scripts/
- **遗留问题**：D1/D2 + H1~H4 仍待拍板；**§一/§五/§六 仍引用自动化 tick 计数（如「47 次零产出」）——本轮未动**：该计数源确为 automation memory（本轮已证明 progress.md 与 tick 计数是两个源），属历史记录且不影响可执行性，留待后续评估是否统一到 commit hash 口径

---

## 2026-08-30 10:2x（I4 Verifier · 0-trust 验证治理提案数字口径整改）

- **闸门**：`git log -1 --format=%s` = `docs(I4-closeout): 治理提案数字口径整改（§三 量级描述实测重写…） [advancer]`（HEAD `0604e81`，08-30 09:23:17）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空，与 Advancer 声称一致，无上轮遗留未提交行）
- **验证对象**：commit `0604e81`，diff 范围 `3099912..0604e81`
- **7 项 0-trust 逐项实跑结果**：
  1. **eval 全量** ✅ —— `python scripts/run-eval.py` 真实复跑，19/19 PASS（A~X 全绿）、`🎉 All scenarios passed!`、exit 0
  2. **diff 审计** ✅ —— `git diff HEAD~1 --stat` = 2 files changed / 50 insertions(+) / 12 deletions(-)：`docs/automation-governance-proposal.md`（+34/-12）+ `progress.md`（+16，仅 Advancer 日志段）；逐行全文审阅确认改动仅限 §三（3.1/3.2/3.3 全量重写）与 §7.3（H2/H3 + 漂移说明 + H3 去向下句）；**`git diff HEAD~1 --name-only \| grep -c task_plan.md` = 0**（Goal / Key Decisions / Phase 结构零改动）
  3. **预算守卫** ✅ —— code-map-generator.py:46 `ROUTER_TOKEN_LIMIT=3000` / :49 `ENTRY_MAX_TOKENS=300`；exposure-guard.py:45-49 三层 3000/300/500 + 双预算 `TASK_ENTRY_BUDGET=24`/`TASK_TOKEN_BUDGET=2000` + `DEEP_FOLLOWUP_TURNS=2` 均在位；本次纯文档改动未触碰脚本
  4. **红线机检** ✅ —— rpd-cold-start.py:213-255 `verified[]/stale[]/unverified[]` 三层结构在位，:253 verified / :246 stale(missing) / :255 stale(fingerprint_mismatch) 判定逻辑无回归
  5. **向后兼容** ✅ —— code-map-generator.py:50 `SCHEMA_VERSION="2.1.0"` + :62 `SCHEMA_WHITELIST=("2.0.0","2.1.0")` 在位；i4-gate.py:101-105 回归守卫实际消费（非死常量）
  6. **计划一致性** ✅ —— task_plan.md I4-0~I4-9 十个 Phase Status 全 complete、pending=0、L3 planned 冻结；本轮 diff 0 行 → 状态与产物一致
  7. **无 mock 注入** ✅ —— diff 文件列表仅有 .md，纯 Markdown 文档，无视觉/UI 改动
- **0-trust 数字独立复算（本轮最大风险点是「文档声称的数字是否可复现」，故逐条重跑，不采信 Advancer 转述）**：
  - `git show 5aebe97:progress.md | wc -l` = **417** ✅（`git log -1 5aebe97` = I4 收官报告 verify commit，hash 真实存在）
  - `sed -n '442,603p' progress.md | wc -l` = **162** ✅（#51~#65 共 15 段）
  - `sed -n '442,563p;576,592p' progress.md | wc -l` = **139** ✅（#51~#61=122 / #63=9 / #64=8）
  - `git rev-list --left-right --count origin/main...HEAD` = **0 behind / 41 ahead**（文档记 40，+1 恰为本 commit 自身 → 漂移可被完全解释）
  - `git ls-remote --heads origin` 实跑**仅 `refs/heads/main`** ✅ → 「分支纯本地、远端无副本」结论成立
  - **关键断言验证**：`grep -nE '^## .*#'` 列全部 tick 标题 → **#51~#61 恰为 11 段（行 442–563）**，而「46 条」对应 `.workbuddy/automations/automation-1787109094822/memory.md` 的 tick 计数（该序列现已编至 **#77**）→ 文档「混淆两个计数源、高估约 2.5 倍」的根因判定**属实**
  - **算术自洽复核**：417+122=539 ✅ · 122/539=22.6%≈「~23%」✅ · 162/738=21.95%≈「22%」✅ · 139/738=18.83%≈「18.8%」✅ · #62(12行)+#65(11行)=23 ✅ · 738−139+6≈605 ✅
  - **结论**：§三 全部数字可复现且算术自洽，初稿虚高的 D2 收益预期（539→250）已下修为实测口径（738→约 605），**决策输入不再失真**
- **⚠️ 本轮新观察（非 FAIL，仅留档，Verifier 禁改 docs/）**：
  1. §三 3.2 的「当前实测」值随本轮日志继续漂移（文档记 738，现值 **754**，+16 = 本 commit 的 progress.md 日志段），与 §7.3 新增的漂移说明属同一成因；3.2 已带实测时刻 + 复现命令，读者自跑可得当前值，不构成误导
  2. §一「连续 47 次零产出」仍为 tick 计数口径（现序列已至 #77，该值已偏低约 14 次）。Advancer 已在上一日志明确声明本轮未动、属历史记录；其**不影响 D1 结论**（D1 的承载事实是「可推进模块 = 0」，已由 task_plan.md 十个 Phase 全 complete 独立证实）。留待后续是否统一到 commit hash 口径
- **判定 A 处置**：7 项全过且本轮声明范围内（§三 量级描述重写 + §7.3 硬编码数字改实测时刻+复现命令）已全部达成 → Test Results 追加 1 行验证记录（真实数字 + 复算证据）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4-0~I4-9 全 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留**：D1（A 停用 / B 降频周观察 / C 按需触发 / 维持现状）+ D2（progress 压缩授权，需授权）+ H1~H4 全部待张敬拍板；**自动化 2026-08-31 23:59（Asia/Shanghai）到期，剩约 37.5 小时**

---

## 2026-08-30 12:1x（I4 Advancer · 治理提案加「§零 口径公约」，一次性终结数字漂移与 tick 计数两类缺陷）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，治理提案数字口径整改验证通过 [verifier]`（HEAD `1edb4b2`，08-30 10:26:39）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 空）
- **模块**：无待推进（I4-0~I4-9 十个 Phase 全 complete，pending=0；L3 planned 冻结）→ 不空转，兑现上轮 Verifier 留档的两项观察（Verifier 禁改 docs/，属 Advancer 写入范围）
- **做了什么**：`docs/automation-governance-proposal.md` 新增 **§零 口径公约**（R-1 当前值=快照 / R-2 来源=commit hash+日期 / R-3 修订触发条件 + 历史遗留 tick 标注读法）→ **不再逐条改数字，改为一次性约定，终结「改一次漂一次」的循环**；§一 两行整改（废弃「47 次零产出」tick 口径，换成仓库内可核对的 commit 口径；「tick #15」→ commit hash）；§三 3.2 更新实测时刻与总行数并补「行号范围不漂、总行数会漂」的稳定性说明；3.3 预期效果改为公式表达
- **🔑 本轮最有价值的发现（超出 Verifier 观察范围）**：比「47 次零产出」强得多的可核对事实是——自 I4 收官 commit `27f7fd5`（2026-08-21）起 **13 个提交全部为 docs/progress 类，`scripts/` 改动 0 条**；`git diff --name-only 27f7fd5..HEAD | sort -u` 仅 3 个文件（`docs/automation-governance-proposal.md` / `docs/handoff-automation-2026-08-19.md` / `progress.md`）。这是**任何人一条命令即可验证**的零产出证据，而 tick 计数只在自动化运行日志里、仓库外无法核对
- **0-trust 一手证据（均实跑，时刻 2026-08-30 12:13:22）**：`wc -l progress.md` = **785**；`sed -n '442,603p' progress.md | wc -l` = **162**（与 09:16 测量**完全一致**）；`sed -n '442,563p;576,592p' progress.md | wc -l` = **139**（同样一致）→ 证实「空转段在中段、新日志追加到尾部，故待压缩量稳定、只有总行数漂移」；`git log --oneline 27f7fd5..HEAD | wc -l` = **13**；`git log --oneline 27f7fd5..HEAD -- scripts/ | wc -l` = **0**；`git diff --stat 27f7fd5..HEAD -- scripts/ | wc -l` = **0**；`git rev-list --left-right --count origin/main...HEAD` = 0 behind / **42** ahead；`git log -1 --format=%ad --date=iso 562c14b` = 2026-08-29 16:15:37（与文档「固化 16:1x」吻合）；`git log -1 --format=%ad --date=iso 27f7fd5` = 2026-08-21 14:13:45
- **eval 真实数字**：19/19 PASS，exit 0（改动后实跑，`🎉 All scenarios passed!`）；Markdown-only，未触碰 scripts/
- **改了哪些文件**：docs/automation-governance-proposal.md（+约 45/-8）、progress.md（仅本条日志）
- **遗留问题**：D1/D2 + H1~H4 仍待张敬拍板；§三 3.1 的 `tick #17~#62`/`46 条` 按 R-2 **刻意保留**（是「计数源混淆」错误的当事数值，抹掉等于销毁整改证据）；自动化 2026-08-31 23:59（Asia/Shanghai）到期，剩约 35.8 小时
- **方法沉淀**：文档缺陷若反复以同一形态出现（本例连续两轮「数字漂移」），正确做法不是再修一次数字，而是**写一条公约让该类缺陷不再产生**——§零 R-3 明确「不因数值变旧而更新」，从规则层面关闭了逐 tick 追更这条成本通道

---

## 2026-08-30 13:1x（I4 Verifier · §零 口径公约 判定 A）

- **闸门**：`git log -1 --format=%s` = `docs(I4-closeout): 治理提案加 §零 口径公约… [advancer]`（HEAD `d5a0628`）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；**起始 worktree clean**（`git status --porcelain` 输出 0 行）
- **验证对象**：`docs/automation-governance-proposal.md` §零 口径公约（R-1/R-2/R-3 + 历史遗留 tick 标注读法）+ §一 废弃 tick 计数口径改 commit 口径 + §三 3.2 实测刷新与 3.3 公式化
- **7 项 0-trust 逐项（全部实跑，无一项推测）**：
  1. **eval 全量 PASS** —— `python scripts/run-eval.py` = **19/19 PASS**（A~X 全过，`🎉 All scenarios passed!`），**EXIT=0**
  2. **diff 审计 PASS** —— `git diff HEAD~1 --stat` = 2 files changed / 48 insertions / 9 deletions：docs/automation-governance-proposal.md（+34/-9）+ progress.md（+14/-0）；**task_plan.md diff 0 行**，Goal / Key Decisions / Phase 结构均未被动
  3. **预算守卫 PASS** —— ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300（code-map-generator.py:46/49）+ 三层 3000/300/500 与双预算 TASK_ENTRY_BUDGET=24 / TASK_TOKEN_BUDGET=2000（exposure-guard.py:46-49）
  4. **红线机检 PASS** —— 三级信任 verified/stale/unverified 在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）；**补跑 `python scripts/i4-gate.py . --json` → exit 0、`"pass": true`，regression_guard 三项 findings 全 `ok:true`**
  5. **向后兼容 PASS** —— SCHEMA_VERSION=2.1.0 + SCHEMA_WHITELIST=(2.0.0,2.1.0)（code-map-generator.py:50/62），且被 i4-gate.py:101-105 回归守卫消费
  6. **计划一致性 PASS** —— task_plan.md 十个 Phase（I4-0~I4-9）Status 全 `complete`、pending=0，L3 planned 冻结；本轮改动仅 docs/progress，与状态一致
  7. **无 mock 注入 PASS** —— 纯 Markdown 文档改动，零视觉/UI 改动，无需截图证据
- **0-trust 数字独立复算（不采信 Advancer 任何一手声称，其文档内每条复现命令全部重跑）**：`wc -l progress.md` = **799**（Advancer 记 785 → +14 恰为本 commit 自身的 Advancer 日志，§零 R-1「当前值=写入时刻快照」声明**成立且非造假**）；`sed -n '442,603p' \| wc -l` = **162** ✅ 与 09:16 测量完全一致；`sed -n '442,563p;576,592p' \| wc -l` = **139** ✅ 同样一致 → **「待压缩量稳定、只有总行数漂」这一 D2 收益判断的前提被独立证实**；`git log --oneline 27f7fd5..HEAD \| wc -l` = **14**（记 13，+1 自身）；**核心断言 `git log --oneline 27f7fd5..HEAD -- scripts/ \| wc -l` = 0 在 14 commits 下依然为真**；`git diff --name-only 27f7fd5..HEAD \| sort -u` = 3 文件，与文档逐字吻合；`git log -1 --format=%ad --date=iso 562c14b` = 2026-08-29 16:15:37 ✅、同命令 `27f7fd5` = 2026-08-21 14:13:45 ✅；`git rev-list --left-right --count origin/main...HEAD` = 0 behind / **43** ahead（记 42，+1 自身）；算术复核 162/785≈20.6%（文档「~21%」）✅、139/785≈17.7% ✅、785−139+6=**652** ✅
- **判定 A 处置**：7 项全过且本轮声明范围（§零 公约 + §一 去 tick 口径 + §三 3.2/3.3）已**全部达成** → Test Results 追加 1 行验证记录（真实数字 + 复算证据）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4-0~I4-9 全 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **留档观察（非 FAIL，Verifier 禁改 docs/）**：①§一「13 个提交」与 §三 3.2「785 行」现读分别为 14 / 799 —— **这正是 §零 R-1 所描述并已声明接受的自引用漂移**，公约生效后按 R-3 不再追更，属预期内、不建议再改 ②§三 3.1 的 `tick #17~#62`/`46 条` 按 R-2 刻意保留作为整改证据，与 §一 已废弃 tick 口径并存，读者需借 §零 的「历史遗留标注读法」一节理解，略增阅读成本但换取了证据完整性
- **遗留**：D1/D2 + H1~H4 仍待张敬拍板；自动化 2026-08-31 23:59:59（Asia/Shanghai）到期，**剩约 34.7 小时**

---

## 2026-08-30 14:1x（I4 Advancer · H3 合并前风险审计：44 commits 收敛为 4 文件 / 14 处删改）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，治理提案 §零 口径公约验证通过 [verifier]`（HEAD `089c8ce`）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 输出 0 行）
- **模块**：无待推进（I4-0~I4-9 十个 Phase 全 complete，pending=0；L3 planned 冻结）→ 不空转，补 H3 缺失的一环
- **为什么做这个**：H3 的推荐去向是「开 PR 合并进 main」，但此前**从未有人量化过合并面**——「44 ahead」听起来风险高，可能正是它迟迟未拍板的原因之一。§七 只讲了「要不要合并」，没讲「合并会动到什么」
- **做了什么**：`docs/automation-governance-proposal.md` 新增 **§八 H3 合并前风险审计**（8.1 合并面实测 / 8.2 14 处删改逐条核实 / 8.3 执行顺序建议 / 8.4 拍板后可复制命令）
- **三条审计结论（均可一条命令复验）**：
  1. **合并面近似为零** —— 21 个涉及文件中 **17 个是纯新增**（`progress.md`/`task_plan.md`/`findings.md`/6 个 I4 脚本/3 篇新文档在 main 上**根本不存在**，`git show origin/main:progress.md` 直接报 does not exist，numstat deletions 列全 0）→ 不可能冲突
  2. **真正需人工审视的只有 4 文件 / 14 处删改** —— 判定依据 `git diff --numstat origin/main...HEAD | awk '$2>0'` 恰输出 4 行：SKILL.md(10) / rpd-v2-technical-spec.md(2) / code-map-generator.py(1) / rpd-cold-start.py(1)。**逐条实跑核实：无一处功能丢失**——code-map 的 `SCHEMA_VERSION 2.0.0` 删除是 R-10 升级，白名单 `("2.0.0","2.1.0")` 在位（:62）；cold-start 的 Step 4 仍在（:421，标题随 R-23 扩展）；SKILL.md 旧表 10 行全部有对应新条目并新增 I4 三脚本；spec 两行为文档演进
  3. **唯一需正眼看的**是 code-map schema 升级（红线 7，唯一可能影响 main 既有产物的改动）→ 白名单在位且被 `i4-gate.py:101-105` 实际消费，**向后兼容成立**
- **🔑 本轮新发现（影响决策顺序，非文档精度问题）**：**必须先 D2 压缩、后 H3 合并**。因为 `progress.md` 在 main 上不存在 → 它是随本次合并**首次进入 main**；若先合并，139 行纯空转日志**一次性永久写入 main 提交历史**，之后再压缩也只多一个删除提交、历史痕迹不可消除；先压缩则 main 从一开始就只看到 681 行（820−139）。**这是 D2/H3 存在先后依赖的第一个硬理由**（此前文档中两者是并列的独立决策点）
- **0-trust 一手证据（14:14 Asia/Shanghai 实跑，文档内每条复现命令均已验证可用）**：`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 44 ahead**；`git log --oneline origin/main..HEAD | wc -l` = **44**；`git diff --name-only origin/main...HEAD | sort -u | wc -l` = **21**；`awk '$2>0'` = 4 行（与文档表逐字一致）；`git ls-files scripts/ | grep -c "\.pyc$"` = **0**；`wc -l progress.md` = **820**；`sed -n '442,563p;576,592p' | wc -l` = **139**（与 09:16 测量**第三次一致**，稳定量判断再获证实）；820−139=**681**；`git show origin/main:progress.md` = `fatal: path 'progress.md' ... not in 'origin/main'`；`automation_update(mode="view")` 两个 ID（…9094822 / …9023265）**均为 ACTIVE、validUntil 2026-08-31T15:59:59.999Z**，与 §7.1 表逐字吻合（未做任何修改性调用）
- **顺带证伪一个我自己的怀疑**：起初按红线怀疑 `.workbuddy/` 混入 main，实查 `.gitignore` 第 20-22 行有显式例外 `!.workbuddy/automation-rules.md`（注释：「自动化任务依赖的规则文件，需保留在版本库」）→ **有意保留，非污染**；`promo/` 与 `*.pyc` 均已被忽略
- **eval 真实数字**：19/19 PASS，exit 0（改动后实跑，`🎉 All scenarios passed!`，A~X 全绿）；Markdown-only，未触碰 scripts/
- **改了哪些文件**：docs/automation-governance-proposal.md（+约 62）、progress.md（仅本条日志）
- **遗留**：D1/D2 + H1~H4 待拍板；**D2 与 H3 现存在先后依赖（见上）**，拍板时请连顺序一起给；自动化 2026-08-31 23:59:59（Asia/Shanghai）到期，剩约 **34 小时**

---

## 2026-08-30 15:1x（I4 Verifier · §八 H3 合并前风险审计 0-trust 验证）

- **闸门**：`git log -1 --format=%s` = `docs(I4-closeout): 治理提案新增 §八 H3 合并前风险审计 …[advancer]`（HEAD `51b2e81`）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 输出 0 行）
- **验证对象**：`docs/automation-governance-proposal.md` 新增 §八（8.1 合并面实测 / 8.2 14 处删改逐条核实 / 8.3 D2 先于 H3 / 8.4 可复制命令）
- **7 项 0-trust 检查结果**：
  1. **eval 全量 PASS** —— 真实复跑 `python scripts/run-eval.py` → **19/19 PASS，REAL_EXIT=0**（A~X 全过，`🎉 All scenarios passed!`；用 `> /tmp/eval.out` 重定向取真实退出码，非管道退出码）
  2. **diff 审计 PASS** —— `git diff HEAD~1 --stat` = 2 files changed / 81 insertions / 0 deletions（governance-proposal.md +62、progress.md +19）；**task_plan.md diff 0 行**，Goal / Key Decisions / Phase 结构未被触碰
  3. **预算守卫 PASS** —— ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300（code-map-generator.py:46/49）；三层 3000/300/500 + 双预算 24 条/2000t（exposure-guard.py:45-49）；i4-gate.py:38/39 同值且在位
  4. **红线机检 PASS** —— verified/stale/unverified + fingerprint 比对在位（rpd-cold-start.py:213-255，:246 missing / :255 fingerprint_mismatch）；另补跑 `i4-gate.py . --json` → **exit 0 / `"pass": true` / regression_guard 三项全 ok**
  5. **向后兼容 PASS** —— SCHEMA_VERSION 2.1.0 + SCHEMA_WHITELIST ("2.0.0","2.1.0") 在位（code-map-generator.py:50/62），被 i4-gate.py:101-105 实际消费；tree-sitter → 正则降级路径在位（:241/:358/:373）
  6. **计划一致性 PASS** —— task_plan.md 十个 Phase（I4-0~I4-9）Status 全 complete、pending=0，与实际产物一致
  7. **无 mock 注入 PASS** —— 纯 Markdown 文档改动，零视觉/UI 改动，无需截图证据
- **0-trust 数字独立复算（不采信 Advancer 任何一手声称，文档内每条复现命令全部重跑）**：`git rev-list --left-right --count origin/main...HEAD` = **0 / 45**（记 44，+1 自身）；`git log --oneline origin/main..HEAD \| wc -l` = **45**；`git diff --name-only origin/main...HEAD \| sort -u \| wc -l` = **21** ✅；`git ls-remote --heads origin` 仅 `refs/heads/main` ✅；`git status --porcelain \| wc -l` = **0** ✅；**8.2 核心断言 `git diff --numstat origin/main...HEAD \| awk '$2>0'` 恰 4 行**（SKILL.md 10 / spec 2 / code-map-generator 1 / rpd-cold-start 1 = **14 处删改**）✅；`git show origin/main:progress.md` 报 `not in 'origin/main'` ✅（8.1 与 8.3 两个论证的前提同时被证实）；`grep SCHEMA_WHITELIST` = :62 ✅；`grep "Step 4"` = :421 ✅；`sed -n '94,110p' SKILL.md` = 新表 15 行含旧 10 脚本全部条目 ✅；`git ls-files scripts/ \| grep -c "\.pyc$"` = **0** ✅；`git ls-files .workbuddy/` 仅 automation-rules.md ✅；**待压缩量三测一致**：122 / 139 / 162（与 09:16、12:13 第四次吻合）✅；`wc -l progress.md` = **839**（记 820，+19 自身日志）；`automation_update(mode="list")` 复验 §8.4 两个 ID 真实存在且 ACTIVE；算术 122+17=139 ✅、820−139=681 ✅
- **判定 A 处置**：7 项全过且本轮声明范围（8.1~8.4）已**全部达成** → Test Results 追加 1 行验证记录（真实数字 + 复算证据）；**task_plan.md 未动**（无 pending Phase 需标 complete，I4-0~I4-9 全 complete）；未回滚、未改任何代码文件
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **留档观察（非 FAIL，Verifier 禁改 docs/）**：①§八 8.2 结论三称「`.gitignore` 第 20-22 行有显式例外」，实查该文件**共 19 行**，例外实际在**第 16-18 行**（`.workbuddy/*` → 注释 → `!.workbuddy/automation-rules.md`）→ **行号引用偏差 4 行，但实质结论成立**（`git ls-files .workbuddy/` 确仅 1 文件、promo/ 与 *.pyc 确被忽略）。与 §零 R-1 已声明接受的自引用漂移同属文档精度级问题，非造假，建议下次触碰该节时顺手修正 ②§三 3.2 把 tick #63 / #64 归类为「纯空转」并纳入压缩区间 576-592，但这两段实际上记录了真实交付（#63 治理提案更新+commit、#64 引用 verifier commit 378b2f2）；§三 3.3 已明示「保留 #62 / #65」，两者口径自洽，但 D2 执行前建议再确认这两段是否值得保留 ③§8.1「44 ahead / 820 行」现读 45 / 839，同属 R-1 覆盖的自引用漂移
- **遗留**：D1/D2 + H1~H4 仍待张敬拍板；**D2 须先于 H3**（否则 139 行空转日志永久写入 main 历史）；自动化 2026-08-31 23:59:59（Asia/Shanghai）到期，**剩约 32.8 小时**

---

## 2026-08-30 16:1x（I4 Advancer · 交付完整性审计：27 个未勾 checkbox 三重对账，排除「假 complete」，发现 R-05 临界）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，治理提案 §八 H3 合并前风险审计验证通过 [verifier]`（HEAD `709a6fe`）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**
- **模块**：无待推进（I4-0~I4-9 全 complete、pending=0；L3 planned 冻结）→ 不空转，补一个**此前无人查过的审计面**
- **为什么做这个**：`.workbuddy/automation-rules.md` 的 0-trust 第 6 项「计划一致性」只核对 `Status:` 字段，从未核对 Phase 下的**逐条 checkbox**。实测 **27 个 checkbox 未勾**，而其所属 Phase 全部标 `complete`。这两种情况对 H3（合并进 main）含义完全相反 —— 要么「清单滞后」（安全），要么「假 complete」（把缺口带进 main），必须分清
- **做了什么**：新建 `docs/i4-delivery-completeness-audit.md`（5 节），对 27 项做**三重对账**（代码符号 `file:line` / eval 断言行 / spec 章节），不采信 Status 与任何自述
- **结论**：**22 项已实现（清单滞后）+ 1 项临界 + 4 项流程纪律，无一项「未实现」** → **I4 的 complete 不是假的，是清单没跟上实现**；§八 的合并面结论（17 纯新增 / 4 文件 14 处删改）不受影响
- **🔑 本轮最有价值发现（F1，差点误报）**：工作区 `wc -c SKILL.md` = **8235 B > 8192**，初判「违反 R-05 硬约束」。深挖是**行尾口径**问题 —— `core.autocrlf=true` 且无 `.gitattributes`，检出时 119 行各加 1 个 CR（8116+119=8235；`grep -c $'\r'` = 119 = `wc -l` = 119 完全对得上）。**Git 对象内仍是 LF 的 8116 B，R-05 并未违反，但余量只剩 76 字节（0.93%）** ≈ 2~3 行中文。引入点 `4c40084`（2026-08-21）自称「SKILL 工具箱 18 行 ≤8KB」，按 LF 口径**成立、非造假**。而 `grep -c "SKILL" scripts/i4-gate.py` = **0** → **没有任何机检会拦住下一次「顺手加一行」**
- **⚠️ 加守卫有陷阱（顺序依赖）**：若给 `i4-gate.py` 加体积守卫，**必须用 LF 口径 `git show HEAD:SKILL.md | wc -c`，不能用 `wc -c SKILL.md`** —— 后者在 Windows 上恒定 8235，会直接让 eval FAIL，反过来卡死红线 3「19/19 才 commit」
- **另两项发现**：F2 task_plan 称「12 个 scripts」，实测 **18**（I4 新增 6 个），接手 agent 按 12 盘点会漏掉全部 I4 主力脚本；F3 I4-8①「每 fix 独立 type/scope 分支」与实际不符 —— I4 的 45 个提交全在 `automation/i4-l2` 单分支（自动化串行节奏的既定约定），须加注例外
- **0-trust 一手证据（16:15 Asia/Shanghai 实跑）**：`grep -c '^\- \*\*Status:\*\* complete' task_plan.md` = **10**；未勾 checkbox = **27**（4+3+2+4+3+3+4+4）；`git show HEAD:SKILL.md | wc -c` = **8116**；`wc -c SKILL.md` = **8235**；`grep -c $'\r' SKILL.md` = **119**；`wc -l SKILL.md` = **119**；`wc -m SKILL.md` = 5341；`ls scripts/*.py | wc -l` = **18**；`grep -c "SKILL" scripts/i4-gate.py` = **0**；`git log -1 --format=%ad --date=iso 4c40084` = 2026-08-21 12:24:36 +0800；`.project-state.md` 4659 B（08-21 12:23）；spec §16.1 R-19~R-25 在 `:701–711`
- **自查（诚实记录）**：文档初稿把 8 个分组的和误算成 23（实为 27），复核复现命令时自曝并已修正为 27 —— 修正后总数自洽（22+1+4=27）
- **eval 真实数字**：19/19 PASS，**EXIT=0**（`python scripts/run-eval.py > /tmp/eval_i4_audit.out` 取真实退出码，非管道退出码；`grep -c "✅ PASS"` = 19，`🎉 All scenarios passed!`）。新增文档为纯 Markdown，未触碰 `scripts/`
- **改了哪些文件**：`docs/i4-delivery-completeness-audit.md`（新建）、`progress.md`（仅本条日志）
- **遗留**：① 22 项勾选权在 Verifier（Advancer 禁改 `task_plan.md`）② I4-9② 暂不勾 —— R-05 临界，建议「先压缩腾出 ≥200 B，再加 LF 口径守卫」，需张敬授权 ③ D1/D2 + H1~H4 待拍板，**D2 须先于 H3** ④ 上轮 Verifier 留档的 §三 3.2 误删区间问题（#63/#64 实为真实交付 17 行，若按 §8.4 命令执行会误删）本轮未处理，建议下轮 Advancer 优先修
- **方法沉淀**：「Status complete」是**结论字段**，「checkbox」是**证据字段**。只看结论字段的审计会漏掉「结论与证据不一致」这类问题（本轮 27 项）。审计应查证据，不查结论

---

## 2026-08-30 17:1x（I4 Verifier · 交付完整性审计 判定 A：7 项 0-trust 全过；F1 R-05 临界经字节级复核属实；22 项勾选权冲突 → 升级张敬）

- **闸门**：`git log -1 --format=%s` 含 `[advancer]`（HEAD `3163c73`，2026-08-30 16:21:08 +0800）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 0 行）
- **验证对象**：commit `3163c73` = 新建 `docs/i4-delivery-completeness-audit.md`（+165）+ progress.md（+19）；**Advancer 本轮未改任何代码，只做审计**
- **7 项 0-trust 逐项（全部实跑，无一项推测）**：
  1. **eval 全量 PASS** —— `python scripts/run-eval.py` 重定向取真实退出码 **REAL_EXIT=0**，PASS 计数 **19**，`🎉 All scenarios passed!`
  2. **diff 审计 PASS** —— `git diff HEAD~1 --stat` = 2 files / 184 insertions；`git diff HEAD~1 --stat -- task_plan.md` **0 行输出** → Goal / Key Decisions / Phase 结构零改动；新增文档已入跟踪（`git ls-files` 命中）
  3. **预算守卫 PASS** —— `code-map-generator.py:46/49` ROUTER_TOKEN_LIMIT=3000 / ENTRY_MAX_TOKENS=300；`exposure-guard.py:45-49` 三层 3000/300/500 + 双预算 24/2000；`i4-gate.py:38/39` ROUTER_LIMIT/ENTRY_LIMIT 全部在位
  4. **红线机检 PASS** —— `rpd-cold-start.py:213-255` verified/unverified/stale + `dependency_drift` + `:255 fingerprint_mismatch` 在位；**补跑 `i4-gate.py . --json` → exit 0 / `"pass": true` / regression_guard 三项全 ok**
  5. **向后兼容 PASS** —— `code-map-generator.py:50` SCHEMA_VERSION="2.1.0" + `:62` SCHEMA_WHITELIST=("2.0.0","2.1.0") 在位，且被 `i4-gate.py:101-105` 回归守卫消费
  6. **计划一致性 PASS** —— 10 个 Phase Status 全 complete、pending=0；本轮审计恰恰把第 6 项的盲点（只查 Status、不查 checkbox）补上并给出证据：**27 项无一项「未实现」**，故 Status=complete 有事实支撑，非假 complete
  7. **无 mock 注入 PASS** —— 纯 Markdown 文档，无视觉/UI 改动，红线不适用
- **🔍 F1 独立复核（本轮重点，差点被 bash 工具坑）**：`grep -c $'\r' SKILL.md` 在本工具下返回 **0 / exit 1**（引号转义失效），若据此会误判 Advancer 的「119 个 CR」造假。改用 **python 字节级复核**得到真相：工作区 8235 B（CR=119、LF=119）、git blob 8116 B（CR=0、LF=119）→ **8116+119=8235 完全成立**，`core.autocrlf=true`、无 `.gitattributes` 亦属实。**结论：F1「R-05 未违反但余量仅 76 B（0.93%）」判定成立，且「加守卫必须用 LF 口径」的陷阱提示正确**（`wc -c` 在 Windows 恒定 8235，会反过来卡死红线 3）
- **数字逐条独立复算（不采信 Advancer）**：分 Phase 未勾数 4/3/2/0/4/0/3/3/4/4 = **27** ✅ 与文档逐字吻合，22+1+4=27 自洽；基线 `HEAD~1` = `709a6fe` ✅；`ls scripts/*.py` = **18**（F2 属实）；`grep -c "SKILL" i4-gate.py` = **0**（无体积守卫，属实）；`4c40084` = 2026-08-21 12:24:36 ✅、`27f7fd5` = 14:13:45 ✅、handoff 260 行 ✅、`.project-state.md` 4659 B ✅、`grep -c "\.py" SKILL.md` = 30 ✅、`.workbuddy/memory/*.md` = 8（= 7 份日志 + MEMORY.md，与文档描述一致）✅
- **60 处 file:line 证据抽检**：retriever / code-map-generator / impact-analyzer / memory-layers / parking-lot / spec / run-eval / SKILL 工具箱表逐条打开核对 —— **内容全部命中**，只有 **3 处行号偏差（非造假，留档）**：①I4-1④ 与 I4-1② 引用的 `run-eval.py:745/746`（vector disabled / TODO 断言）**实际在 :747/:748**，偏移 +2，断言原文一字不差 ②I4-6② 的「docstring `:28`」实为**膨胀守卫**行，过期/`--drop-clean` 描述在 **:23-24**（`--drop-clean` 旗标名正确，见 usage :43 / code :488）③F3① 的 `origin/main..HEAD` = **45**，现读 **47**（+1 = 审计 commit 自身、+1 = 上轮 verifier commit 709a6fe），属 §零 R-1 已声明接受的自引用漂移，实质结论「全部提交都在 automation/i4-l2 单分支」成立
- **⚠️ 权限冲突 → 升级张敬拍板（Verifier 不自行扩权）**：审计 §5 动作 1 把「勾选 22 项 checkbox」归属写为 **Verifier**，但 `.workbuddy/automation-rules.md` Verifier 写入范围明确限定为 `task_plan.md（仅 Phase 状态标记：pending → complete）`，且通用规则 4 规定「两个 Agent 均不得修改计划的 Goal/决策/**Phase 结构**」。两条规则冲突时按**不扩权**处理 —— 本轮**未勾选任何 checkbox**，理由：①勾选 22 项会留下 5 项未勾的混合态，属计划形态变更 ②其中 I4-8① 与 I4-0② 涉及**文字内容修改**（加注「自动化轮次例外」、12→18），已超出状态标记 ③§5 动作 2 明示需张敬授权。**建议张敬一次性拍板**：(a) 授权 Verifier 勾 22 项 + 改 2 处措辞；(b) 保持现状（Status 已 complete，checkbox 作为历史留痕）；(c) 由人工在 H3 合并前统一整理
- **对 H3 的影响**：审计排除了「假 complete」可能，§八 合并面结论（17 纯新增 / 4 文件 14 处删改）不受影响；新增风险仅 F1（SKILL.md 余量 76 B，无机检拦截）
- **本 tick 改动**：仅 progress.md（Test Results 1 行 + 本条日志）；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **遗留**：① 22 项勾选权待张敬拍板（见上）② I4-9② 暂不勾 —— 建议「先压缩 SKILL.md 腾出 ≥200 B，再加 LF 口径守卫」，需授权 ③ D1/D2 + H1~H4 待拍板，**D2 须先于 H3** ④ 上上轮留档的 §三 3.2 误删区间问题（#63/#64 实为真实交付 17 行）仍未处理，建议下轮 Advancer 优先修 ⑤ 自动化 2026-08-31 23:59:59（Asia/Shanghai）到期，**剩约 30.8 小时**
- **方法沉淀**：①**「grep 返回 0」不等于「事实为 0」** —— 本工具下 `grep -c $'\r'` 因引号转义失效给出假 0，差点误判对方造假；涉及字节/不可见字符的核验一律改用 python 字节级读取 ②审计类文档的 0-trust 重心是 **file:line 的「内容」而非「行号」** —— 行号会随提交漂移（本轮 3 处），内容命中即证据成立，行号偏差只留档不 FAIL ③遇到「Advancer 建议我做 X」而规则未授权时，默认**不扩权并升级**，不因为对方写了「归属：Verifier」就自行动手

---

## 2026-08-30 20:2x（I4 Advancer · 修掉一条会造成不可逆破坏的高危命令：§8.4 压缩区间错位 +4 行 + #63/#64 误分类）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，交付完整性审计验证通过（27 项三重对账独立复算；F1 R-05 余量 76B 字节级复核属实） [verifier]`（HEAD `9e04c89`，2026-08-30 17:15:58 +0800）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**
- **模块**：I4-0~I4-9 全 complete、pending=0；L3 planned 冻结 → 不空转，兑现**连续两轮 Verifier 留档、两轮均未处理**的最高优先项（§三 3.2 误删区间）
- **为什么这条必须先修**：§8.4 的 H2 是本文档**唯一带 `sed -i` 的破坏性操作**。其余缺陷看错就是看错，这条按原文执行会**永久删错内容**；而 progress.md 在 main 上不存在、备份只有 `.workbuddy/tmp/progress-worktree-20260829-1910.md`（08-29 旧快照）→ 一旦执行几乎无法还原
- **做了什么**（仅 `docs/automation-governance-proposal.md`）：§零 新增 **R-4「行号区间 = 锚点求值，禁止硬编码」**+ 增补缘起；§三 3.2 全节重写（C-1/C-2 缺陷对照表 + 推翻前稿「行号不漂」结论 + 全部命令改锚点）；§3.3 压缩量 139→122、保留清单加 #63/#64、新增第 4 项「同步改写 ℹ️ 注记」；§8.2 `.gitignore` 行号 20-22→**16-18**（共 19 行）；§8.3 收益 139→122；§8.4 H2 由**一行硬编码 sed 改为 7 步锚点流程**（备份 / 锚点求值 / 三项前置断言 / dry-run / 执行 / 收尾 / 事后校验）
- **🔑 C-1 区间整体错位 +4 行（真实破坏风险，不是数值漂移）**：前稿 `sed -i '442,563d;576,592d'` 实际会 ① 误删行 442 的 ℹ️ 说明注记（Verifier 08-29 19:1x 刻意写入，解释这批日志为何保持未提交）② 把 #61 的「遗留问题」行 + 分隔符**留成孤儿残片** ③ 误删 #62 的「遗留问题」行（与 3.3「保留 #62」自相矛盾）④ #64 只删一半、剩 4 行悬空。正确区间实测 **446–567** / **580–596**
- **🔑 漂移根因（推翻前稿结论，一条命令可复现）**：前稿推理「新日志一律追加到尾部 ⇒ 中段行号不动」**只覆盖 Advancer、漏掉 Verifier** —— 每个 Verifier tick 会向**头部 Test Results 表**插 1 行，位置在压缩区间**之上**，整段被等量顶偏。实证 `#51` 标题行迁移：`0604e81`=**442** → `d5a0628`=**443** → `3163c73`=**445** → HEAD=**446**；`git diff 0604e81 HEAD -- progress.md` 头部区域 4 处新增**全部**是 Test Results 表行（0604e81/d5a0628/51b2e81/3163c73 四次验证记录）→ **偏移量 = 期间经过的 Verifier tick 数，只会继续增大**，硬编码行号方案**结构性不安全**
- **🔑 C-2 #63/#64 被误归「纯空转」**：#63 记录了「更新治理提案计数 + 追加 tick 日志」的真实文档产出；#64 是**交棒链条的唯一记录点**（闸门 `378b2f2`、治理提案 `562c14b` 已被 Verifier 复验）→ 删掉即断链、仓库内无法重建。可压缩净量 **139 → 122 行**，D2 收益下修为「当前行数 − 122 + 6」（按 903 计 ≈ 787，降幅 12.8%）
- **⚠️ 自己写的命令被实跑打回两次（0-trust 的实际价值）**：① 初版锚点用裸 `grep -n 'tick #62 '` → 实测 `grep -c` = **2**（#63 正文里也写了「tick #62」），求值直接报 `arithmetic syntax error` → 改为 `^## .*tick #62 ` ② 初版 dry-run 用 `grep -c 'tick #6'` → 实测返回 **2**（误命中 #60/#61）→ 改为 `grep -cE 'tick #6[2-5]'`。**若只「看着对」就写进文档，等于把两个新坑埋给执行者**；两处修正均已写入文档注释，防止后人重踩
- **0-trust 一手证据（20:1x~20:2x 实跑）**：三锚点 `^## .*tick #51 ` / `#62 ` / `#67 ` 的 `grep -c` 均 = **1**；可压缩区间 **446-567 = 122 行**；全段 **446-607 = 162 行**；修正后 dry-run `grep -cE 'tick #6[2-5]'` = **0**；区间末行 `cat -A` = `$`（空行，边界干净）；`wc -l progress.md` = **903**；`.gitignore` 共 **19** 行、例外在 **16-18**（`grep -n 'automation-rules'`）；#65 块止于 **607**（后接 #67，**#66 不存在** → 全段 END 锚点须用 `#67` 而非 `#66`）
- **eval 真实数字**：**19/19 PASS，REAL_EXIT=0**（`> /tmp/eval_i4_r4.out` 重定向取真实退出码，非管道码；`grep -c "✅ PASS"` = **19**、`🎉 All scenarios passed!`）。纯 Markdown 改动，未触碰 `scripts/`
- **改了哪些文件**：`docs/automation-governance-proposal.md`（+68 −19）、`progress.md`（仅本条日志）
- **遗留**：① D1/D2 + H1~H4 仍待张敬拍板，**D2 须先于 H3** ② 22 项 checkbox 勾选权冲突待拍板（上轮 Verifier 已升级，Advancer 无权代决）③ F1 SKILL.md R-05 余量 76 B 且无机检 —— 建议下轮 Advancer 接手，**必须用 LF 口径 `git show HEAD:SKILL.md | wc -c`**，用 `wc -c SKILL.md` 会因 CRLF 恒为 8235 而反卡红线 3 ④ §一/§五/§六 仍引用 tick 计数（按 §零 R-2 刻意保留原文，是「计数源混淆」的当事证据）⑤ 自动化 2026-08-31 23:59:59（Asia/Shanghai）到期，**剩约 27.6 小时**
- **方法沉淀**：**破坏性命令与描述性数字必须分级对待。** §零 R-1「自跑取当前值」治得了「数字变旧」，治不了「区间错位」—— 后者跑几次都是错的，且后果不可逆。凡文档内含 `sed -i` / `rm` / `git reset` 一类命令，必须①锚点求值②前置断言③dry-run 三件套齐备，并**由作者本人实跑一遍**（本轮正是实跑才暴露两个自造缺陷）。另：连续两轮 Verifier 留档同一项而无人处理时，该项应优先于任何「新增内容」——留档不等于已修。

---

## 2026-08-31 00:5x（I4 Verifier · 0-trust 独立检验 · 判定 A）

- **闸门**：`git log -1 --format=%s` = `fix(I4-closeout): 修正 §8.4 压缩命令的不可逆破坏风险（区间错位 +4 行 + #63/#64 误分类），新增 §零 R-4 锚点求值公约 [advancer]`（HEAD `bb58644`，2026-08-30 20:26:01 +0800）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**（`git status --porcelain` 0 行）
- **7 项 0-trust 逐项结果**：
  1. **eval 全量** ✅ —— `python scripts/run-eval.py` 真实复跑，**19/19 PASS**（A~X 全过）、`🎉 All scenarios passed!`、**REAL_EXIT=0**（重定向取真实退出码，非管道码）
  2. **diff 审计** ✅ —— `git diff HEAD~1 --numstat` = docs/automation-governance-proposal.md **68/19** + progress.md **18/0**，共 2 文件；**task_plan.md diff 0 行**（Goal / Key Decisions / Phase 结构未动）；改动完全在 Advancer 写入范围（docs/ + progress.md）
  3. **预算守卫** ✅ —— code-map-generator.py:46/49 = 3000/300；exposure-guard.py:45-47/50 = 3000/300/500 + DEEP_FOLLOWUP_TURNS=2；i4-gate.py:38/39 在位
  4. **红线机检** ✅ —— rpd-cold-start.py:213-255 verified/stale/unverified + :246 missing + :255 fingerprint_mismatch 未回归；**补跑 `python scripts/i4-gate.py . --json`** → **exit 0 / `"pass": true`**，regression_guard 三项全 ok（`budget:router_entry` / `redline:trust` / `compat:schema`）
  5. **向后兼容** ✅ —— SCHEMA_VERSION 2.1.0 + SCHEMA_WHITELIST ("2.0.0","2.1.0")（code-map-generator.py:50/62）在位，且被 i4-gate.py:101-105 回归守卫实际消费
  6. **计划一致性** ✅ —— task_plan.md I4-0~I4-9 **10 个 Phase Status 全 complete**、L3 planned 冻结 → pending=0，与本轮「无 Phase 可标 complete」一致；`git rev-list --left-right --count origin/main...HEAD` = 0 behind / **49** ahead
  7. **无 mock 注入** ✅ —— 纯 Markdown 文档改动，无视觉/UI 产物，该项不适用
- **0-trust 独立复算（不采信 Advancer 一手值，全部重跑）**：
  - 三锚点 `^## .*tick #51 / #62 / #67 ` 的 `grep -c` **均 = 1** ✅；行号实测 **446 / 568 / 608** → 可压缩区间 **446-567 = 122 行** ✅、全段 **446-607 = 162 行** ✅，与文档「122 / 162」逐字吻合
  - **分段逐块复算**（python 遍历标题行）：#51~#58 各 11、#59=12、#60=11、#61=11 → **122** ✅；#62=12 / #63=9 / #64=8 / #65=11 → **40** ✅；122+40=**162** 自洽
  - 边界：446 = `#51` 标题、567 = 空行（`cat -A` = `$`）、568 = `#62` 标题、607 = 空行、608 = `#67` 标题 → 边界干净，**#66 确不存在**，文档「END 锚点须用 #67」属实
  - 修正后 dry-run `sed -n '446,567p' progress.md | grep -cE 'tick #6[2-5]'` = **0** ✅
  - **C-1 漂移实证逐条复现**：`#51` 标题行 `0604e81`=**442** → `d5a0628`=**443** → `3163c73`=**445** → `HEAD`=**446**，四个数值与文档**逐字吻合** → 「Verifier 向头部 Test Results 表插行 ⇒ 中段区间被等量顶偏」根因成立，硬编码行号方案结构性不安全
  - **C-2 分类更正成立**：#63（9 行，治理提案计数更新的真实产出）/ #64（8 行，`378b2f2`/`562c14b` 交棒链条记录点）确有实质内容 → 可压缩量 139 → **122**
  - **裸锚点不唯一实证**：全文 `grep -c 'tick #62 '` = **3**（Advancer 记 2，+1 = 其自身日志再次提及）；区间内 `sed -n '446,567p' | grep -c 'tick #6'` = **2**，命中行恰为 #60/#61 标题 → 文档改用 `^## .*` 与 `#6[2-5]` 的两处自纠均有实测依据
  - `.gitignore`：`wc -l` = **19**、`grep -n 'automation-rules'` = **18**，16-18 行实为 `.workbuddy/*` + 注释 + 例外 → §8.2 从「20-22」更正为「16-18」**属实**
  - 算术复核：903−122+6 = **787** ✅、(903−787)/903 = **12.8%** ✅ 与文档一致
- **判定 A**（无 pending Phase 可标 complete）：**task_plan.md 未动**；progress.md 追加 Test Results 1 行 + 本条日志
- **本 tick 改动**：仅 progress.md；未触碰 scripts/ docs/ references/ eval/ task_plan.md；未 push、未碰 main
- **留档观察（非 FAIL，Verifier 禁改 docs/）**：①§三 3.2「文件总行数 903」现读 921（+18 = 本 commit 自身日志），已被 §零 R-1 覆盖 ②3.2 表内行号 446-607 已标注「20:1x 快照、请自跑锚点求值」，因 H2 全面改锚点，行号仅作示例 → 无 C-1 类破坏风险 ③H2-3 前置断言写死「行数 = 122」，日后区间内容增删会误停手 —— 属**安全侧失败**（不删错内容），可接受 ④Advancer 日志称 docs「+68 −19」与 numstat 一致，其「progress.md 仅本条日志」亦属实
- **遗留**：① D1/D2 + H1~H4 仍待张敬拍板，**D2 须先于 H3** ② 22 项 checkbox 勾选权冲突待拍板 ③ F1 SKILL.md R-05 余量 76 B 且无机检（下轮 Advancer 须用 LF 口径 `git show HEAD:SKILL.md | wc -c`）④ 自动化 **2026-08-31 23:59:59（Asia/Shanghai）到期，剩约 23 小时**
- **方法沉淀**：①**文档类 commit 的 0-trust 重心 = 文档给出的命令是否可执行、给出的数字是否可复现** —— 本轮把所有锚点 `grep -c`、行号迁移序列、分段行数、dry-run、`.gitignore` 行号全部独立重跑，C-1/C-2 两条更正**均被证实** ②**Advancer 自曝「自己写的命令被实跑打回两次」是正面信号** —— 说明其命令经过实跑而非凭空写；Verifier 只需复跑验证其修正后的版本，不必怀疑其动机 ③**破坏性命令的验收标准应高于描述性数字**：数字漂一次无害，区间错位不可逆；本轮看到 H2 已从一行 `sed -i` 升级为「备份 → 锚点求值 → 三项前置断言 → dry-run → 执行 → 收尾 → 事后校验」7 步，符合该标准

---

## 2026-08-31 01:1x（I4 Advancer · F1：给 SKILL.md R-05 加机检守卫，堵住 76 B 裸奔 + CRLF 假失败）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，§8.4 压缩命令风险修正（R-4 锚点求值 + C-1 区间错位 + C-2 #63/#64 误分类）验证通过 [verifier]`（HEAD `9e04c89`）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**
- **模块**：I4-0~I4-9 全 complete、pending=0。按第 2 步规则「全 complete → 写收官报告」，但**收官报告已于 2026-08-21 落盘**（本文件 §Session: 2026-08-21），重抄一遍属空转 → 沿用前几轮约定，**兑现上一轮 Verifier 留档 #③**：F1 = SKILL.md R-05 余量仅 76 B 且**无任何机检**
- **为什么值得做**：R-05 是 CLAUDE.md 明列的硬约束（「≤8KB，超限先压缩再提交」），但 `grep -c "SKILL" scripts/i4-gate.py` = **0** —— 唯一的约束是「人记得住」，而余量只剩 76 B，一次顺手加两行就会破线且无人拦截
- **做了什么**（`scripts/i4-gate.py` 纯新增，不改任何既有判定）：新增常量 `SKILL_LIMIT = 8192` / `SKILL_WARN_MARGIN = 512`、辅助函数 `_lf_size()`、第 4 条回归守卫 `budget:skill_size`；docstring 同步登记
- **🔑 关键设计：必须走 LF 口径，否则守卫会在它本该保护的平台误报**。实测 `wc -c SKILL.md`（工作区 CRLF）= **8235 B > 8192**，直接拿裸字节判定会**恒 FAIL**；而 `git show HEAD:SKILL.md | wc -c` = **8116 B**（CRLF 数 119，8235−119=8116）。故 `_lf_size()` 先 `read_bytes().replace(b"\r\n", b"\n")` 再计量 → 实测报 **8116 B / 余量 76 B / PASS**，与 git blob 口径完全一致
- **🚨 踩坑：自己的改动把 eval 打挂了（18/19，U 失败）** —— `scripts/run-eval.py:1275` 硬断言 `len(reg["findings"]) == 3`，新增第 4 条守卫即破。**定位过程**：`git stash push scripts/i4-gate.py` 后复跑 = **19/19 PASS / exit 0** → 确认是我的改动导致，非环境抖动；而非「改断言让它过」了事
- **⚖️ 断言改造（本轮唯一需要 Verifier 重点 scrutiny 的地方）**：把 `len(...) == 3` 改为**按名契约**——要求 `{"budget:router_entry","redline:trust","compat:schema","budget:skill_size"}` 四项**全部在集**且 `all(ok)`。这是**加强不是放松**：①原来只数 3 个匿名项，现在点名 4 项，漏任何一项会**按名失败**而非靠数量蒙混 ②新增守卫被 eval 反向锁定，拆掉就挂。**负向测试实证其非空转**：`git stash` 掉 i4-gate.py 而保留新断言 → eval **exit 1 / U FAIL**，输出 findings 里只有 3 项、无 `budget:skill_size` → 证明新断言真的在守新守卫，不是橡皮图章
- **0-trust 一手证据（01:1x 实跑）**：`git show HEAD:SKILL.md | wc -c` = **8116** ✅；`wc -c SKILL.md` = **8235** ✅；CRLF 计数 **119** ✅；`grep -c "SKILL" scripts/i4-gate.py` 改动前 = **0** ✅（改动后 >0）；`i4-gate.py . --json` → **REAL_EXIT=0 / pass=true**，4 条 findings 全 OK，`budget:skill_size` 报「8116B (LF caliber) <= 8192B, headroom 76B」且 `warn=true`（余量 <512，触发 advisory 提示）
- **守卫边界测试（合成文件，未触碰真实 SKILL.md）**：8192 B → **PASS**（headroom 0，边界含在内）；8193 B → **FAIL**（headroom −1，能抓 1 字节越界）；9000 B → **FAIL**；**正确构造的 CRLF 文件 raw 8235 B（naive `wc -c` 会判 FAIL）→ 守卫报 8116 B PASS，假失败陷阱已堵**；文件缺失 → **FAIL**
- **⚠️ 一次测试自身写错、被复跑纠正**：首版 CRLF 测试对**已含 CRLF 的真实文件**再做 `replace(b"\n", b"\r\n")`，产出 `\r\r\n` 畸形输入（8235 B / headroom −43 的_FAIL_ 结论是假信号）。已改为「先归一化成 LF 原文再转 CRLF」重测，结论反转为 PASS。**若直接采信首版输出，会得出「守卫在 CRLF 下误报」的相反错误结论并记录进文档**
- **eval 真实数字**：**19/19 PASS，REAL_EXIT=0**（`> eval_out.txt` 重定向取真实退出码；`grep -c "✅ PASS"` = 19、`🎉 All scenarios passed!`）。诚实失败路径 rc 2 与正常路径 rc 0 均由 U 场景内含断言覆盖（1275→1283 行），未单独加探针
- **改了哪些文件**：`scripts/i4-gate.py`（+40 −0）、`scripts/run-eval.py`（+9 −1）、`progress.md`（仅本条日志）。**`SKILL.md` 零改动**（`git diff --stat SKILL.md` = 0 行）、**`task_plan.md` / `findings.md` 零改动**
- **红线复核**：预算守卫 3000/300 在位（code-map-generator.py:46/49）；SCHEMA_VERSION 2.1.0 + 白名单 ("2.0.0","2.1.0") 在位（:50/:62）；无新增外部依赖（diff 内无新 import）；未 push、未碰 main
- **遗留**：① SKILL.md 余量仍仅 **76 B**（本轮只加守卫、未压缩）—— 压缩需动内容，属独立决策，建议下轮或人工评估 ② D1/D2 + H1~H4 仍待张敬拍板，**D2 须先于 H3** ③ 22 项 checkbox 勾选权冲突待拍板 ④ 自动化 **2026-08-31 23:59:59（Asia/Shanghai）到期，剩约 22.8 小时**
- **方法沉淀**：**①「加机检」与「改数字」要分开做** —— 余量 76 B 有两个独立解法（加守卫 / 压体积），前者零风险且立刻消除「破线无人知」，后者动内容需授权；先做零风险那个。②**断言实现细节（数量/内部名）会在功能正当演进时误伤**，应断言行为与命名契约 —— 但改造时必须反向证明「拆掉新功能会 FAIL」，否则就是给自己放水。③**Windows 上一切字节阈值必须先定口径**（LF vs CRLF），用工作区裸字节做硬约束判定，等于在唯一需要它的平台上制造假失败

---

## 2026-08-31 16:3x（I4 Verifier · F1 机检守卫 0-trust 复核：7 项全 PASS，判定 A）

- **闸门**：`git log -1 --format=%s` = `feat(I4-closeout): R-05 给 SKILL.md 加机检守卫，LF 口径计量堵住 CRLF 假失败 [advancer]`（HEAD `9bd7a69`）→ 本轮属 Verifier ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**

### 7 项 0-trust 检查

| # | 检查项 | 真实命令输出（一手证据） | 判定 |
|---|--------|------------------------|------|
| 1 | eval 全量 | `python scripts/run-eval.py` → **19/19 PASS**（A~X 全绿）+ `🎉 All scenarios passed!`，**EXIT_CODE=0** | ✅ PASS |
| 2 | diff 审计 | `git diff HEAD~1 --name-only` = 仅 `progress.md` / `scripts/i4-gate.py` / `scripts/run-eval.py`（+69 −1）；`task_plan.md` / `findings.md` / `SKILL.md` **零改动**，Goal / Key Decisions / Phase 结构未被动 | ✅ PASS |
| 3 | 预算守卫 | `code-map-generator.py:46` `ROUTER_TOKEN_LIMIT=3000`、`:49` `ENTRY_MAX_TOKENS=300` 在位；新增 `i4-gate.py:44` `SKILL_LIMIT=8192`；`i4-gate.py . --json` → `budget:skill_size` = **8116B (LF caliber) ≤ 8192B, headroom 76B, ok=true, warn=true** | ✅ PASS |
| 4 | 红线机检 | `i4-gate.py . --json` 4 条 findings **全 ok**；`redline:trust` 在位，`rpd-cold-start.py:213/246/255` verified / stale(missing) / stale(fingerprint_mismatch) 逻辑未回归 | ✅ PASS |
| 5 | 向后兼容 | `code-map-generator.py:50` `SCHEMA_VERSION="2.1.0"`、`:62` `SCHEMA_WHITELIST=("2.0.0","2.1.0")` 仍在；`compat:schema` ok=true | ✅ PASS |
| 6 | 计划一致性 | I4-0~I4-9 Status 全 complete、pending=0；本轮为 **I4-closeout（F1）**，`task_plan.md` **无该 Phase 条目**。依 automation-rules §通用规则 4（Phase 结构属用户权限，Verifier 只改状态标记），**不新增 Phase、不改结构** —— 与前两轮 verifier（`1969234` / `9e04c89` 均只动 progress.md）口径一致 | ✅ PASS（沿用，无新增不一致） |
| 7 | 无 mock 注入 | 本轮纯脚本 / 守卫改动，**无视觉或 UI 改动**，该项不适用；全部证据为实跑输出，未注入任何 mock | ✅ PASS（N/A） |

### 独立复算（不采信 Advancer 自述）

- **体积口径三证对齐**：`git show HEAD:SKILL.md | wc -c` = **8116** ✅；工作区 `wc -c SKILL.md` = **8235** ✅；CRLF 计数 **119** ✅；8235 − 119 = 8116，与 i4-gate 报数**完全一致**
- **`_lf_size()` 边界（独立 import 模块实跑，非读代码推断）**：
  | 用例 | 实测 | 结论 |
  |------|------|------|
  | 8192 B 纯 LF | **8192**（margin 0） | 边界含入 → PASS |
  | 8193 B 纯 LF | **8193**（margin −1） | 能抓 1 字节越界 → FAIL |
  | 正确构造的 CRLF 样本（raw 8216 B） | LF 口径 **8116 B** | 假失败已堵 → PASS |
  | 文件缺失 | **None** | FAIL 路径可达 |
- **🔑 负向测试（证明新断言不是橡皮图章）**：`git worktree add --detach` 建**隔离副本**（主工作区全程零改动），在副本中删除 `budget:skill_size` 守卫后复跑 eval → **EXIT=1，❌ FAIL - U (v2 code-map)**，findings 仅剩 3 项且无 `budget:skill_size` → 证明 `run-eval.py:1275` 的按名契约断言**真的在守新守卫**。测后 `git worktree remove --force` + `prune`，`git worktree list` 仅剩主工作区、`git status --short` **clean**
- **断言改造评估（本轮唯一需 scrutiny 处）**：`len(reg["findings"]) == 3` → 按名集合 `{"budget:router_entry","redline:trust","compat:schema","budget:skill_size"}` 全在集 + `all(ok)`。判定为**加强而非放松**：原断言只数 3 个匿名项，新断言点名 4 项，漏任一项会**按名失败**；且负向测试已反向证明「拆掉即挂」。**未发现"改断言让它过"的放水痕迹**

### 判定

**A（7 项全 PASS + 本轮验收达成）** —— `task_plan.md` **无需改动**（无 closeout Phase 条目，且新增 Phase 结构属用户权限）；仅追加本条 `progress.md` 记录并 `git add progress.md` 单文件提交。**未 rollback，代码文件零改动**。

### 遗留（顺延，非本轮 FAIL）

1. SKILL.md 余量仍 **76 B**，压缩属独立决策（动内容需授权）—— 本轮只加守卫，符合「加机检 / 改数字分开做」
2. D1/D2 + H1~H4 仍待张敬拍板，**D2 须先于 H3**
3. 22 项 checkbox 勾选权冲突待拍板
4. 自动化 **2026-08-31 23:59:59（Asia/Shanghai）到期，剩约 7.4 小时**

### 方法沉淀

1. **改动「校验器自身」时，验收标准必须升级为负向测试** —— 正向全绿只证明"没弄坏"，只有"拆掉新功能必须 FAIL"才能证明新校验真的生效、不是橡皮图章
2. **负向测试要在隔离副本里做**（`git worktree add --detach` + 事后 `remove`/`prune`）—— 在主工作区删代码再恢复，恢复失败就是灾难
3. **Windows 上字节阈值必须二次确认口径**：本轮若只看 `wc -c SKILL.md` = 8235，会判定 R-05 破线，得出与事实完全相反的结论
4. **"未勾选但 Status=complete"不一定是假 complete** —— 已有 2026-08-30 交付完整性审计（27 项三重对账，见 `docs/i4-delivery-completeness-audit.md` + 本文件 §2026-08-30）给出证据，Verifier 应查证据不查结论，不重复推翻已审计结论

---

## 2026-08-31 21:3x（I4 Advancer · 到期前轮：修正 §7.1 rrule 事实错误 + 代执行 H4 到期前确认）

- **闸门**：`git log -1 --format=%s` = `verify(I4-closeout): 7 项 0-trust 全过，R-05 SKILL.md 机检守卫…[verifier]`（HEAD `98d07bb`）→ 本轮属 Advancer ✅；分支 `automation/i4-l2` ✅；起始 worktree **clean**
- **模块**：I4-0~I4-9 全 complete、pending=0；收官报告 2026-08-21 已落盘，重抄属空转 → 沿用近几轮约定，**兑现上一轮 Verifier 留档中与时间窗口强相关的项**：自动化 **今晚 23:59:59 到期**，§七 到期处置预案的 H4 仍停在 08-30 07:13 的陈旧基线
- **🔴 本轮实际发现（非预想）**：`automation_update(mode="list")` 返回的两个 rrule **并不相同** —— Advancer `INTERVAL=1`、Verifier **`INTERVAL=12`**。而 §7.1 表把 Verifier 的 rrule 写成「同左」（即每 1 小时），**与配置不符**。补 `mode="view"` 逐个实查确认：`validUntil` 两者确为同一时刻（`2026-08-31T15:59:59.999Z`），故「同时停」的**结论成立**，但**运行频率不同**被漏记了
- **为什么这个错值得修**：§7.2 原写「若有效期被延长 → 立即复活，恢复**每小时**空转」。按真实配置应为「Advancer 24 次/天 + Verifier 2 次/天」。张敬若据此估算延期成本，会**高估近一倍**。已改为标注实测频率
- **教训（已写入文档）**：§7.1 表除 `validUntil` 外的字段此前多为「同左」**推定**而未逐个 `view` 实查 —— 这与本文档 §零 口径公约（凡数字须可复现）自相矛盾。凡写进本文档的配置值一律取自 `mode="view"` 返回，不靠对称性推断
- **代执行 H4（新增 §7.5）**：H4 原列「需人工」，实为**纯只读核查**，agent 有权代跑。2026-08-31 **21:39:04**（+0800，`date` 实跑）七项一手值：`git status --porcelain` = **空**（无未落盘成果）；HEAD = **`98d07bb`**；`git rev-list --left-right --count origin/main...HEAD` = **0 behind / 52 ahead**；`git log -1 origin/main` = `1081696 2026-08-03 22:26:51` → **main 自 08-03 未动**，0 behind 属实；`python scripts/run-eval.py` = **19/19 PASS / exit 0**；`wc -l progress.md` = **1020 行**（08-30 09:16 为 738 行 → 12 天 **+282 行 / 12 commits**，印证 H2「持续增长」判断）
- **结论**：到期前**无未落盘成果**。但 4 项里只解决了 1 项 —— **H1（显式 PAUSED）/ H2（授权压缩）/ H3（分支归宿）仍需张敬**，性质未变（agent 无权改自动化配置 / 禁历史改写 / 禁自动 merge main 与 push）
- **🚨 唯一实质风险已点名**：**H3** —— 52 个提交只存在于**本地**分支 `automation/i4-l2`，远端仅 `refs/heads/main`、无副本；换机或清工作区即失。其余三项只是语义/整洁度问题
- **🛡️ 自查：文档里的命令逐条复跑**（沿用前几轮方法，文档价值 = 其命令可执行）：`git status --porcelain` / `git rev-parse --short HEAD` / `git branch --show-current` / `git rev-list --left-right --count origin/main...HEAD` / `git log -1 --format='%h %ci' origin/main` / `wc -l < progress.md` **六条全部复跑，返回值与文档所载一致**
- **自引用漂移已显式标注**：§7.5 第 1 行注明「clean」测于**本轮改动落盘前**，并写「commit 后复测同样为空」—— 该承诺已在 commit 后实跑兑现（见下）
- **eval 真实数字**：**19/19 PASS，`REAL_EXIT=0`**（两次独立运行：改动前取基线、提交前取门禁，均为 19 / exit 0）
- **改了哪些文件**：`docs/automation-governance-proposal.md`（**+35 −3**，单文件）；`progress.md`（仅本条日志）。**`scripts/` 零改动、`SKILL.md` 零改动、`task_plan.md` / `findings.md` 零改动**（`git diff --stat` 提交前 = `1 file changed`）
- **红线复核**：未 push、未碰 main；无新增外部依赖；eval 全过才 commit；`git add` 仅两个具体文件，未用 `-A`/`.`
- **遗留**：① **H1/H2/H3 仍待张敬拍板（H3 是唯一实质风险：52 commits 无远端副本）** ② D1/D2 + 22 项 checkbox 勾选权冲突待拍板 ③ SKILL.md 余量仍 **76 B**（压缩属独立决策）④ 自动化 **2026-08-31 23:59:59 到期，剩约 2 小时**
- **方法沉淀**：**①「同左 / 同上 / 以此类推」是文档里最危险的两个字** —— 它看起来是复用，实为未经验证的推定；本表的 `validFrom` 恰好同值属于运气，`rrule` 就翻车了。**凡配置值，逐个 `view` 实查，对称性不算证据**。②**「需人工」这个标签要定期重估** —— H4 被标了 12 天无人做，实际只是纯只读核查，agent 本可代办；分类时应按「是否需要权限/是否不可逆」判，不按「是否有人提过」判。③**文档的数字错，危害取决于它驱动的决策** —— rrule 错本身无害，但它支撑的「延期成本估算」会翻倍；评估文档缺陷时问一句「谁会拿这个数字做什么决定」
