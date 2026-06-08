<h1 align="center">⚡ RPD — Rapid Product Document</h1>

<p align="center">
  <strong>智能体确定性认知工程学外骨骼 — 跨会话长周期全生命周期状态机</strong>
  <br />
  <em>Deterministic cognitive exoskeleton for AI agents — cross-session, full-lifecycle state machine.</em>
</p>

<p align="center">
  <a href="https://github.com/ZhangJing-gugugaga/RPD-Skill/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-UNLICENSED-red" alt="License" /></a>
  <a href="https://docs.anthropic.com/en/docs/claude-code"><img src="https://img.shields.io/badge/Claude_Code-8A2BE2" alt="Claude Code" /></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-00c853" alt="Quick Start" /></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Runtime-8__stdlib__Python-yellow" alt="8 stdlib Python" /></a>
  <a href="#-security-engine"><img src="https://img.shields.io/badge/Security-8__SEC__Rules-critical" alt="8 SEC Rules" /></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Fullstack-Next.js__Router__Ready-blue" alt="Next.js Ready" /></a>
  <a href="#-eval-matrix"><img src="https://img.shields.io/badge/Eval-11__Scenarios-brightgreen" alt="11 Eval Scenarios" /></a>
  <a href="#-multi-platform-installation"><img src="https://img.shields.io/badge/Platform-Claude%20Code%20%7C%20Cursor%20%7C%20VS%20Code-lightgrey" alt="Multi-platform" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.md">中文</a>
</p>

<p align="center">
  <img src="assets/hero.png" alt="RPD — Rapid Product Document" width="800" />
</p>

---

**你用 AI 做 Vibe Coding，每次开新对话它就失忆了。两周后回来，忘了当初为什么选 SQLite。**

RPD 是一个 [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills)，通过 **8 个零依赖的纯标准库 Python 脚本** 构建硬核运行时阻断协议，将项目记忆、技术栈决策、业务安全护栏硬化为高确定性的本地控制流。告别概率型 Cloud Memory 的废话糊墙，拒绝每次新开对话后的"精神断层"。

> **核心使命：硬化跨会话项目孪生状态，拦截决策 Spec 漂移，强行将具备概率不确定性的 AI 智能体死死锁在线性工程的高保真轨道上。**

---

## 🚀 快速开始 / Quick Start

### 1. 安装 Skill / Install

```bash
# 项目级安装（推荐）
mkdir -p .claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git _rpd_tmp
cp -r _rpd_tmp/* .claude/skills/rpd/
rm -rf _rpd_tmp
```

或全局安装（所有项目可用）：

```bash
mkdir -p ~/.claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git _rpd_tmp
cp -r _rpd_tmp/* ~/.claude/skills/rpd/
rm -rf _rpd_tmp
```

### 2. 验证安装 / Verify Installation

在 Claude Code 中输入：

```
我想做一个记账App
```

| 结果 | 含义 |
|------|------|
| Claude 问 "这个东西是给谁用的？" | ✅ Skill 已激活 |
| Claude 直接开始写代码 | ❌ 未安装成功，检查路径 |

### 3. 开始使用 / Start Building

```
# New project
我想做一个给独立开发者用的记账工具

# Take over existing project
接手这个项目

# Continue previous work
继续开发
```

---

## ✨ 功能特性 / Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🔄 Git 原生状态隔离</h3>
      <p><code>.project-state.md</code> 采用 Git-native 架构，配合 <code>state-guard.py</code> 的 Branch Affinity Lock，在 <code>git merge</code> 时自动熔断跨分支静默覆盖。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ 8 条业务安全规则</h3>
      <p>SEC-001~008 函数级检测：短信轰炸、UGC 无审核、文件上传漏洞、Prompt 泄露、无认证中间件。大文件流式扫描，永不静默跳过。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🎯 确定性意图路由</h3>
      <p><code>intent-router.py</code> 零 Token 硬分类：新项目 / 接手半成品 / 继续开发。小白自动进入场景探索模式，标准用户走三视角诊断。</p>
    </td>
    <td width="50%" valign="top">
      <h3>📉 Token 坍缩经济学</h3>
      <p>Turbo Mode 将项目上下文压缩为 4 行 100 Token 矩阵。安全扫描始终执行（零 Token 消耗）。长周期 Vibe Coding 的成本控制极限。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔍 决策漂移检测</h3>
      <p>PRD 定了用 JWT，代码里却装了 express-session。<code>gap-analyzer.py</code> 自动比对文档决策与实际依赖，发出 CRITICAL 警告。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🌐 现代全栈感知</h3>
      <p>完美兼容 Next.js App Router 文件路由、Prisma/Supabase 等现代 BaaS。双向中英文词根映射字典，中文功能名自动匹配英文代码。</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔐 原子化状态更新</h3>
      <p>备份 → 原子写入 → JSON Schema 校验 → 失败自动回滚。<code>state-guard.py</code> 保证状态文件永远不会写坏。</p>
    </td>
    <td width="50%" valign="top">
      <h3>🗣️ 中英双语</h3>
      <p>从首条消息检测语言，全程跟随。所有模板、诊断问题、安全报告、PRD 输出均支持中英文。</p>
    </td>
  </tr>
</table>

---

## 📦 多平台安装 / Multi-Platform Installation

### Claude Code（原生）

**项目级安装**（推荐 — 隔离在单个项目内）：

```bash
mkdir -p .claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git _rpd_tmp
cp -r _rpd_tmp/* .claude/skills/rpd/
rm -rf _rpd_tmp
```

**全局安装**（所有项目可用）：

```bash
mkdir -p ~/.claude/skills/rpd
git clone --depth 1 https://github.com/ZhangJing-gugugaga/RPD-Skill.git _rpd_tmp
cp -r _rpd_tmp/* ~/.claude/skills/rpd/
rm -rf _rpd_tmp
```

### 一键安装（macOS / Linux）

```bash
curl -fsSL https://raw.githubusercontent.com/ZhangJing-gugugaga/RPD-Skill/main/install.sh | bash
```

### 一键安装（Windows PowerShell）

```powershell
iwr -useb https://raw.githubusercontent.com/ZhangJing-gugugaga/RPD-Skill/main/install.ps1 | iex
```

### Cursor

1. 克隆本仓库到项目目录
2. Cursor 通过 `.claude-plugin/plugin.json` 自动发现 Skill
3. 若自动发现失败：**Cursor Settings → Plugins** → 粘贴 `https://github.com/ZhangJing-gugugaga/RPD-Skill`

### VS Code + GitHub Copilot

1. 克隆本仓库到项目目录
2. VS Code 通过 `.claude-plugin/plugin.json` 自动发现 Skill
3. 个人级 Skill（所有项目可用）：复制到 `~/.claude/skills/rpd/`

### 平台兼容性 / Platform Compatibility

| 平台 | 状态 | 安装方式 | 说明 |
|------|------|----------|------|
| Claude Code | ✅ 原生支持 | `.claude/skills/rpd/` | 主要目标平台，全部功能 |
| Cursor | ✅ 支持 | 通过 `plugin.json` 自动发现 | 克隆仓库到项目目录 |
| VS Code + Copilot | ✅ 支持 | 通过 `plugin.json` 自动发现 | 克隆仓库到项目目录 |
| Codex | ⚠️ 实验性 | 手动复制到 skills 目录 | 仅核心流程 |
| Gemini CLI | ⚠️ 实验性 | 手动复制到 skills 目录 | 仅核心流程 |

---

## 🔄 更新 / Update

### 更新到最新版 / Update to Latest

```bash
# 项目级安装
cd .claude/skills/rpd && git pull origin main

# 全局安装
cd ~/.claude/skills/rpd && git pull origin main
```

### 查看当前版本 / Check Version

```bash
grep '"version"' .claude/skills/rpd/.claude-plugin/plugin.json
```

### 回滚到指定版本 / Pin Version

```bash
cd .claude/skills/rpd
git fetch --tags
git checkout v1.5.0  # or any tag
```

---

## 🏗 架构 / Architecture

```
[用户输入 (自然语言 / 快捷指令)]
                 │
                 ▼
      ┌──────────────────┐
      │ intent-router.py │ ──── 零 Token 意图硬路由与成熟度判断
      └──────────────────┘
                 │
  ┌──────────────┼──────────────┐
  ▼              ▼              ▼
Flow A          Flow B         Flow C
新项目          接手半成品      续传开发
三视角降维诊断  安全&技术探伤   差距分析&决策漂移
概念/落地版PRD  (流式分块防护)  (Next.js现代感知)
  │              │              │
  └──────────────┼──────────────┘
                 ▼
      ┌──────────────────┐
      │  state-guard.py  │ ──── 备份自滚回 & Git Branch Affinity Lock
      └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │state-validator.py│ ──── YAML Frontmatter JSON Schema 强卡口
      └──────────────────┘
```

### 运行时工具箱 / Runtime Toolbox

| 脚本 | 确定性断言机制 | 调用时机 | 退出码 |
|------|---------------|----------|--------|
| `intent-router.py` | 正则关键词硬路由，成熟度分类 | 每次对话开始 | `0` 成功, `1` 错误 |
| `security-scanner.py` | 8 条 SEC 规则 + 路径遍历 + 注入检测 + 流式分块 | Flow B/C 冷启动 | `0` 安全, `1` 错误, `2` 阻断 |
| `project-scanner.py` | 技术栈、组件、API 路由、TODO | Flow B 接手 | `0` 成功, `1` 错误 |
| `gap-analyzer.py` | PRD vs 代码差距 + 决策漂移 + Next.js 路由检测 | Flow C 续传 | `0` 成功, `1` 错误, `2` 无状态, `3` 无功能 |
| `state-guard.py` | 原子写入 + 备份(max 10) + Git 分支亲和度锁 | 状态文件变更前 | `0` 成功, `1` 错误, `2` 回滚, `3` 未找到, `4` 冲突 |
| `state-validator.py` | YAML Frontmatter JSON Schema 校验 | 状态文件变更后 | `0` 有效, `1` 错误, `3` 无效 |
| `prd-validator.py` | 语义缺口审计（异常处理、状态机、字段规范） | 落地版 PRD 生成后 | `0` 完整, `1` 错误, `2` 有缺口 |
| `run-eval.py` | 11 个评估场景 | 开发 / CI | `0` 全部通过, `1` 部分失败 |

> **You never run these manually.** Claude calls them automatically at the appropriate workflow nodes.

### 底层机制 / Under the Hood

| 组件 | 机制 | 工程价值 |
|------|------|----------|
| `intent-router.py` | 预编译正则模式，首次匹配优先 | 零 Token 消耗，确定性路由 |
| `security-scanner.py` | 函数级上下文窗口（`to_top` 模式）+ >1MB 文件流式分块 | 检测同文件内联 rateLimit 中间件，永不静默跳过大文件 |
| `gap-analyzer.py` | 三层接口检测（API 路由 → 页面路由 → 数据模型）+ 双向中英文词根映射（50+ 条目） | 中文"登录"自动匹配英文 `login` |
| `state-guard.py` | `branch-affinity` YAML 字段 + `git branch --show-current` 比对 | 防止跨分支静默合并项目记忆 |
| `state-validator.py` | JSON Schema `minimum`/`maximum`/`pattern`/`enum` 约束 | 阻断 Agent 选择性截断元数据 |
| `prd-validator.py` | 六大盲区自检清单 + `####` 标题检测 | 确保 PRD 覆盖异常处理、状态机、字段规范 |

---

## 🔐 安全引擎 / Security Engine

| 规则 ID | 名称 | 严重程度 | 检测模式 |
|---------|------|----------|----------|
| SEC-001 | 短信/邮件发送接口缺少频率限制 | `CRITICAL` | `sendSMS()` / `sendEmail()` 同函数上下文无 `rateLimit` |
| SEC-002 | 用户生成内容(UGC)写入无审核机制 | `CRITICAL` | `Comment.create()` 同函数上下文无 `contentModerat` |
| SEC-003 | 文件上传缺少文件类型校验 | `HIGH` | `multer({storage})` 无 `fileFilter` |
| SEC-004 | 文件存储在服务器本地磁盘 | `MEDIUM` | 使用 `diskStorage()` |
| SEC-005 | AI System Prompt 硬编码在代码中 | `HIGH` | 代码中 `SYSTEM_PROMPT = "..."` |
| SEC-006 | 文件 URL 直接可访问，无防盗链保护 | `MEDIUM` | `res.json({url: ...})` 无签名 URL |
| SEC-007 | API 路由缺少认证中间件 | `HIGH` | `router.get("/api/...")` 上下文窗口无 `auth` |
| SEC-008 | AI System Prompt 通过字符串拼接构造 | `LOW` | `SYSTEM_PROMPT = var + "..."` |

**额外防护 / Additional Protections:**

| 防护类型 | 机制 |
|----------|------|
| 路径遍历 | `verify_path_safety()` — 解析符号链接，阻断 `../` 逃逸 |
| 提示词注入 | 状态文件模式检测（`ignore previous instructions` 等） |
| 大文件绕过 | >1MB 文件逐行流式扫描，带 `[大文件流式拦截]` 前缀 |
| 注释过滤 | 跳过 `#`、`//`、`*` 开头的行，防止误报 |

---

## 📐 架构边界与非目标 / Scope & Non-Goals

RPD 专注于为大语言模型提供运行时确定性控制流约束，其工程职责遵循严格的**最小干预原则**：

| Scope | Description |
|-------|-------------|
| **Non-Goals** | 本系统不介入具体生成式代码的物理编写，不替代人类进行顶层商业/产品选型决策，亦不提供概率型的发散推演 |
| **Core Mission** | 硬化跨会话项目孪生状态，拦截决策 Spec 漂移，强行将具备概率不确定性的 AI 智能体死死锁在线性工程的高保真轨道上 |

---

## 📁 目录结构 / Directory Structure

```
rpd/
├── .claude-plugin/
│   └── plugin.json              # 插件元数据（名称、版本、关键词）
├── SKILL.md                     # 主控指令（中英双语，6 条硬性红线）
├── README.md                    # 本文件
├── scripts/
│   ├── intent-router.py         # 确定性意图分类
│   ├── security-scanner.py      # 8 条 SEC 规则 + 流式扫描 + 路径遍历防护
│   ├── project-scanner.py       # 技术栈 / 组件 / 路由检测
│   ├── gap-analyzer.py          # PRD vs 代码 + 决策漂移 + Next.js 路由
│   ├── state-validator.py       # YAML Frontmatter JSON Schema 校验
│   ├── state-guard.py           # 原子写入 + 备份 + 分支亲和度锁
│   ├── prd-validator.py         # PRD 完整性审计
│   └── run-eval.py              # 11 个评估场景
├── references/
│   ├── prd-template.md          # PRD 模板（概念版 + 落地版 + 安全自检清单）
│   ├── state-file-spec.md       # 状态文件规范（5 列功能表 + 5 列决策表）
│   ├── state-schema.json        # 状态文件 JSON Schema
│   └── keyword-map.json         # 中英文关键词映射（50+ 条目）
├── eval/
│   └── scenarios/               # 11 个评估场景定义
└── assets/
    ├── hero.png                 # 首图
    └── example-state.md         # 示例状态文件
```

---

## 🧪 评估矩阵 / Eval Matrix

11 evaluation scenarios covering all core functionality, run via `python scripts/run-eval.py`:

| 场景 | 名称 | 测试内容 | 退出码 |
|------|------|----------|--------|
| A | 空项目 | 状态文件不存在 → 正确报错 | `1` |
| B | 损坏的状态文件 | YAML Frontmatter 无效 → Schema 拒绝 | `3` |
| C | 提示词注入 | 状态文件注入模式 → 硬阻断 | `2` |
| D | 半成品项目 | React+Vite 检测 → 正确识别技术栈 | `0` |
| E | 意图路由器 | 7 个意图分类用例（中英文） | `0` |
| F | PRD 校验器 | 完整 / 缺失异常处理 / `####` 标题 | `0`/`2` |
| G | 决策漂移 | 无漂移 / MEDIUM 共存 / HIGH 替换 | `0` |
| H | 状态守卫 | 备份 / 清理 / 回滚操作 | `0` |
| I | SEC 规则 | SEC-001 检测、内联 limiter 绕过、注释过滤 | `0`/`2` |
| O | 中文项目名 | YAML Frontmatter 中文项目名 | `0` |
| P | Turbo 模式 | 模糊输入 → `scene_exploration` 路由 | `0` |

---

## 📋 状态文件示例 / State File Example

`.project-state.md` — the project's digital twin, committed to Git:

```markdown
---
name: my-app
state_revision: 3
branch-affinity: main
last-commit-sha: a1b2c3d4
created: 2026-06-03
last-synced: 2026-06-08T14:30:00
status: in-development
entry-type: new-idea
---

## 功能进度清单
| 功能 | 子任务 | 优先级 | 状态 | 备注 |
|------|--------|--------|------|------|
| 用户登录 | 表单提交 | P0 | ✅ 已完成 | |
| 用户登录 | OAuth对接 | P0 | 🔨 进行中 | 70% |
| 记账功能 | 手动记账 | P0 | ⏳ 未开始 | |

## 关键决策记录
| 日期 | 类型 | 决策 | 原因 | 影响范围 |
|------|------|------|------|----------|
| 06-03 | 技术选型 | 用SQLite | 单机部署 | 数据层全局 |
| 06-05 | 安全策略 | 用JWT认证 | 无状态 | 认证层 |
```

---

## ❓ 常见问题 / FAQ

| 问题 | 回答 |
|------|------|
| 需要记住触发词吗？ | 不需要。`intent-router.py` 确定性分类意图，说人话就行 |
| Token 不够了怎么办？ | Turbo Mode 自动激活：跳过概念版 PRD，4 行 100 Token 输出，安全扫描照常（零 Token） |
| 可以中途改 PRD 吗？ | 可以。修改核心功能需重新冻结范围。概念版 PRD 改 >3 次建议先做用户调研 |
| 状态文件冲突了？ | `state-guard.py` 检测 Git UU 冲突 + Branch Affinity 不匹配 → exit(4) 硬阻断 |
| 能用在非 Node.js 项目？ | 可以。脚本扫描通用模式。框架检测对 React/Vue/Express/Flask/Django/Go/Java 最佳 |
| 大文件会被跳过吗？ | 不会。>1MB 文件流式逐行扫描，带 `[大文件流式拦截]` 前缀 |
| Next.js App Router 支持？ | 支持。`gap-analyzer.py` 检测 `app/api/xxx/route.ts` 的 `export async function` |

---

## 🤝 贡献 / Contributing

| 步骤 | 操作 |
|------|------|
| 1 | Fork 仓库 |
| 2 | 创建功能分支 (`git checkout -b feature/my-feature`) |
| 3 | 运行评估测试 (`python scripts/run-eval.py`) |
| 4 | 11 个场景必须全部通过 |
| 5 | 提交并发起 Pull Request |

请先开 Issue 讨论重大变更。

---

<p align="center">
  <strong>不介入决策，不接管编码。RPD 旨在为生成式智能体硬化本地工程契约。</strong><br>
  <strong>锁死长周期时空记忆，阻断认知偏差，让每一颗 Token 都精准压进高确定性交付的弹夹。</strong>
</p>
