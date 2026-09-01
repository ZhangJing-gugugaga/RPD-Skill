# RPD-Skill v3 升级计划书（最终版）

> 状态：执行中 · 分支：`upload` · 制定日期：2026-09-02
> 依据：全仓库批判性审查（P0×5 / P1×11 / P2×12）+ 三轮社区调研（Agent 记忆方案、插件生态、代码索引技术选型）
> 调研结论：hooks 强制层是官方正解；`commit+file:line` 可机器验证锚点为领先业界的差异化设计；tree-sitter 采用聚合包；语义层必须绑定指纹防腐。

## 0. 设计决策（已确认）

| 决策点 | 结论 | 依据 |
|---|---|---|
| 解析哲学 | 混合式：结构层确定性（tree-sitter/正则），语义层由宿主 Agent 填写并落盘缓存 | understand-anything 验证 |
| 记忆分层 | 文件版 L1/L2 轻量分层，不引入服务/向量库 | 腾讯 L0-L3 思想 + skill 定位 |
| v1 收敛 | `.rpd/` 唯一真相源，v1 自动迁移后冻结 | 审查 P0 级双轨混乱 |
| 交付节奏 | 四阶段，每阶段独立可发布、eval 全绿 | 风险控制 |
| 记忆加载 | 索引模式：active-context ≤200 行当索引，子文件按需读 | Cline 全量读已被证伪 |
| 落盘保障 | hot path 同步写（SKILL.md 流程内）+ Stop hook 兜底 + PreCompact 快照 | Claude Code 官方分工 |
| 决策日志 | 写时对账四算子（ADD/UPDATE/DELETE/NOOP）替代 append-only | mem0 arXiv:2504.19413 |

## 1. 阶段 1 — P0 修复 + 多语言 code-map（发布 v2.3）

### 1a. code-map 语言注册表重构（P0-1：非 C/C++ 项目 code-map 为空）
- `code-map-generator.py` 硬编码 C 逻辑重构为 `LANG_REGISTRY`：首批 **Python、JavaScript/TypeScript、Java、Go、Rust、C#**（C/C++ 保留）。
- tree-sitter 优先走 **tree-sitter-language-pack** 聚合包（371 语言、abi3 wheel、按需惰性下载；aider 生产验证），extras：`rpd-skill[code-index]`；锁 `tree_sitter>=0.23`（0.23 起Language capsule 化、`set_language` 移除）。
- **C# grammar 为 ABI 15**：探测到旧 core 自动降级正则，降级规则写进代码而非假设。
- 每语言零依赖正则兜底：花括号块与缩进块（Python）双模式、方法归属类的启发式、文档注释风格（`#`/`//`/`/**`）、通用调用提取。兜底定位 = grep 级定位 + 最小定义识别（社区 "just grep" 派的务实共识）。
- 不采用 ctags（需外部二进制且无引用边，aider 已弃用）与 ast-grep（外部 CLI，不做库内依赖）。

### 1b. 混合式语义层（防腐化三原则）
- 新增 `scripts/code-map-enrich.py`：从结构事实生成 LLM 填写提示词（`.rpd/enrich-prompt.md`），宿主 Agent 填写模块摘要/架构分层（API/Service/Data/UI/Utility），落盘 `.rpd/code-map.semantic.json`。
- **防腐三原则**：①结构层唯一事实源，语义层纯派生缓存；②每条摘要绑定源文件内容 hash + 符号路径外键 + 生成时间戳 + 模型名；③按文件粒度增量失效，加载时悬空摘要（符号已不存在）丢弃；语义缺失时结构层自洽可用。
- **语义摘要不进 router ≤3k 常驻预算**，只进懒读取层。
- router 排序：v1 沿用简单裁剪；TODO(v2)：aider 式按引用频次排序、超预算先丢低分。

### 1c. P0 修复
- `state-schema.json` 补 `branch-affinity`/`last-commit-sha` 字段（修复 branch-affinity 防覆盖锁永远无法通过校验的死代码问题 P0-2）。
- `security-scanner.py` 分级：仅 CRITICAL exit 2 阻断；HIGH/MEDIUM/LOW 警告放行（修复 `.env` 存在即常态阻断 P0-3）；注入 pattern 补中文（P1-8）；`.rpd/*.md` 纳入默认注入扫描。
- Flow C 与冷启动统一先读 `.rpd/active-context.md`（v1 只读兼容，铺路阶段 3）。

## 2. 阶段 2 — hooks 强制层（发布 v2.4）

### 2a. rpd-hook-bridge.py（纯 stdlib，唯一 hook 入口）
- `session-start`：探测 `.rpd/active-context.md` / `.project-state.md` → 输出 **`additionalContext` JSON**（官方推荐结构化方式，非裸 stdout）；内容 ≤1-2k 字符（10k 硬上限），索引式注入 + 恢复指引；matcher 覆盖 `startup|resume|clear|compact` 并解析 `source`（compact 后全量重注入）；非 RPD 项目输出 `{"suppressOutput": true}` 静默退出；`RPD_HOOKS_DISABLED=1` 逃生开关。
- `stop`：fingerprint 机检（源码改动未落盘）→ **additionalContext 温和续跑**（不用 decision:block，避免打断用户）；必须检查 `stop_hook_active` 防递归；会话内最多 3 次（计数器放 `${CLAUDE_PLUGIN_DATA}`），之后只告警。
- **stdout 纪律（claude-mem 翻车史）**：禁 ANSI 色码/调试输出进 stdout，日志走文件；Windows 强制 `PYTHONIOENCODING=utf-8`（GBK 控制台防炸）。

### 2b. hooks/hooks.json
- `type: "process"` exec 形式（官方 Windows 推荐，绕开 PowerShell 占位符重写）；注册 SessionStart + Stop；Claude Code / ZCode 双宿主通用。
- Claude Code 专属 PreCompact 提醒放 README 可选片段（ZCode 无此事件）。

### 2c. 激活与路由修复
- SKILL.md description 重写：第三人称 MUST/SHOULD + 中英双语触发词清单（650 会话实验证明 20 倍激活提升）。
- UserPromptSubmit 路由 hook 兜底（复用 keyword-map.json）。
- intent-router：continue 触发词以状态文件存在为前置（P1-2）；confidence=medium 允许 Agent 覆盖。
- 冷启动提速：`map_commit == HEAD` 跳过全量 sha256（P1-3）。
- Flow C 轻量 fast path：改一行代码场景跳过 security/gap 全扫描（P1-4）。
- state-guard：超时/锁异常捕获（exit 4）、porcelain 按字段解析（P1-5/P2-1）。
- 降级路径：`references/agents-bootstrap-snippet.md` + README 三档能力说明。

## 3. 阶段 3 — 记忆分层 v3（发布 v3.0，MAJOR + CHANGELOG）

- **v1 收敛**：`--migrate` 自动迁移 v1→v2 并归档冻结（`.project-state.md.migrated`）；Flow C、gap-analyzer、run-eval 全部去 v1。
- **L2 场景层**：active-context ≤200 行硬上限，超限触发整理；进度表与 code-map entry 对账机检，长期不动自动标 stale（修 P1-6 进度表腐化）。
- **L1 事实层**：decisions 写时对账四算子；每条锚定 `commit+file:line` + confidence + modified 时间戳；**Stop hook 脚本化校验锚点，代码已变则置信度自动降级**（差异化核心）；超限归档 = 摘出索引保留原文（mem0 存储/检索分离）。
- **知识沉淀层**：`.rpd/knowledge.md` 硬上限；只允许沉淀"代码读不出来"的内容（踩坑/跨文件因果/调参经验），明文禁止复抄可推导内容；与 Claude Code Auto Memory 划界（git 可提交、跨工具可移植、结构化锚定）。
- 状态文件带 `schema_version`，脚本入口运行时迁移（官方无安装期钩子，绝不删用户数据）。
- 移除 gap-analyzer 硬编码私人词表（P1-11）→ 项目级 `.rpd/keyword-map.json`；多 worktree 场景文档声明（P1-7）。

## 4. 阶段 4 — eval 行为级重建（发布 v3.1）

- 场景 X 恒通过问题改为真行为断言；补关键回归：branch-affinity 锁端到端、stale 状态冷启动、v1 迁移幂等、空/损坏 `.rpd/` 容错、hooks bridge 三模式（含 Windows GBK 输出）、6 门语言 fixture 符号提取、语义层 fingerprint 失效。
- 文档数字对齐（P1-10）：plugin.json 版本、红线计数、阈值口径、场景计数、死链命令。
- README/SKILL.md 同步 v3：分层记忆图、hooks 接线指南、语言覆盖表、调用边懒加载用法（"查 callers 用 code-map 而非 grep"——索引被绕过是社区验证的最大采纳瓶颈）。

## 5. 明确不做

常驻服务/向量库/BM25 混合检索；硬拦截；每次 Edit 自动写状态；dashboard/web 界面；ctags/ast-grep 依赖；首批超 6 门新语言；Cline 式六文件全家桶；与 Claude Code Auto Memory 竞争而非共存。

## 6. 调研来源（关键）

- Claude Code Hooks/Plugins/Memory 官方文档；mem0 论文 arXiv:2504.19413；aider repo-map 与 ctags 弃用；understand-anything（Egonex-AI）；claude-mem hooks 架构与 issue #519/#621/#1253；tree-sitter-language-pack（PyPI）；Letta Memory Blocks；Cline Memory Bank 及其失败模式批评；HN CodeRLM 讨论（索引 vs "just grep"）。
