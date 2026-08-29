# RPD-skill I4 自动化任务 · 交接文档

> 创建于 2026-08-19 01:52 · 作者：福帮手（被用户终止，原因：反复创建错误类型的任务，浪费资源）
> 用途：让下一轮接手者（人或 AI）不重复我的错误，直接从正确位置继续。

---

## 一、项目快照

| 项 | 值 |
|---|---|
| 项目 | RPD-skill（Agent Skill，项目全生命周期管理） |
| 仓库 | E:\Desktop\work\RPD-skill |
| GitHub | ZhangJing-gugugaga/RPD-Skill |
| 当前版本 | v2.0.2 |
| 当前分支 | `automation/i4-l2`（从 main 创建，已 commit 基础文件） |
| 最新 commit | `854a67f` chore: 初始化自动化计划三件套+规则+I4研究报告 |
| Eval 基线 | 19/19 PASS（A~X，exit 0），2026-08-19 复跑确认 |

## 二、已完成且有效的资产

### 计划三件套（已 commit 到 automation/i4-l2）
- `task_plan.md` — L0–L3 生命周期计划，含 Key Decisions（Q1~Q5 全部拍板）
- `findings.md` — 全量资产台账（A–H 八类）+ UA/TAM 研究结论
- `progress.md` — 进度日志 + Test Results 真实基线
- `.workbuddy/automation-rules.md` — Advancer/Verifier 规则 + 7 项 0-trust 验证清单

### Key Decisions（已拍板，直接执行）
| # | 决策 |
|---|------|
| Q1 | R-22 零外部依赖先行（BM25+RRF），向量打标 TODO |
| Q2 | R-19 仅复用 R-10 knowledge-graph.json，不自建 AST |
| Q3 | R-20 从现有 PRD 文档解析，不新增 domain 注册 |
| Q4 | R-23 第三级语义摘要 ≤500 token，深入追问=连续2轮追问 |
| Q5 | M1/M2 纳入 eval 基线作为 I4 出口 Gate |

### WorkBuddy Todo（10 条，已创建，在项目面板可见可调）
| ID | 模块 | 状态 |
|----|------|------|
| `rhb7Wp` | I4-0: 基线核对 | 进行中 |
| `rcW4RS` | I4-1: R-22 混合检索 | 待开始 |
| `raUZs4` | I4-2: R-19 边信息复用 | 待开始 |
| `rnAxRa` | I4-3: R-25 依赖版本锁定 | 待开始 |
| `rsO1C9` | I4-4: R-20 PRD↔代码影响分析 | 待开始 |
| `rvXVu0` | I4-5: R-23 渐进式暴露 | 待开始 |
| `rZEKBI` | I4-6: R-21 L0-L3 分层记忆 | 待开始 |
| `r7Madr` | I4-7: parking-lot 治理 | 待开始 |
| `rMym7V` | I4-8: 测试与验证 | 待开始 |
| `rDdzl2` | I4-9: 文档与交付 | 待开始 |

### 研究报告
- `docs/research-report-ua-tam-optimization.md`（537 行，26 参考文献，I4 全部依据）

## 三、我犯的错误（接手者别重复）

### 错误 1：用 Agent 工具的 model 参数找 hy3
- Agent 工具只支持 default/lite/reasoning，没有 hy3
- hy3 在**自动化系统**里（`automation_list_models` 返回），不是在 Agent 工具里
- 教训：找模型要先查 `mcp__wb-issues__automation_list_models`

### 错误 2：用 TeamCreate + 后台 Agent 创建团队
- 用户要的是 WorkBuddy 自动化任务（`automation_create`），不是 agent 团队
- 团队是自主后台运行，用户在 UI 里看不见调不了
- 已清理：团队已删除

### 错误 3：用 todo_create 当自动化任务
- todo 是项目计划项，不是自动化任务
- 用户要的是 `automation_create` 创建的定时自动运行任务
- todo 本身没错（作为计划展示有用），但它不等于自动化

### 错误 4：recurring 调度类型 BYHOUR 只取第一个值
- 用 `FREQ=DAILY;BYHOUR=0,2,4,6,8...` 想实现每 2 小时，系统只取第一个值变成每天 1 次
- 应该用 `schedule_type: "interval"` + `rrule: "FREQ=HOURLY;INTERVAL=2"`
- 两个自动化任务因此被删除，需要重建

## 四、未完成的关键步骤：重建两个自动化任务

### 自动化系统资源清单（已查清，可直接用）

| 资源 | 值 |
|------|---|
| 模型 | `hy3`（id: hy3） |
| 可用专家 | 技能匠人（Skill制作顾问）/ 福帮手（超级独董会）/ 听声声 / 鹏城信息 |
| 可用 Skill | planning-with-files / Deep Research / 提示词工程专家 / 腾讯会议 |
| 可用 Connector | TAPD / tdocs-app |
| 项目 owner | id: 6c5fe5b9-1941-4c49-8b3d-e030890e7faa |

### 需要创建的两个自动化任务

**任务 1：I4-推进**
- name: `I4-推进：按计划实现下一模块`
- schedule_type: `interval`
- rrule: `FREQ=HOURLY;INTERVAL=2`（每 2 小时）
- model_name: `hy3`
- expert_name: `技能匠人`
- skill: `/planning-with-files`（写在 prompt 里）
- connector_names: `["TAPD", "tdocs-app"]`
- prompt 要点：读 task_plan.md 找下一个 pending 模块 → 实施 → eval 19/19 PASS → commit 到 automation/i4-l2 → 不 push、不碰 main、不改计划结构
- 完整 prompt 见 `progress.md` Session 2026-08-19（自动化启动段落）

**任务 2：I4-验证**
- name: `I4-验证：0-trust 独立检验`
- schedule_type: `interval`
- rrule: `FREQ=HOURLY;INTERVAL=2`（错开 1 小时启动，或用 `FREQ=HOURLY;INTERVAL=2` 但 valid_from 设晚 1 小时）
- model_name: `hy3`
- expert_name: `福帮手`
- skill: `/planning-with-files`
- connector_names: `["TAPD", "tdocs-app"]`
- prompt 要点：7 项 0-trust 检查 → PASS 标 complete / FAIL revert → 不读 Advancer 对话、不改代码
- 完整 prompt 见 `progress.md` 同上段落

### 关于错开 1 小时
用户要求严格 1h 交替（推进奇数小时，验证偶数小时，或反过来）。`interval` 类型只支持固定间隔，不支持"偶数小时跑"。两个方案：
1. 两个都用 `FREQ=HOURLY;INTERVAL=2`，但第二个的首次启动时间手动设为晚 1 小时（如果系统支持 offset）
2. 两个都用 `FREQ=HOURLY;INTERVAL=1`（每小时都跑），但在 prompt 里写明"如果距上次自己运行不足 2 小时则跳过"——不优雅但能用
3. 直接两个都用 `FREQ=HOURLY;INTERVAL=2`，接受它们可能同时跑，靠 prompt 里的串行逻辑保证不冲突

**建议接手者先测试 `interval` + `FREQ=HOURLY;INTERVAL=2` 是否正确生效，再决定错开方案。**

## 五、用户要求与红线

| 要求 | 状态 |
|------|------|
| 用 hy3 模型 | ✅ 确认可用（id: hy3） |
| 配置好 skill | planning-with-files（写在 prompt 里） |
| 配置好专家 | 推进→技能匠人 / 验证→福帮手 |
| 配置好 MCP/Connector | TAPD + tdocs-app |
| 写好规则 | ✅ `.workbuddy/automation-rules.md` |
| 每小时一次直到计划结束 | ❌ 未完成（调度类型需重建） |
| 计划无"本轮不做" | ✅ 已清理 |
| 自动化长期推进 | valid_until 设为 2026-09-19 |
| FAIL 自动 revert | ✅ 写在验证 prompt 里 |
| 仅 automation 分支手动 merge | ✅ 写在规则里 |

### 8 条红线（所有自动化任务必须遵守）
1. 不 push 到远程
2. 只在 automation/i4-l2 分支工作
3. 测试 0 failed 才 commit
4. 视觉验证禁 mock 注入
5. 信息不全先记录不瞎猜
6. 预算守卫不破：router ≤3k / 单条 ≤300 token
7. R-10 向后兼容
8. 红线机检 + 三级信任持续有效

## 六、下次接手者的第一步

1. 读本文件 + `task_plan.md` + `progress.md`
2. 用 `automation_create` 重建两个自动化任务（interval 类型，参数见第四节）
3. 先跑一次推进任务验证 hy3 + skill + expert 是否正常工作
4. 确认调度生效后，让它长期运行
5. I4-0 基线核对已部分完成（git + eval done），剩余文档项可由第一个推进 tick 完成

---

## 七、交接已完成（2026-08-19 02:10 · 紫怡接手）

**第四节的两个自动化任务已创建，无需重建。再次创建会产生重复调度。**

| 任务 | ID | 调度 | 模型 | 专家 | Skill | Connector |
|------|----|------|------|------|-------|-----------|
| I4-推进（Advancer） | `5867270` | interval · 每 1 小时 | hy3 | 技能匠人 | /planning-with-files | TAPD, tdocs-app |
| I4-验证（Verifier） | `5867281` | interval · 每 1 小时 | hy3 | 福帮手 | /planning-with-files | TAPD, tdocs-app |

均 ACTIVE，`valid_until` = 2026-09-19，时区 Asia/Shanghai，首次运行 2026-08-19 03:00。
`interval` + `FREQ=HOURLY;INTERVAL=1` 已验证生效（返回 `schedule_desc: 每 1 小时`，`cron: 0 0 */1 * * *`），第四节的错误 4 已规避。

### 对第四节「错开 1 小时」问题的最终解法

三个候选方案都没采用。`interval` 不支持小时级 offset，`valid_from` 只到日粒度，靠时间错开做不到。
改为**从 git log 推导轮次**——两个任务都每小时唤醒，第 0 步执行 `git log -1 --format=%s`：

| HEAD commit 尾标 | Advancer | Verifier |
|---|---|---|
| `[advancer]` | 跳过 | 干活 |
| `[verifier]` / `[verifier-revert]` / `[automation-init]` | 干活 | 跳过 |

每小时恰好一个 Agent 真正工作，另一个读一行 git log 即退出。好处：
- 零额外状态文件，不需要 .gitignore 改动，不与 `git revert` 纠缠
- eval FAIL 时不 commit → HEAD 不变 → 下个 tick 自动重试同一模块（自愈，比时间错开更符合真实依赖）

⚠️ **代价**：Verifier 回滚必须用 `git revert --no-commit HEAD` 再手写 message。直接 `git revert HEAD` 的默认信息是 `Revert "feat(...) [advancer]"`，会把 `[advancer]` 带进来导致轮次死锁。已写进 Verifier prompt。

### 补的设计缺口：第三种判定

原规则只有 PASS→标 complete / FAIL→revert。缺了「7 项全过但该 Phase 验收标准只做了一半」这种情况——按原规则会被误回滚，白扔有效成果。
已在 Verifier prompt 加判定 C：**不回滚、不标 complete**，在 progress.md 列出剩余勾选项，commit `[verifier]` 交回 Advancer 下个 tick 继续同一模块。
建议同步更新 `.workbuddy/automation-rules.md` 的 Verifier 工作流程章节。

### 与项目面板 todo 打通

两份 prompt 都内置了 10 条 todo 的 ID 映射，并要求先调 `todo_statuses` 拿真实状态 id（不硬编码）：
Advancer 置 running + 评论 commit hash；Verifier 按判定 A/B/C 分别置 done / 回 claim / 保持 running。

### 遗留（未替用户处理）

仓库工作区有未提交的 `progress.md` 和未跟踪的 `promo/`、`.workbuddy/artifacts/`、`.workbuddy/research-materials/`、本交接文档。
没有代为提交（超出授权范围）。改为在两份 prompt 里**明令禁止 `git add -A` / `git add .`**，只允许 add 本次实际改动的具体路径，避免污染 Verifier 的 diff 审计。
若要长期保留本交接文档，建议手动 commit 到 automation/i4-l2。

---

*第一~六节由福帮手在用户终止后编写。第七节由紫怡接手完成。*

---

## 八、2026-08-29 状态校正（Advancer tick #65）

> 本文件自 2026-08-19 起一直是未跟踪文件（`??`），随时可能因工作区清理丢失，故本 tick 入仓；同时校正第一/二/七节中已过期的信息。

| 项 | 本文件原文（已过期） | 2026-08-29 实际 |
|---|---|---|
| I4 进度 | I4-0 部分完成，其余待开始 | **I4-0~I4-9 全部 complete**；收官报告 `27f7fd5`，Verifier `5aebe97` 复验通过 |
| Key Decisions | Q1~Q5 已拍板待执行 | Q1~Q5 **全部落地**；已落地需求 = **R-19~R-23 + R-25**（+ Q5 出口 Gate）。**R-24 / R-26~R-29 是 parking-lot 冻结项，不是已交付能力**，见下方「机检证据」 |
| 最新 commit | `854a67f` | 见 `git log -1`（收官后仅治理提案类提交） |
| Advancer 自动化 ID | `5867270` | **`automation-1787109094822`**（第七节的两个 ID 已不存在，勿按 ID 找） |
| Verifier 自动化 ID | `5867281` | 旧 ID 已不存在，**当前有效 ID = `automation-1787109023265`**（「I4-验证（Verifier）：0-trust 独立检验」，ACTIVE，`FREQ=HOURLY;INTERVAL=1`）。轮次判定仍走第七节的 git log 尾标推导，机制不变 |
| valid_until | 2026-09-19 | **2026-08-31 23:59（Asia/Shanghai）**，到期自动停止 |
| eval 基线 | 19/19 PASS | 19/19 PASS，exit 0（2026-08-29 23:1x 复跑确认） |

#### 机检证据：已落地 vs parking-lot 冻结（2026-08-29 tick #68 一手复跑校正）

> 上一版写「Q1~Q5 全部落地（R-19~R-29）」，把 parking-lot 条目误记为已交付。以下为实跑结果，可复现：

```bash
python scripts/parking-lot.py --audit
# count=5，五条目 status 全部 "frozen"：
#   R-24 经验资产化      deps=[R-21]           signals=0
#   R-26 ACL 访问控制    deps=[R-21]           signals=0
#   R-27 全图影响分析    deps=[R-19]           signals=0
#   R-28 团队记忆        deps=[R-21, R-26]     signals=0  ← 因 R-26 未落地，T1 依赖就绪=False
#   R-29 多语言支持      deps=[R-22]           signals=0

grep -n "LANDED_FALLBACK" scripts/parking-lot.py
# LANDED_FALLBACK = {"R-19","R-20","R-21","R-22","R-23","R-25"}
```

**结论口径（请以本段为准）**

| 类别 | 需求编号 | 说明 |
|---|---|---|
| 已落地 | R-19 / R-20 / R-21 / R-22 / R-23 / R-25 | 由 `landed_set()` 机检确认；Q5 出口 Gate（`scripts/i4-gate.py`）同时落地 |
| parking-lot 冻结 | R-24 / R-26 / R-27 / R-28 / R-29 | `status=frozen`，**对外不得宣称"已规划交付"**；升级需 `scripts/parking-lot.py <root> --upgrade --id R-26 --impact "..." --budget "..."` 三要素齐全（缺一 exit 1）且四档触发之一命中 |

**为什么这条容易写错**：I4-9「文档交付」曾把 R-19~R-29 的**验收行**一次性补进 `docs/rpd-v2-technical-spec.md` §16.1——那是验收标准占位，不等于能力已实现。看需求是否落地，以 `parking-lot.py --audit` 与 `scripts/` 实际模块为准，不要以 spec 验收行的存在与否为准。

### 第二节 10 条 todo 的注意事项

自动化运行期间 WorkBuddy todo（`mcp__wb-issues__*`）工具**长期不可用**，这 10 条自 2026-08-20 起未再同步。
**真实进度一律以 `task_plan.md` 的 Phase Status 为准**，不要照抄第二节表格里的"待开始"。

### 到期前的两个未决治理项

见 `docs/automation-governance-proposal.md`（D1：自动化到期后停用 / 降频周观察 / 转 parking-lot 按需触发；D2：是否授权压缩 `progress.md` 的空转日志）。
两项均未拍板，自动化到期后需人工处理。

### L3

`task_plan.md` 中 L3 仍为 `planned`（冻结），不属于 I4 排期；升级条件走 `scripts/parking-lot.py` 四档触发机检。
