#!/usr/bin/env python3
"""RPD-Skill host hook bridge: session auto-restore + closeout staleness guard.

One deterministic entry point for host lifecycle hooks (Claude Code / ZCode
plugin hooks). Pure stdlib, zero LLM calls, stdout carries ONLY the final JSON.

Modes:
  session-start <project-root>   Detect RPD state files and inject a restore
                                 summary via `additionalContext` (index-style,
                                 <=1800 chars). Fires on startup/resume/clear/
                                 compact — after a context compact it re-injects
                                 in full, which is the long-conversation fix.
  stop <project-root>            Closeout guard: if code changed after the last
                                 state sync (v2 fingerprint check / v1 mtime +
                                 git status), inject a gentle continuation note
                                 telling the agent to persist state first.
                                 Soft: never blocks (exit 0), max 3 nudges per
                                 session (stop_hook_active respected).

Behaviour contract (claude-mem postmortem rules):
  - no ANSI codes, no debug prints on stdout; logs go to a file only
  - non-RPD projects: print nothing, exit 0 (zero noise)
  - kill switch: env RPD_HOOKS_DISABLED=1 disables everything
  - output format: default claude (hookSpecificOutput wrapper); RPD_HOOK_FORMAT
    env or --format zcode switches to the flat {"additionalContext": ...} shape

Usage:
  python rpd-hook-bridge.py <mode> <project-root> [--format claude|zcode] [--log <file>]

Exit codes: 0 normal (including "nothing to say"), 1 usage/fatal error.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MAX_CONTEXT_CHARS = 1800
MAX_STOP_NOTE_CHARS = 600
MAX_NUDGES_PER_SESSION = 3
MAX_FINGERPRINT_FILES = 1500
SESSION_START_EVENTS = ("startup", "resume", "clear", "compact")


def log(project_root, message):
    """Append debug info to a log file — never to stdout (claude-mem lesson)."""
    try:
        log_file = os.environ.get("RPD_HOOK_LOG")
        if not log_file:
            data_dir = (_plugin_data_dir() or (Path(project_root) / ".rpd" / ".hooks-cache"))
            log_file = str(Path(data_dir) / "hook-bridge.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} {message}\n")
    except Exception:
        pass


def _plugin_data_dir():
    for var in ("ZCODE_PLUGIN_DATA", "CLAUDE_PLUGIN_DATA"):
        val = os.environ.get(var)
        if val:
            return val
    return None


def _project_dir():
    for var in ("ZCODE_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        val = os.environ.get(var)
        if val:
            return val
    return None


def read_stdin_json():
    """Read hook payload from stdin; tolerate empty/invalid input."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def emit(text, event, fmt):
    """Emit the final JSON (or nothing) to stdout, then exit 0."""
    if not text:
        return 0
    text = text[:MAX_CONTEXT_CHARS if event == "SessionStart" else MAX_STOP_NOTE_CHARS]
    if fmt == "zcode":
        out = {"additionalContext": text}
    else:
        out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
    print(json.dumps(out, ensure_ascii=False))
    return 0


def disabled():
    return os.environ.get("RPD_HOOKS_DISABLED", "").strip() == "1"


def detect_state(project_root):
    """Return (kind, path) for v2 active-context / v1 state file, or (None, None)."""
    v2 = project_root / ".rpd" / "active-context.md"
    if v2.is_file():
        return "v2", v2
    v1 = project_root / ".project-state.md"
    if v1.is_file():
        return "v1", v1
    return None, None


def _cache_dir(project_root):
    base = _plugin_data_dir() or (project_root / ".rpd" / ".hooks-cache")
    d = Path(base)
    d.mkdir(parents=True, exist_ok=True)
    return d


def session_marker(project_root, session_id):
    """Path of the per-session injection marker file."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")[:80]
    return _cache_dir(project_root) / f"injected-{safe}.json"


def already_injected(project_root, session_id):
    marker = session_marker(project_root, session_id)
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        return bool(data.get("full"))
    except Exception:
        return False


def mark_injected(project_root, session_id):
    marker = session_marker(project_root, session_id)
    try:
        marker.write_text(json.dumps({
            "full": True,
            "at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _trim_body(text, max_lines=14, max_chars=900):
    """Keep a bounded, non-empty summary of a state file body."""
    lines = []
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line or line.startswith("---"):
            continue
        lines.append(line)
        if sum(len(l) for l in lines) > max_chars or len(lines) >= max_lines:
            break
    return "\n".join(lines[:max_lines])


def v1_summary(state_path):
    """Parse v1 frontmatter + first progress rows into a short summary."""
    try:
        content = state_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    fm = {}
    body_started = False
    body_lines = []
    in_frontmatter = False
    for raw in content.split("\n"):
        line = raw.rstrip()
        if line.strip() == "---":
            if not body_started and not in_frontmatter:
                in_frontmatter = True
                continue
            if in_frontmatter:
                in_frontmatter = False
                body_started = True
                continue
        if in_frontmatter and ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
        elif body_started and line:
            body_lines.append(line)
    progress = [l for l in body_lines if l.lstrip().startswith("|")][:6]
    parts = [f"项目: {fm.get('name', '?')} | 状态: {fm.get('status', '?')} | "
             f"最近同步: {fm.get('last-synced', '?')}"]
    if progress:
        parts.append("功能进度（截选）:")
        parts.extend(progress)
    return "\n".join(parts)


def session_start(project_root, fmt):
    kind, state_path = detect_state(project_root)
    if kind is None:
        return 0  # not an RPD-managed project: silence
    payload = read_stdin_json()
    session_id = str(payload.get("session_id", "") or os.environ.get("CLAUDE_SESSION_ID", ""))
    source = str(payload.get("source", "startup"))
    if source not in SESSION_START_EVENTS:
        source = "startup"

    if source != "compact" and already_injected(project_root, session_id):
        log(project_root, f"session-start: already injected this session, light reminder")
        return emit("[RPD-Skill] 本会话已注入过项目状态摘要；详情见 .rpd/active-context.md。"
                    "收尾时记得更新状态文件。", "SessionStart", fmt)

    if kind == "v2":
        try:
            body = _trim_body(state_path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            body = "(状态文件读取失败，请手动检查 .rpd/active-context.md)"
        summary = f"v2 状态文件 .rpd/active-context.md 摘要:\n{body}"
    else:
        summary = v1_summary(state_path) or "(v1 状态文件存在但内容为空)"

    text = (
        f"[RPD-Skill] 检测到本项目由 RPD 状态管理（{kind}）。\n"
        f"{summary}\n"
        "---\n"
        "以上是上次会话留下的项目状态索引。继续开发前请通读 "
        + (".rpd/active-context.md 与 .rpd/decisions.md（仅 accepted）"
           if kind == "v2" else ".project-state.md")
        + "；收尾时必须通过 state-guard.py 更新状态（详见 SKILL.md）。"
    )
    mark_injected(project_root, session_id)
    log(project_root, f"session-start: injected {kind} summary (source={source})")
    return emit(text, "SessionStart", fmt)


# --- Stop mode: closeout staleness guard ---

def _git(project_root, args):
    try:
        return subprocess.check_output(
            ["git", "-C", str(project_root)] + args,
            text=True, encoding="utf-8", errors="replace", stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None


def v2_stale(project_root, meta):
    """Fingerprint check of meta-listed files vs disk; plus map_commit vs HEAD."""
    files = meta.get("files", {})
    checked = 0
    for rel, info in files.items():
        if checked >= MAX_FINGERPRINT_FILES:
            break
        checked += 1
        p = project_root / rel
        if not p.is_file():
            return True, f"状态记录的文件已删除: {rel}"
        try:
            digest = "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
        except Exception:
            return True, f"文件不可读: {rel}"
        if digest != info.get("fingerprint"):
            return True, f"源码改动未落盘 code-map: {rel}"
    map_commit = meta.get("map_commit")
    if map_commit and map_commit != "unknown":
        head = _git(project_root, ["rev-parse", "HEAD"])
        if head and head.strip() and head.strip() != map_commit:
            return True, "存在 map_commit 之后的提交，code-map 未增量落盘"
    return False, ""


def v1_stale(project_root, state_path):
    """v1 heuristic: uncommitted changes newer than the state file."""
    status = _git(project_root, ["status", "--porcelain"])
    if not status or not status.strip():
        return False, ""
    try:
        state_mtime = state_path.stat().st_mtime
    except Exception:
        return False, ""
    for line in status.splitlines():
        if len(line) < 4:
            continue
        rel = line[3:].strip().strip('"')
        p = project_root / rel
        if p.suffix.lower() in (".md",) and rel.startswith("."):
            continue  # state/meta files themselves
        try:
            if p.is_file() and p.stat().st_mtime > state_mtime:
                return True, f"代码改动晚于状态更新: {rel}"
        except Exception:
            continue
    return False, ""


def nudge_count(project_root, session_id):
    marker = _cache_dir(project_root) / f"stop-{re.sub(r'[^A-Za-z0-9_-]', '_', session_id or 'unknown')[:80]}.json"
    try:
        return int(json.loads(marker.read_text(encoding="utf-8")).get("count", 0)), marker
    except Exception:
        return 0, marker


def bump_nudge(project_root, session_id, marker, new_count):
    try:
        marker.write_text(json.dumps({"count": new_count}), encoding="utf-8")
    except Exception:
        pass


def stop(project_root, fmt):
    payload = read_stdin_json()
    if payload.get("stop_hook_active"):
        return 0  # our own continuation: never recurse
    session_id = str(payload.get("session_id", "") or os.environ.get("CLAUDE_SESSION_ID", ""))

    kind, state_path = detect_state(project_root)
    if kind is None:
        return 0

    reason = ""
    if kind == "v2":
        meta_path = project_root / ".rpd" / "code-map.meta.json"
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                stale, reason = v2_stale(project_root, meta)
            except Exception as e:
                log(project_root, f"stop: meta parse failed: {e}")
                stale = False
        else:
            # v2 context exists but no code-map yet: fall back to v1 heuristic
            stale, reason = v1_stale(project_root, state_path)
    else:
        stale, reason = v1_stale(project_root, state_path)

    if not stale:
        return 0

    count, marker = nudge_count(project_root, session_id)
    if count >= MAX_NUDGES_PER_SESSION:
        log(project_root, f"stop: stale but nudge limit reached ({count})")
        return 0  # soft: never hold the user hostage
    bump_nudge(project_root, session_id, marker, count + 1)
    log(project_root, f"stop: stale ({reason}), nudge {count + 1}/{MAX_NUDGES_PER_SESSION}")

    text = (
        f"[RPD-Skill 落盘提醒 {count + 1}/{MAX_NUDGES_PER_SESSION}] {reason}。"
        "结束前请先落盘状态：运行 state-guard.py --action backup 后更新"
        + (" .rpd/active-context.md 并增量重跑 code-map-generator.py"
           if kind == "v2" else " .project-state.md（跑 state-validator.py 校验）")
        + "，然后正常收尾。"
    )
    return emit(text, "Stop", fmt)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python rpd-hook-bridge.py <session-start|stop> <project-root> "
              "[--format claude|zcode]")
        return 1
    mode = args[0]
    if mode not in ("session-start", "stop"):
        print(f"Error: unknown mode: {mode}", file=sys.stderr)
        return 1
    if disabled():
        return 0
    root_arg = args[1] if len(args) > 1 else (_project_dir() or "")
    project_root = Path(root_arg)
    if not project_root.is_dir():
        return 0  # hooks must never hard-fail a session on a bad path
    fmt = "claude"
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            fmt = args[idx + 1]
    fmt = os.environ.get("RPD_HOOK_FORMAT", fmt)

    try:
        if mode == "session-start":
            return session_start(project_root, fmt)
        return stop(project_root, fmt)
    except Exception as e:
        log(project_root, f"fatal in {mode}: {e!r}")
        return 0  # a broken guard must never break the session


if __name__ == "__main__":
    sys.exit(main())
