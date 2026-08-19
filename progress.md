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
| Where am I? | L2 — I4 外扩迭代 Phase I4-0（基线核对），处于整体生命周期计划框架下 |
| Where am I going? | I4-1 R-22 → I4-2 R-19 → I4-3 R-25 → I4-4 R-20 → I4-5 R-23 → I4-6 R-21 → I4-7 parking-lot → I4-8 测试 → I4-9 交付 → L3 未来三支柱 |
| What's the goal? | RPD-skill 整体生命周期管理：在红线之下按版本阶段推进能力交付 |
| What have I learned? | 见 findings.md（资产台账 + UA/TAM 研究 + R-19~R-29 + 三支柱） |
| What have I done? | 资产全量盘点 + 生命周期计划重构 + I4 计划升级保留 + 资产台账落盘 |

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
