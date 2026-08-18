# Findings & Decisions — RPD-skill 整体生命周期

> planning-with-files 外部记忆库。随生命周期推进持续更新。
> 本文件 = 研究结论（沿用）+ **资产台账（Asset Inventory）** + 生命周期上下文。

---

## 现有资产台账（Asset Inventory）— 截至 2026-08-19

> 全量盘点 RPD-skill 仓库当前所有交付物与过程物。状态：活跃=产品组成部分；过程物=开发/研究痕迹。

### A. 核心产品交付物（根目录）
| 资产 | 用途 | 生命周期阶段 | 状态 |
|------|------|-------------|------|
| `SKILL.md` | 主控指令（≤8KB 双语，10 条红线，Flow A/B/C + v2 code-map） | L0→L1 持续 | 活跃 |
| `README.md` | 项目总览 / 安装 / 架构 / 安全引擎 / 评估矩阵 / FAQ | L0→L1 持续 | 活跃 |
| `CLAUDE.md` | 开发项目指令（代码规范 / 版本史 v1.0–v2.0.2） | L1 建立 | 活跃 |
| `TRAINING.md` | RPD 专家训练配方 v1.2（12 章节 + 文件读取顺序） | L1 建立 | 活跃 |
| `LICENSE` | MIT | L0 | 活跃 |
| `_user_meta.json` | 用户元数据 | — | 活跃 |

### B. 运行时脚本（scripts/ — 12 个 .py）
| # | 脚本 | 确定性断言机制 | 阶段 | 状态 |
|---|------|---------------|------|------|
| 1 | `intent-router.py` | 正则关键词硬路由 + 成熟度分类 | L0（v1.2.0） | 活跃 |
| 2 | `security-scanner.py` | 8 SEC + 注入 + 流式扫描 | L0（v1.1.0） | 活跃 |
| 3 | `project-scanner.py` | 技术栈 / 组件 / 路由 / TODO | L0 | 活跃 |
| 4 | `gap-analyzer.py` | PRD vs 代码 + 决策漂移 + Next.js | L0（v1.3.0） | 活跃 |
| 5 | `state-validator.py` | YAML Frontmatter JSON Schema 校验 | L0（v1.2.0） | 活跃 |
| 6 | `state-guard.py` | 原子写 + 备份 + 分支锁 + R-18 物理锁 | L0（v1.2.0）→ L1（v2.0.1） | 活跃 |
| 7 | `prd-validator.py` | PRD 完整性 + `--ai-mode` 8 区块 | L0（v1.2.0） | 活跃 |
| 8 | `run-eval.py` | 19 个评估场景 | L1（v2.0.0） | 活跃 |
| 9 | `rpd-cold-start.py` | v2 冷启动 7 步 + v1 兼容读取 | L1（v2.0.0） | 活跃 |
| 10 | `code-map-generator.py` | code-map 三件套（tree-sitter + 正则） | L1（v2.0.0） | 活跃 |
| 11 | `rpd-decisions.py` | decisions.md 决策日志（grill-me 前置） | L1（v2.0.0） | 活跃 |
| 12 | `rpd-metrics.py` | M1/M2/M3 主指标采集 | L1（v2.0.0） | 活跃 |
| — | `scripts/__pycache__/*.pyc` | 编译缓存 | — | 忽略（按需重建） |

### C. 文档（docs/ — 3 .md）
| 资产 | 用途 | 状态 |
|------|------|------|
| `docs/rpd-v2-technical-spec.md` | v2 技术规格书（17 节 + 附录 A 需求池 R-01~R-18 / 附录 B） | 活跃（L2 待扩展 R-19~R-25） |
| `docs/rpd-v2-usage.md` | v2 使用规格（冷启动 7 步 / 红线机检 / 审核视图 / 小仓库标准） | 活跃 |
| `docs/research-report-ua-tam-optimization.md` | I4 深度研究报告（537 行，26 参考文献，5 章） | L2 权威依据 |

### D. 参考与模板（references/ — 6 件）
| 资产 | 用途 | 状态 |
|------|------|------|
| `brainstorming-flow.md` | 三视角诊断 4 轮问题清单 + 概念/落地版入口 | 活跃 |
| `prd-template.md` | PRD 模板（概念版 + 落地版 + AI 增强 8 区块） | 活跃 |
| `state-file-spec.md` | 状态文件规范（5 列功能表 / 5 列决策表 / 4 列诊断表） | 活跃 |
| `state-schema.json` | 状态文件 JSON Schema | 活跃 |
| `keyword-map.json` | 中英文关键词映射（50+ 条目，gap-analyzer 用） | 活跃 |
| `rpd-v2-layout.md` | .rpd/ 目录规格（双层落点 + 全动态路径 + 迁移） | 活跃 |

### E. 评估（eval/ — 19 场景）
- **独立场景 .md（5）**：`empty-project.md`(A) / `corrupted-state.md`(B) / `prompt-injection.md`(C) / `half-finished.md`(D) / `cold-start-flow.md`(S)
- **run-eval.py 内联断言（12）**：E 意图路由 / F PRD 校验 / G 决策漂移 / H 状态守卫 / I SEC 规则 / O 中文名 / P Turbo / Q AI PRD / R 模板 / T v2 决策 / U v2 code-map / V v2 主指标 / W v2 物理锁
- **行为级（1）**：X Agent 行为人工核验
- **合计 19 场景**；README 记为 19，TRAINING.md 记为 18/18（口径差异待 L2 Phase 0 复跑核对）

### F. 资产与推广（assets/ · promo/）
| 资产 | 用途 | 状态 |
|------|------|------|
| `assets/hero.png` | README 首图 | 活跃 |
| `assets/example-state.md` | 示例状态文件 | 活跃 |
| `promo/社区文案-v1.md` | 社区推广文案 v1 | 活跃 |
| `promo/社区文案-v2-人性化.md` | 社区推广文案 v2（人性化） | 活跃 |

### G. 分发元数据（.claude-plugin/ · .github/）
| 资产 | 用途 | 状态 |
|------|------|------|
| `.claude-plugin/plugin.json` | 插件元数据（name/version/description） | 活跃 |
| `.claude-plugin/marketplace.json` | marketplace 分发描述 | 活跃 |
| `.github/FUNDING.yml` | 赞助 | 活跃 |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug 模板 | 活跃 |
| `.github/ISSUE_TEMPLATE/feature_request.md` | 功能模板 | 活跃 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR 模板 | 活跃 |
| `.github/workflows/eval.yml` | CI 评估工作流 | 活跃 |

### H. 规划与研究过程物（.workbuddy/ · logs/ · 根目录三件套）
| 资产 | 用途 | 状态 |
|------|------|------|
| `task_plan.md` / `findings.md` / `progress.md` | 本生命周期计划三件套（planning-with-files） | 活跃 |
| `.workbuddy/research-materials/` | I4 研究报告草稿/审稿/修订（ch1-5 + 引言/结论/目录，10+ 文件） | 过程物 |
| `.workbuddy/artifacts/RPD-skill-审查报告-2026-08-18.md` | 2026-08-18 审查报告 | 过程物 |
| `.workbuddy/memory/2026-08-18.md` · `2026-08-19.md` | 每日记忆 | 过程物 |
| `.workbuddy/assemble_report.py` | 报告汇编脚本 | 过程物 |
| `logs/` | subagent/session 事件 json + debug log（10 json + 1 log） | 过程物 |

---

## Requirements（用户需求）
- 使用 planning-with-files 把 RPD-skill 配置为**整体生命周期**管理：计划 + 任务 + 已有资产。
- 此前已深度调研 UA / TAM 两仓库，产出 I4 研究报告中含 R-19~R-29 需求池与三支柱方向。
- 用户已确认三项决策（grill-me）：A. 采纳排期 I4 六条 P1；B. 认可 parking-lot 触发条件；C. 认可三支柱长期架构。
- 硬性约束：不 push 除非明确同意；main 受保护；测试 0 failed 才 commit；视觉验证禁 mock；信息不全先提问。

## Research Findings（研究结论，详见 docs/research-report-ua-tam-optimization.md）

### Understand-Anything（UA）核心机制
- 结构确定性（Tree-sitter）+ 语义灵活性（LLM）双轨；结构层可复现、可机检、可指纹增量。
- 7 阶段流水线（5 专职 Agent + 编排器 SAVE 收尾），中间产物 JSON 独立可重跑；"部分结果优于无结果"。
- knowledge-graph.json：节点 16 种、边 35 种 / 8 大类 + 权重约定（contains 1.0 / calls 0.8 / imports 0.7 / depends_on 0.6…）；Zod 4 层校验；commit hash + 结构指纹过期检测。
- /understand-diff：changedNodes / affectedNodes(1-hop) / affectedLayers / blast radius 风险分级 → PRD 变更影响分析范式。
- /understand-domain：技术符号 → 业务语言聚类映射 → 需求↔代码双向映射范式。

### TencentDB-Agent-Memory（TAM）核心机制
- L0-L3 分层记忆（原始对话 → 原子 → 场景 → 画像）+ "提取-聚合-蒸馏"异步流水线；低层存证据、高层存结构。
- 分层检索：L2/L3 快速引导 + BM25 + 向量 + RRF 回退 L1/L0 + 三重预算（条目数/字符/超时）。
- 四类资产：Chat Memory / Skill（含版本、触发边界、验证规则）/ LLM-Wiki / CodeGraph。
- 治理：Fixed Binding + ACL"先过滤后检索"、默认私有、版本锁定、MemoryProxy 零代码接入。
- 官方自报数据（Token -61.38%、PersonaMem 48%→76%）无第三方复现，作方向性参考。

### RPD v2 现状（docs/rpd-v2-technical-spec.md）
- code-map 双层：router.json 常驻 ≤3k / code-map.json 按需单条 ≤300 token；红线机检 + 三级信任（verified/unverified/stale）；decisions.md 决策日志；审核视图五区块；R-10 兼容读取 UA knowledge-graph.json。
- 12 启发点覆盖：已覆盖 4（1/2/3/7）、半覆盖 3（10/11/12）、未覆盖 5（4/5/6/8/9）。
- 差距归因四分法：数据模型差异 2（启发 4/6）/ 技术路径差异 1（启发 12）/ 范围超限 3（启发 5/8/9）/ 资源约束 2（启发 10/11）。
- 薄弱点：跨会话记忆层级不足、检索策略单一、经验未资产化、无 PRD↔代码影响分析、数据模型未图化。

### I4 增量需求池（R-19~R-29）
- I4(P1) 六条：R-19 边信息复用 / R-20 PRD↔代码影响分析 / R-21 L0-L3 分层记忆 / R-22 混合检索 BM25+RRF / R-23 渐进式暴露 / R-25 依赖版本锁定。
- parking-lot 五条：R-24 经验资产化 / R-26 ACL / R-27 全图影响（2-hop+）/ R-28 团队记忆 / R-29 多语言。
- ROI 排序：P1-a（R-22、R-19）→ P1-b（R-20、R-25、R-23）→ P1-c（R-21）。
- 风险对策：token 预算、向后兼容（R-10 版本白名单+降级）、图谱膨胀与过期、对外口径（不宣称"同源等价"）。

## Technical Decisions（项目级 Charter）

| Decision | Rationale |
|----------|-----------|
| I4 落序 R-22+R-19 → R-25 → R-20/R-23 → R-21 | 报告 §4.6 ROI；R-20 依赖 R-19 边质量 |
| parking-lot 冻结 + 四档触发条件 | 用户决策 B |
| 三支柱不排期、为长期方向 | 用户决策 C |
| 混合检索零外部依赖先行（BM25+RRF），向量打标 | 务实主义，避免过度工程化 |
| R-19 边仅复用 R-10 knowledge-graph.json，不自建 AST 管线 | 规避自建全量解析 |
| 预算守卫 / 向后兼容 / 红线机检三条硬约束不破 | 规格硬约束 |
| 生命周期计划升级：I4-only → L0–L3 全景 | 用户要求"整体生命周期"；I4 细节保留为活跃子阶段 |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| 研究阶段：Ch2 论文归属误述 | round1 审稿 REVISE → 修订移除 → round2 PASS |
| 研究阶段：Ch3 差距归因三处口径不一致 | round1 审稿 REVISE → 四分法统一、总数=8 |
| 研究阶段：parkin-lot 笔误 | 统稿修复 |
| 研究阶段：patch 指令未执行 | lead 直接对终稿最小化 Edit 清理 |
| 生命周期重构：原 plan 仅 I4 范围，缺资产台账与历史阶段 | 升级为 L0–L3 全景 + findings.md 资产台账 |

## Resources
- 研究报告（终稿）：`docs/research-report-ua-tam-optimization.md`（537 行，26 参考文献）
- RPD v2 技术规格：`docs/rpd-v2-technical-spec.md`
- RPD v2 运行参考：`docs/rpd-v2-usage.md`
- 关键脚本：`scripts/`（12 个，职责见 §B 台账）
- 研究过程物：`.workbuddy/research-materials/`
- UA 仓库：https://github.com/Egonex-AI/Understand-Anything
- TAM 仓库：https://github.com/TencentCloud/TencentDB-Agent-Memory

---

*Update after every 2 view/browser/search operations — 2-Action Rule*
