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
