# RPD — Rapid Product Document

> 一个覆盖项目全生命周期的 Claude Code Skill

**灵感来源：** [FlowUs RPD Skill](https://flowus.cn/panix/share/9258e8aa-7a06-4b8d-9817-b7c6d1a0724d)

## 解决什么问题？

Vibecoding 时代，项目失败的三大断裂点：

1. **需求断裂**：想法模糊就开始写代码，反复返工
2. **上下文断裂**：切换 agent 后新 agent 完全不了解项目
3. **时间断裂**：项目搁置一段时间后无法恢复开发方向

RPD Skill 通过三个入口覆盖项目全生命周期，让 vibecoding 项目真正能落地。

## 安装

将 `skills/rpd/` 目录复制到你的 Claude Code skills 目录：

```bash
# 项目级安装
cp -r skills/rpd /path/to/your/project/.claude/skills/rpd

# 或全局安装
cp -r skills/rpd ~/.claude/skills/rpd
```

## 使用方式

### 入口 1：新项目

当你有一个新的产品想法时：

```
> 我想做一个记账 App，帮助个人用户追踪日常支出
```

RPD 会通过三视角诊断（用户/商业/技术）对齐需求，然后输出完整的 PRD 和项目状态文件。

### 入口 2：接手半成品

当你接手一个做到一半的项目时：

```
> 接手这个项目，分析一下当前进度
```

RPD 会扫描代码结构、识别技术栈、推断已完成的功能，然后生成 PRD 和状态文件。

### 入口 3：继续开发

切换 agent 或搁置一段时间后继续开发：

```
> 继续开发
```

RPD 会读取状态文件、分析当前代码与 PRD 的差距，输出行动建议和偏离警告。

## 目录结构

```
skills/rpd/
├── SKILL.md                  # 主控指令
├── README.md                 # 本文件
├── scripts/                  # 确定性脚本（纯 Python 标准库）
│   ├── project-scanner.py    # 扫描项目结构
│   ├── gap-analyzer.py       # 差距分析
│   ├── state-validator.py    # 状态文件校验
│   ├── security-scanner.py   # 安全扫描
│   └── run-eval.py           # 评估测试
├── references/               # 知识库
│   ├── brainstorming-flow.md # 头脑风暴流程
│   ├── prd-template.md       # PRD 模板
│   ├── state-file-spec.md    # 状态文件规范
│   └── state-schema.json     # JSON Schema
├── eval/scenarios/           # 评估场景
└── assets/example-state.md   # 示例状态文件
```

## 核心文件：.project-state.md

这是整个 skill 的心脏。它记录了：
- PRD 摘要（核心功能、排除项、商业模式）
- 功能进度清单（每个功能的完成状态）
- 关键决策记录（避免重复讨论）
- 当前阻塞项（待解决的问题）

切换 agent 时，新 agent 读取这个文件就能快速恢复上下文。

## 脚本说明

所有脚本使用 Python 标准库，零依赖：

| 脚本 | 用途 | Exit Code |
|------|------|-----------|
| project-scanner.py | 扫描项目结构和技术栈 | 0=成功, 1=错误 |
| gap-analyzer.py | 对比 PRD 与实际代码 | 0=成功, 2=无状态文件, 3=无功能 |
| state-validator.py | 校验状态文件格式 | 0=合法, 2=格式错误, 3=Schema错误 |
| security-scanner.py | 检测硬编码密钥和注入 | 0=安全, 2=发现问题 |
| run-eval.py | 运行评估场景 | 0=全部通过, 1=有失败 |

## 运行评估

```bash
python scripts/run-eval.py
```

## License

MIT
