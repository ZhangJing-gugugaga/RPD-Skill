# 自动化治理提案（I4 收官后）

> 生成时间：2026-08-29 15:1x（tick #62 · I4 Advancer）
> 固化时间：2026-08-29 16:1x（tick #63 · I4 Advancer）→ 已 commit 入 `automation/i4-l2`，交 Verifier 复验
> 适用对象：automation-1787109094822「I4-推进（Advancer）」
> 状态：**待张敬拍板**（本文档只提方案，不擅自改配置）

---

## 一、现状（事实，非判断）

| 项 | 值 |
|---|---|
| 自动化 ID | `automation-1787109094822` |
| 调度 | `FREQ=HOURLY;INTERVAL=1`（全周 7 天，每小时 1 次） |
| 有效期 | 2026-08-18 ~ 2026-08-31 |
| 分支 | `automation/i4-l2` |
| 可推进模块 | **0**（task_plan.md 中 I4-0~I4-9 全部 `complete`） |
| 冻结项 | Phase L3 状态 `planned`，触发条件「用户信号 / 成本收益翻转 / 依赖就绪 / 定期复核」四档均未满足 |
| 空转次数 | 自 tick #17（2026-08-21）起连续 47 次零产出（#62 产出本文档，#63 将其 commit 固化） |
| 最近一次有效交付 | tick #15 · `27f7fd5` I4 收官报告（Verifier `5aebe97` 复验通过） |
| 基线健康度 | `python scripts/run-eval.py` = **19/19 PASS，exit 0**（A~X 全过） |

**结论**：本自动化已经「跑完了它的全部工作」。每小时仍在触发，但每个 tick 只能做同一件事——复跑 eval 确认 19/19，然后终止。

---

## 二、三个选项（推荐 A）

### A. 停用本自动化（推荐）

- 动作：`automation_update(mode="update", id="automation-1787109094822", status="PAUSED")`
- 理由：目标已达成，继续运行只有 token 成本，零边际产出；L3 需要的是**用户决策**（是否进入新迭代），不是机器空转
- 代价：无。仓库状态已固化在分支上，随时可恢复
- 恢复方式：L3 有排期时改回 `ACTIVE` 即可

### B. 降频为「每周观察任务」

- 动作：rrule 改为 `FREQ=WEEKLY;BYDAY=MO;BYHOUR=10`
- 价值：保留「有人定期看一眼基线是否劣化」的能力，成本降到 1/168
- 适用：你想保留每周一次的 eval 健康巡检
- 注意：这本质上是把 Advancer 改造成了 Monitor，prompt 需要同步重写（从「推进下一个模块」改为「跑 eval + 报告基线」）

### C. 绑定到 parking-lot 四档触发

- 动作：停用当前自动化，改为 parking-lot 条目升级时手工创建一次性任务
- 价值：完全按需触发，零空转
- 前提：需要有人盯 parking-lot（见 `scripts/parking-lot.py` 的四档机检）

---

## 三、治理债：progress.md 空转日志压缩（需单独授权）

**问题**：progress.md 现 539 行，其中 tick #17~#62 共 46 条空转日志约 300+ 行（占文件 ~60%），内容高度重复，已淹没有效信息。

**压缩方案**（一次性执行，不改任何代码）：

1. 删除 tick #17~#61 的 45 条重复日志
2. 替换为单条汇总记录，保留以下字段：
   - 时间区间：2026-08-21 ~ 2026-08-29
   - tick 编号区间：#17 ~ #61（共 45 次）
   - 共同结论：I4-0~I4-9 全 complete；L3 planned 冻结；eval 每次均为 19/19 PASS
   - 累计建议：停用或降频
3. 保留全部**有效**日志（tick #1~#16 的真实交付记录 + 收官报告 + Error Log + Test Results）

**预期效果**：progress.md 从 539 行降到约 250 行，恢复可读性。

**风险**：属历史改写（虽然是本地未提交的 `M progress.md`），Verifier 无法复验——需张敬明确授权，我会在授权后单 tick 执行并 commit。

---

## 四、需要张敬的一句话决策

| # | 决策点 | 选项 |
|---|---|---|
| D1 | 本自动化怎么处理？ | A 停用 / B 降频为周观察 / C 转按需触发 / 维持现状 |
| D2 | progress.md 空转日志是否压缩？ | 授权压缩 / 保持原样 |

给出选项字母即可（例：「A + 授权压缩」），我下一 tick 执行。

---

## 五、已执行的自我改进（tick #63，无需授权）

**问题**：每 tick 往 `progress.md` 追加一段空转日志 → 项目交付文件持续膨胀（539 行 → 551 行），且因未授权压缩而长期无法提交，反过来又污染 Verifier 的 diff 审计。

**本 tick 起生效的约束**（Advancer 自我约束，不触碰任何计划结构）：

| 内容 | 归属 | 频率 |
|------|------|------|
| 每小时 tick 运行记录（闸门/模块/eval/commit） | `.workbuddy/automations/<id>/memory.md` | 每 tick |
| 真实交付（模块实现、文档、报告） | `progress.md` | 仅当产出时 |
| 空转状态声明 | `progress.md` 单行（≤3 行） | 每 tick（替代原 6 行段落） |

**效果**：`progress.md` 停止无意义膨胀；tick 粒度痕迹不丢，只是移到自动化运行日志这一它本该待的位置。

---

## 六、未改动承诺

- tick #62：除新建本文档外，**未改动任何仓库文件、未 commit、未 push、未触碰 main**。
- tick #63：仅 commit 本文档（`git diff --cached --stat` = 1 file changed, 102 insertions，无其他文件入 diff），eval 19/19 PASS 后提交；`progress.md` 的历史空转日志**未**纳入本次提交（待 D2 授权后统一处理），未 push、未触碰 main。
