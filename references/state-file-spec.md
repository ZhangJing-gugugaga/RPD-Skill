# 项目状态文件规范（.project-state.md）

## 概述

`.project-state.md` 是 RPD Skill 的核心持久化文件，记录项目的 PRD 摘要、功能进度、关键决策和阻塞项。它是跨 agent、跨会话的唯一真相来源。

## 文件格式

### YAML Frontmatter

文件必须以 YAML frontmatter 开头，用 `---` 分隔：

```yaml
---
name: my-project          # 必填，小写 kebab-case
created: 2026-06-05       # 必填，YYYY-MM-DD
last-synced: 2026-06-05T14:30:00  # 必填，ISO 8601
status: in-development    # 必填，planning|in-development|paused|completed
entry-type: new-idea      # 必填，new-idea|half-finished|continued
---
```

### 正文结构

正文使用标准 Markdown，包含以下章节：

1. **# 项目状态：[项目名]** — 标题
2. **## 一句话定义** — 产品核心定义
3. **## PRD 摘要** — 核心功能、排除项、商业模式、技术栈
4. **## 功能进度清单** — 表格形式的功能状态追踪
5. **## 关键决策记录** — 已做出的技术/产品决策
6. **## 当前阻塞项** — 待解决的问题
7. **## 技术栈** — 技术选型详情
8. **## 变更日志** — 状态文件的变更历史

### 功能进度清单格式

```markdown
| 功能 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| 功能名 | P0/P1/P2 | ✅ 已完成 / 🔨 进行中 / ⏳ 未开始 | 补充说明 |
```

### 状态标记规则

- ✅ 已完成：功能有完整实现，可正常使用
- 🔨 进行中：有部分代码但未完成
- ⏳ 未开始：PRD 中定义但无代码

## 更新时机

1. **初始化**：新项目流程完成 PRD 后自动生成
2. **接手项目**：半成品流程分析代码后自动生成
3. **手动更新**：用户说"更新进度"时，Agent 更新功能状态
4. **自动提醒**：开发完一个功能后，Agent 提醒用户更新

## 校验规则

状态文件必须通过 `state-validator.py` 的 JSON Schema 校验：
- 必填字段不可缺失
- status 必须是 planning/in-development/paused/completed 之一
- entry-type 必须是 new-idea/half-finished/continued 之一
- 日期格式必须正确
