# ⚡ RPD (Rapid Product Document)
### 智能体确定性认知工程学外骨骼 — 跨会话长周期全生命周期状态机

[![Bilingual](https://img.shields.io/badge/Language-EN%20%7C%20ZH-purple)](#)
[![Scripts](https://img.shields.io/badge/Runtime-8__stdlib__Python-yellow)](#)
[![Security](https://img.shields.io/badge/Engine-Deterministic__Control__Flow-red)](#)
[![Next.js](https://img.shields.io/badge/Fullstack-Next.js__AppRouter__Ready-blue)](#)

> **致重度 AI 编程创作者（Vibecoder）**：
> 告别概率型 Cloud Memory 的废话糊墙，拒绝每次新开 AI 对话后的"精神断层"。
> RPD 是内生于你代码仓（In-repo）的 Git 原生项目数字孪生系统。通过 **8 个纯标准库 Python 脚本** 构建的硬核运行时阻断协议，将项目记忆、技术栈决策、业务安全护栏硬化为高确定性的本地控制流。

---

## 🛑 核心三大工程防线 (Architectural Edge)

### 1. 🔄 Git 原生多分支状态隔离 (Branch Affinity Lock)
放弃跨项目共享的黑盒记忆。`.project-state.md` 采用 Git-native 架构，记忆紧随 Git 树移动。配合 `state-guard.py` 的 `branch-affinity` 亲和度校验，在执行 `git merge/checkout` 时自动熔断静默跨分支覆盖，彻底终结模型长周期开发中的语义时空错乱。

### 2. 🛡️ 现代全栈感知与安全断路器 (Fullstack & Security Guard)
- **Next.js App Router 级路由感知**：差距分析器（`gap-analyzer.py`）完美兼容现代基于文件系统（File-based）的全栈 API 路由识别，拒绝传统正则对现代架构的"静默失明"与误杀。
- **零 OOM 流式分块安全扫描**：`security-scanner.py` 内置 8 条严苛业务安全规则。针对超 1MB 的巨型大文件，自动降级至高安全流式分块扫描（Chunk Streaming），确保证照、明文密钥无处遁形。

### 3. 📉 Token 账单坍缩经济学 (Context Budget Economy)
内置 **Turbo Mode（极速模式）**。当上下文跌破 2000 阈值或模型过载时，系统策略自动硬性启动，斩断全部白话长文，将巨型项目上下文坍缩为 **4 行超精炼高密矩阵**，用极限不足 100 Token 锁死跨越数周的项目主干上下文。

---

## 🛠️ 智能体运行时工具箱 (Agent Toolkit)

系统由 8 个 **零第三方依赖 (Stdlib-only)** 的高吞吐 Python 脚本构筑，Agent 智能体将在后台根据运行时协议自动隐式调用，无需你手动敲击。

```
    [用户输入 (自然语言/快捷指令)]
                 │
                 ▼
      ┌──────────────────┐
      │ intent-router.py │ ──────► 零 Token 意图硬路由与成熟度判断
      └──────────────────┘
                 │
  ┌──────────────┼──────────────┐
  ▼              ▼              ▼
【Flow A: 新项目】 【Flow B: 接手】 【Flow C: 续传开发】
三视角降维诊断    安全&技术探伤    差距分析 & 决策漂移检测
概念/落地版PRD   (流式分块防护)   (Next.js现代感知)
  │              │              │
  └──────────────┼──────────────┘
                 ▼
      ┌──────────────────┐
      │  state-guard.py  │ ──────► 备份自滚回与 Git 分支亲和度强阻断
      └──────────────────┘
                 │
                 ▼
      ┌──────────────────┐
      │state-validator.py│ ──────► YAML Frontmatter JSON Schema 强卡口
      └──────────────────┘
```

| 核心组件 | 确定性断言机制 | Agent 隐式调用时机 |
|:---|:---|:---|
| `intent-router.py` | 静态正则硬分流，判定用户想法成熟度（Vague / Clear） | 每次新会话启动或指令分发 |
| `security-scanner.py` | 8 大商业高危红线扫描 + 流式分块大文件防绕过 | 接手半成品项目与开发续传冷启动 |
| `gap-analyzer.py` | 中英双向词根映射 + 决策漂移（Decision Drift）检测 | Flow C 差距分析与功能完成率静态计算 |
| `state-guard.py` | 物理增量备份（Max 10） + 原子覆写 + 分支并发亲和度锁 | 任何涉及持久化记忆文件改动前置节点 |
| `state-validator.py` | 顶层元数据 JSON Schema 卡口，阻断 Agent 选择性遗忘 | `.project-state.md` 变更后的强质检 |
| `prd-validator.py` | 语义缺口审计（强数异常流转分支与边界状态机） | 落地版 Full PRD 交付物最终放行质检 |

---

## 🟢 三阶用户多维接入指引

### 💡 视角 A：想法模糊的小白 (Non-coder)
你不必懂得什么是架构或状态机。当你丢出一句模糊想法时，`intent-router.py` 会自动开启**场景探索模式**：
1. **降维三轮 casual 对话**，只聊生活、聊痛点、聊期望，不聊商业模式。
2. 自动在后台生成**大白话版概念 PRD** 并自动为你标记安全投入优先级，零门槛冷启动。
3. **黑话隔离硬护栏**：系统强制 Agent 必须在后台消化底层脚本报错。严禁将"状态机缺失"等程序员黑话甩在你脸上。

### ⚡ 视角 B：有条理的初学者 (Junior Dev)
你在 PRD 里写的是中文"登录"，在代码里写的是 `login`。差距分析器会自动通过**内置双向词根映射字典**追踪你的开发进度。
* **技术栈锁死锁**：若你在文档中定好使用 SQLite，写代码时被 AI 诱导装了 `redis`，漂移检测脚本会在你敲击代码的第一时间发出 `CRITICAL` 警告，死死按住你本地失控的依赖仓。

### 🔴 视角 C：并发极客 (Heavy / Vibecoder)
支持标准快捷路由，极致提升控制效率：
* `/rpd new` : 强行切入新项目诊断流程。
* `/rpd take` : 触发本地代码仓安全与技术栈硬核探伤，倒推 PRD。
* `/rpd cont` : 极速加载本地持久化记忆，比对代码库，直接输出下一步高优先级行动计划。
* `/rpd status` : 零 Token 渲染当前项目数字孪生状态大盘。

---

## 📦 极速安装 (2 Minutes)

1. 在你的项目根目录下建立插件目录：
   ```bash
   mkdir -p .claude/skills/rpd
   ```

2. 将本技能包的所有文件及脚本同步至该目录。

3. 在 Agent 终端中输入 `"我想做一个记账App"`。
   * **激活成功**：Agent 开始进行三视角提问，代表硬核外骨骼已成功挂载。
   * **激活失败**：Agent 直接开始裸写代码，请人工检查路径及 `plugin.json` 配置。

---

<p align="center">
  <strong>RPD 不是万能的。它不能帮你做产品决策、写代码、融资。</strong>
  <br />
  <strong>它能做的是：让项目有记忆、方向不跑偏、Token 不浪费。</strong>
</p>
