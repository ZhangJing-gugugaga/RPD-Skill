# RPD 自动恢复与落盘保障 — 无 hook 宿主降级指引

> 把下面这段粘贴进你项目的 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`（按宿主而定）。
> 它把 RPD 的两条核心纪律（会话开始自动恢复、收尾必落盘）以提示词方式实现，
> 用于不支持插件 hooks 的宿主。支持 hooks 的宿主（Claude Code / ZCode）请勿粘贴，
> 让 `hooks/hooks.json` 的确定性脚本接管。

```markdown
## RPD 项目状态纪律（rpd-skill）

1. 会话开始：如果项目根存在 `.rpd/active-context.md` 或 `.project-state.md`，
   先读取它们再回应任何开发请求（这是上次会话的项目状态，是唯一真相源）；
   `.rpd/knowledge.md` 与 `.rpd/decisions.md`（仅 accepted）按需阅读。
2. 收尾必写：每次会话结束前，若有任何代码改动，必须：
   - 更新 `.rpd/active-context.md`（进度/下一步/阻塞），改源码则重跑
     `python scripts/code-map-generator.py <项目根> --incremental`；
   - 写状态前先 `python scripts/state-guard.py <状态文件> --action backup`；
   - `.project-state.md` 更新后必跑 `state-validator.py` 校验。
3. 新决策写入 `.rpd/decisions.md` 前先跑
   `python scripts/rpd-decisions.py <项目根> reconcile "<决策>"` 对账，
   防止矛盾决策堆叠。
```

## 能力三档对照

| 档位 | 宿主 | 自动恢复 | 落盘保障 | 语义层防腐 |
|------|------|----------|----------|------------|
| 1. 插件 hooks（推荐） | Claude Code、ZCode | SessionStart 注入恢复摘要（compact 后全量重注入） | Stop 指纹机检软提醒（≤3 次） | code-map fingerprint + 语义条目绑定 |
| 2. 粘贴本 snippet | OpenCode、Gemini CLI 等 | 提示词约定（读状态文件） | 提示词约定 | 同上（结构层照常生效） |
| 3. 纯 SKILL.md | 无 AGENTS.md 机制的宿主 | 依赖 description 触发 | 无 | 同上 |

## Claude Code 专属可选增强：PreCompact 落盘提醒

ZCode 无 PreCompact 事件。Claude Code 用户可在用户级 hooks 配置追加
（配合插件 SessionStart 的 compact 全量重注入，形成压缩前后闭环）：

```json
{
  "hooks": {
    "PreCompact": [
      { "hooks": [ { "type": "command",
        "command": "python \"${CLAUDE_PLUGIN_ROOT}/scripts/rpd-hook-bridge.py\" stop \"${CLAUDE_PROJECT_DIR}\"" } ] }
    ]
  }
}
```

## 故障排查

- **SessionStart 注入乱码/失败**：确认 `python` 在 PATH 指向真实 Python
  （Windows 商店占位符 python.exe 会静默失败）；控制台编码问题已由脚本内
  `PYTHONIOENCODING`/`reconfigure` 处理，无需额外设置。
- **不想要提醒**：环境变量 `RPD_HOOKS_DISABLED=1` 全局关闭。
- **ZCode 输出格式**：ZCode 工作区配置中给 bridge 加 `--format zcode`
  （扁平 `additionalContext` JSON）。
