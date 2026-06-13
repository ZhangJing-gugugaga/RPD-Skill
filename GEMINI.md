# RPD Skill – Project Instructions

> 本文件是 RPD Skill 的项目级指令，供 Gemini CLI 在此项目中使用。

---

## 项目概述

RPD（Rapid Product Document）是一个 Gemini CLI Skill，覆盖项目全生命周期：新项目 → PRD 生成 → 半成品接手 → 继续开发。

**核心价值**：解决 Vibecoding 三大断裂点——需求断裂、上下文断裂、时间断裂。

**GitHub 仓库**：https://github.com/ZhangJing-gugugaga/RPD-Skill

---

## 目录结构

```
rpd/
├── .gemini-plugin/          # Gemini 插件配置
├── .claude-plugin/          # Claude 插件配置
├── .github/                 # GitHub 模板 + CI
├── .cursor-plugin/          # Cursor 插件配置
├── .codex-plugin/           # Codex 插件配置
├── .copilot-plugin/         # Copilot 插件配置
├── SKILL.md                 # 主控指令（中英双语）
├── GEMINI.md                # 本文件
├── CLAUDE.md                # Claude 项目指令
├── AGENT.md                 # Agent 交互指南
├── README.md                # 项目文档
├── 行为守则.md               # AI 行为守则
├── scripts/                 # 8 个确定性 Python 脚本
├── references/              # 知识库
├── eval/scenarios/          # 11 个评估场景
├── images/                  # 项目图片
└── assets/                  # 示例文件
```

---

## 脚本工具箱

| 脚本 | 用途 | 退出码 |
|------|------|--------|
| `intent-router.py` | 确定性意图分类 | 0/1 |
| `security-scanner.py` | 8 SEC 规则 + 路径遍历 | 0/1/2 |
| `project-scanner.py` | 技术栈检测 | 0/1 |
| `gap-analyzer.py` | 差距分析 + 决策漂移 | 0/1/3 |
| `state-validator.py` | 状态文件校验 | 0/1/3 |
| `state-guard.py` | 备份 + 原子写入 + Git 检查 | 0/2/3/4 |
| `prd-validator.py` | PRD 完整性校验 | 0/1/2 |
| `run-eval.py` | 11 个评估场景 | 0/1 |

---

## 代码规范

### Python 脚本

1. **编码**：所有脚本开头添加 Windows 编码修复
2. **路径**：输出使用 `.replace("\\", "/")`
3. **文件读取**：使用 `safe_read_file()` 防止 OOM
4. **Exit Code**：0=成功, 1=使用错误, 2=安全阻断, 3=校验失败, 4=Git 冲突

### SKILL.md

1. **中英双语**：所有标题、表格、提示中英对照
2. **Hard Constraints**：6 条不可违反的硬性红线
3. **脚本接入**：state-guard.py 和 prd-validator.py 必须在关键节点调用

---

## 修改后必须做的事

1. 运行 eval：`python scripts/run-eval.py`（11 个场景必须全过）
2. 保持中英双语
3. 等待用户批准后才能提交到 GitHub

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.6.2 | 2026-06-13 | 适配 Gemini CLI：新增 .gemini-plugin 和 GEMINI.md，修复 SKILL.md 元数据 |
| v1.3.0 | 2026-06-08 | SEC-001/002 修复 + Spec 漂移 + Git 并发 + Hard Constraints |
