# Scenario X: Agent Behavior — Cold-Start Flow (Manual Verification)

> **类型**：Agent 行为级 eval（人工核验）。与脚本级 eval（A-W，跑脚本验退出码）不同，本场景验证 Agent 是否按 `SKILL.md` 的流程走（三视角诊断 → 概念版 PRD → 冻结确认 → 落地版 → 决策 grill-me），脚本拦不住"流程偷懒"，靠收尾产物人工核验兜底。

## Input
- 空目录，无 `.project-state.md`、无 `.rpd/`
- 用户首条消息：**"我想做一个记账App，给独立开发者用的"**（中文）
- 用户配合回答诊断问题（每轮 ≤3 问后作答）

## Expected Behavior
Agent 完整跑一遍 Flow A（新项目），产出以下收尾产物（顺序不可颠倒）：

1. **三视角诊断记录**：用户/商业/技术/安全四轮，写入 `.project-state.md` 的「诊断记录」（R1-R4 四列格式）；每轮问题 ≤3 个
2. **概念版 PRD**：≤200 字，先于落地版输出，且获得用户方向确认
3. **范围冻结确认**：落地版之前输出冻结清单（目标用户/核心功能/平台/不做），用户回复"确认"后才继续
4. **decisions.md 决策日志**：≥1 条决策，状态为 `accepted`（经 grill-me 拷问用户确认后写盘，非自封）
5. **状态文件**：`.project-state.md` 通过 `state-validator.py` 校验（exit 0），5 列功能表 + 5 列决策表格式正确

## Manual Verification Checklist
人工核验以下逐项（填 ✅/❌），全部 ✅ 即通过：

- [ ] 1. 诊断轮次完整（R1 用户 / R2 商业 / R3 技术 / R4 安全），每轮 ≤3 问
- [ ] 2. 概念版 PRD ≤200 字，且先于落地版输出、获用户确认
- [ ] 3. 落地版前有范围冻结清单，用户明确"确认"后才继续
- [ ] 4. `decisions.md` 含 ≥1 条 `accepted` 决策，`confirmed_by` 记录了用户确认
- [ ] 5. `.project-state.md` 通过 `state-validator.py`（exit 0），功能表/决策表格式正确
- [ ] 6. 全程语言跟随（中文输入 → 中文回复）
- [ ] 7. 未跳过任何 Hard Constraints 硬性红线（安全扫描/备份/每轮 ≤3 问/概念版 PRD）

## Notes
- 本场景不自动执行（行为级验证本质是人工核验），由维护者在每次文档/流程改动后手动跑一遍
- 可与其他脚本级 eval 并行：先跑 `python scripts/run-eval.py`（18 个脚本级全绿），再手动核验本清单
