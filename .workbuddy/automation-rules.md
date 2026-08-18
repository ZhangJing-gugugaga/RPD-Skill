# RPD-skill 自动化任务规则（Advancer + Verifier）

> 适用于 `automation/i4-l2` 分支上的双 Agent 串行自动化。
> 创建于 2026-08-19 · 模型：推进 reasoning / 验证 default

---

## 通用规则（两个 Agent 共同遵守）

1. **入口**：每次启动先读 `task_plan.md`（当前阶段）→ `progress.md`（Test Results + 最近会话）→ `findings.md`（资产台账 + 决策）。
2. **分支**：只在 `automation/i4-l2` 分支工作；**永不触碰 main**；**永不 push**（本地 commit 仅限 automation 分支）。
3. **红线（8 条，零例外）**：
   - 不 push 除非用户明确同意
   - main 受保护，实施在 automation/i4-l2
   - 测试 0 failed 才 commit（`python scripts/run-eval.py` 必须 19/19 PASS）
   - 视觉验证必须真实截图（禁 mock 注入）
   - 信息不全先记录到 findings.md，不瞎猜
   - 预算守卫不破：router ≤3k / 单条 code-map ≤300 token
   - R-10 向后兼容：版本白名单 + 降级处理
   - 红线机检 + 三级信任持续有效
4. **计划文件权限**：`task_plan.md` 的 Phase 状态标记由 Verifier 更新（验证 PASS 后标 complete）；两个 Agent 均不得修改计划的 Goal/决策/Phase 结构——那是用户的权限。
5. **Key Decisions 已拍板**（见 task_plan.md §Key Decisions）：Q1–Q5 均有明确结论，实施时直接执行，不再追问。

---

## Advancer（推进 Agent）规则

**模型**：reasoning
**Skill**：planning-with-files
**写入范围**：`scripts/` `docs/` `references/` `eval/` `progress.md`（记录做了什么）
**禁止写入**：`task_plan.md`（结构/决策）、`findings.md`（仅追加 Issues）、main 分支

### 工作流程
1. 读三件套，确认当前 pending 的下一个 I4 模块
2. 按 `task_plan.md` 中该 Phase 的「涉及文件」和检查清单实施
3. 实施完成后本地运行 `python scripts/run-eval.py`，必须 19/19 PASS
4. PASS 后 `git add` + `git commit -m "feat(I4-N): R-XX 描述 [advancer]"`
5. 更新 `progress.md` 记录本次实施内容
6. 如果某个 Key Decision 导致无法继续，**停下来写报告到 progress.md**，不要猜
7. 如果 eval FAIL，**不要 commit**，记录错误到 progress.md 并停止

### 禁止行为
- 不修改 `task_plan.md` 的结构、Goal、决策、Phase 定义
- 不跳过 Phase 顺序
- 不同时推进多个模块（严格串行）
- 不 push 到远程
- 不触碰 main 分支
- 不引入外部依赖（Q1 决策：零外部依赖先行）

---

## Verifier（验证 Agent）规则

**模型**：default
**Skill**：planning-with-files
**写入范围**：`progress.md`（Test Results + 验证报告）、`findings.md`（Issues）、`task_plan.md`（仅 Phase 状态标记：pending → complete）
**禁止写入**：`scripts/` `docs/` `references/` `eval/`（代码只读）

### 0-trust 验证清单（7 项，每次必跑）

| # | 检查项 | 命令/方法 | PASS 标准 | FAIL 动作 |
|---|--------|----------|----------|----------|
| 1 | eval 全量 | `python scripts/run-eval.py` | 19/19 PASS, exit 0 | revert |
| 2 | git diff 审计 | `git diff HEAD~1 --stat` + 逐文件审查 | 仅预期文件被改 | revert |
| 3 | 预算守卫 | 检查 router token / 单条 code-map token | router ≤3k / 单条 ≤300 | revert |
| 4 | 红线机检 | 检查三级信任 + stale 检测逻辑 | 不回归 | revert |
| 5 | 向后兼容 | 检查 R-10 版本白名单 + 降级路径 | 不崩 | revert |
| 6 | 计划一致性 | task_plan.md Phase 状态 vs 实际 | 一致 | 标记 mismatch |
| 7 | 无 mock 注入 | 检查视觉/UI 改动 | 有真实数据/截图 | revert |

### 工作流程
1. 读 `task_plan.md`，确认刚完成的模块及其验收标准
2. **不读 Advancer 的对话记录**——只看 git diff + eval 输出 + 文件内容
3. 逐项跑 7 项检查
4. 全 PASS → 在 `task_plan.md` 标记该 Phase 为 complete；在 `progress.md` Test Results 写入验证记录
5. 任一 FAIL → `git revert HEAD` 撤销上一个 commit；在 `progress.md` 写入 FAIL 报告；在 `findings.md` Issues 记录问题
6. FAIL 后该模块回到 pending，下一个 Advancer tick 重做

### 禁止行为
- 不读 Advancer 对话（0-trust 原则）
- 不修改任何代码文件
- 不自己实现功能
- 不 push
- 不跳过任何检查项

---

## 串行节奏

```
T+0h   Advancer 启动 → 实现模块 N → commit → 结束
T+1h   Verifier 启动 → 7 项检查 → PASS 标 complete / FAIL revert → 结束
T+2h   Advancer 启动 → 实现模块 N+1 → ...
  ...  直到 I4-0~9 全部 complete
```

- 严格串行：Advancer 结束后 Verifier 才启动，反之亦然
- 每个模块目标 2h（1h 推进 + 1h 验证）
- Verifier FAIL → 模块回 pending → 下个 Advancer tick 重做（不跳过）
- 连续 3 次 FAIL 同一模块 → 暂停，写报告等人工介入

---

## 模块清单（I4-0 ~ I4-9）

| 模块 | 内容 | Advancer 实现 | Verifier 重点 |
|------|------|--------------|-------------|
| I4-0 | 基线核对（部分完成） | 通读规格 / 盘点脚本 / 起草 R-19~R-25 编号 | 文档一致性 |
| I4-1 | R-22 混合检索 | BM25+RRF 双通道，向量打标 TODO | eval + 预算 |
| I4-2 | R-19 边信息 | edges schema + R-10 映射 + 查询能力 | eval + 兼容 |
| I4-3 | R-25 依赖锁定 | 依赖清单 + commit/指纹 + 漂移检测 | eval + 红线 |
| I4-4 | R-20 PRD↔代码影响 | impact-analyzer.py + 双向映射 | eval + 回退 |
| I4-5 | R-23 渐进式暴露 | 三层暴露 + 双预算守卫 | eval + 预算 |
| I4-6 | R-21 L0-L3 分层记忆 | 分层读写 + 过期规则 + 检索回退 | eval + 膨胀控制 |
| I4-7 | parking-lot 治理 | 四档触发 + 升级三要素 + 条目登记 | 触发条件可机检 |
| I4-8 | 测试与验证 | eval 基线对比 + M1/M2 Gate + 回归 | 0-trust 全量 |
| I4-9 | 文档与交付 | 更新规格/SKILL/usage + 经验沉淀 + 交付清单 | 文档与实现一致 |
