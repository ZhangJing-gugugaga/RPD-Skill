# RPD Skill — Project Instructions

> 本文件是 RPD Skill 仓库的项目级指令，供 AI Agent 在此仓库中开发/维护本 skill 时使用。Claude Code 等工具进入本仓库时自动加载。**使用本 skill 做项目**请读 `SKILL.md`；本文只关乎"开发 RPD 本身"。

---

## 项目概述

RPD（Rapid Product Document）是一个 Agent Skill，覆盖项目全生命周期：新项目 → PRD 生成 → 半成品接手 → 继续开发。

**核心价值**：解决 Vibecoding 三大断裂点——需求断裂、上下文断裂、时间断裂。

**GitHub 仓库**：https://github.com/ZhangJing-gugugaga/RPD-Skill

---

## 代码规范

### Python 脚本

1. **编码**：所有脚本开头添加 Windows 编码修复（`sys.stdout.reconfigure(encoding="utf-8")`）
2. **路径**：输出使用 `.replace("\\", "/")`
3. **文件读取**：使用 `safe_read_file()` 防止 OOM
4. **Exit Code**：0=成功, 1=使用错误, 2=安全阻断, 3=校验失败, 4=Git 冲突

### SKILL.md

1. **中英双语**：所有标题、表格、提示中英对照
2. **体积**：≤8KB（R-05 硬约束），超限先压缩再提交
3. **Hard Constraints**：硬性红线，修改需谨慎
4. **脚本接入**：state-guard.py 和 prd-validator.py 必须在关键节点调用

---

## 修改后必须做的事

1. 运行 eval：`python scripts/run-eval.py`（18 个场景必须全过）
2. 保持中英双语
3. 等待用户批准后才能 push 到 GitHub

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0.0 | 2026-06-05 | 初始版本 |
| v1.1.0 | 2026-06-08 | 安全增强：SEC-001~007 |
| v1.2.0 | 2026-06-08 | 暖启动 + state-guard + prd-validator + intent-router |
| v1.3.0 | 2026-06-08 | SEC-001/002 修复 + Spec 漂移 + Git 并发 + Hard Constraints |
| v2.0.0 | 2026-08-03 | 主指标重构（M1/M2/M3）+ code-map 两层导航 + 取消停建 Gate + decisions.md grill-me + v1 兼容读取降级 + SKILL.md ≤8KB |
| v2.0.1 | 2026-08-03 | R-18 升级：state-guard 进程级物理锁防多 Agent 竞态覆写 |
| v2.0.2 | 2026-08-03 | README 身份中性化（任意 AI 工具）+ 删除平台插件目录（只留 .claude-plugin）+ intent-router 量词修复 + 文档并为一层半 |
