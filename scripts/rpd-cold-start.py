#!/usr/bin/env python3
"""RPD v2 cold-start: 7-step session bootstrap with v1 compatibility read.

Performs:
  1. Read active-context.md (last progress, next steps, blockers)
  2. Red-line machine check: read code-map.meta.json, git diff map_commit..HEAD,
     fingerprint comparison -> verified/unverified/stale file list
  3. Declare freshness: one-line statement of map commit + verified/stale counts;
     if stale -> read affected files first (or hint to update map);
     if understand-anything degraded -> explicit warning
  4. On-demand load: read code-map.router.json (Layer 1, if not already in context);
     per-task look up entry_ref via router, read single entry (<=300 token)
  5. Locate: use id = function:path:name for symbols/files/candidate call edges
  6. Act: before acting on map info, target file must be verified (else Read first)
  7. Wrap-up: update active-context.md; incremental code-map dump; decisions.md;
     review view on audit sessions

Usage:
  python rpd-cold-start.py <project-root> [--json]
  python rpd-cold-start.py <project-root> --migrate   # v1 -> v2 migration backup

Exit codes:
  0 - Cold-start completed
  1 - Usage error / project root missing
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def smart_read(file_path):
    """Read file with multiple encoding attempts."""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'cp1252', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


# Fix Windows encoding for JSON output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def sha256_of_file(path):
    """Full-content sha256 of a file."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def read_meta(project_root):
    """Read code-map.meta.json; return {} if missing."""
    meta_path = project_root / ".rpd" / "code-map.meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(smart_read(str(meta_path)))
    except Exception:
        return {}


def git_available(project_root):
    """Check whether the project is a git repo and git is available."""
    try:
        subprocess.check_output(
            ["git", "-C", str(project_root), "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def current_head(project_root):
    """Get current HEAD commit hash; None if unavailable."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            text=True, encoding="utf-8", errors="replace"
        ).strip()
    except Exception:
        return None


def git_status(project_root):
    """`git status --porcelain` output, or None if git unavailable."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(project_root), "status", "--porcelain"],
            text=True, encoding="utf-8", errors="replace", stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None


def redline_check(project_root, meta):
    """Red-line machine check: fingerprint compare against meta.

    Returns dict: verified[], stale[], unverified[], git_ok, degraded_no_git.
    """
    result = {"verified": [], "stale": [], "unverified": [], "git_ok": False, "degraded_no_git": False}
    files_meta = meta.get("files", {})
    if not files_meta:
        return result

    git_ok = git_available(project_root)
    result["git_ok"] = git_ok
    head = current_head(project_root)
    map_commit = meta.get("map_commit") or meta.get("head_commit")

    # Fast path (P1-3): map_commit == HEAD and the worktree is clean means the
    # map was generated exactly at the current commit — trust it and skip the
    # full-repo re-hash (454 files ≈ seconds on every cold start otherwise).
    # Uncommitted (dirty) worktree still gets a full fingerprint check.
    if git_ok and map_commit and head and map_commit == head:
        status = git_status(project_root)
        if status is not None and not status.strip():
            result["verified"] = list(files_meta.keys())
            result["fast_path"] = True
            return result

    check_paths = list(files_meta.keys())

    if git_ok and map_commit and head and map_commit != head:
        # git diff map_commit..HEAD -> changed file set
        try:
            out = subprocess.check_output(
                ["git", "-C", str(project_root), "diff", "--name-only", f"{map_commit}..HEAD"],
                text=True, encoding="utf-8", errors="replace"
            )
            changed = {line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()}
            if changed:
                check_paths = [p for p in check_paths if p in changed] or check_paths
        except Exception:
            pass  # fall through to full fingerprint check

    for rel_path in check_paths:
        abs_path = project_root / rel_path
        expected = files_meta.get(rel_path, {})
        if not abs_path.exists():
            result["stale"].append({"file": rel_path, "reason": "missing"})
            continue
        actual = sha256_of_file(abs_path)
        expected_fp = expected.get("fingerprint", "")
        # expected_fp format: "sha256:<hex>"
        expected_hex = expected_fp.split(":")[-1] if expected_fp else ""
        if expected_hex and actual and actual == expected_hex:
            result["verified"].append(rel_path)
        else:
            result["stale"].append({"file": rel_path, "reason": "fingerprint_mismatch"})

    if not git_ok:
        result["degraded_no_git"] = True

    return result


def find_kg(project_root):
    """Detect understand-anything knowledge-graph.json (R-10).

    Probe order: .claude/ -> .workbuddy/ -> project root -> .rpd/.
    Returns (path_or_None, schema_ok).
    """
    candidates = [
        project_root / ".claude" / "knowledge-graph.json",
        project_root / ".workbuddy" / "knowledge-graph.json",
        project_root / "knowledge-graph.json",
        project_root / ".rpd" / "knowledge-graph.json",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                data = json.loads(smart_read(str(cand)))
                if isinstance(data, dict) and ("nodes" in data or "edges" in data):
                    return str(cand), True
                return str(cand), False
            except Exception:
                return str(cand), False
    return None, False


def detect_understand_anything(project_root):
    """R-10: detect knowledge-graph.json; returns reuse/degrade status + warning."""
    path, schema_ok = find_kg(project_root)
    if path and schema_ok:
        return {"detected": True, "reused": True, "source_path": path, "warning": None}
    if path and not schema_ok:
        return {
            "detected": True,
            "reused": False,
            "source_path": path,
            "warning": (
                "⚠️ 检测到 understand-anything 的 knowledge-graph.json 存在但 schema 不兼容（或缺失），"
                "已降级为 rpd 自建 code-map。不会读取/修改该文件。"
            ),
        }
    return {"detected": False, "reused": False, "source_path": None, "warning": None}


def parse_v1_state(project_root):
    """Compatibility read of v1 .project-state.md (never writes)."""
    state_path = project_root / ".project-state.md"
    result = {"found": False, "features": [], "decisions": [], "blockers": []}
    if not state_path.exists():
        return result
    result["found"] = True
    content = smart_read(str(state_path))
    if not content:
        return result

    # Parse feature table (5-col: 功能|子任务|优先级|状态|备注)
    table_match = re.search(
        r'\|\s*功能\s*\|\s*子任务\s*\|\s*优先级\s*\|\s*状态\s*\|\s*备注\s*\|(.*?)(?=\n\n|\n##|\Z)',
        content, re.DOTALL
    )
    if table_match:
        for row in table_match.group(1).strip().split("\n"):
            if "|" not in row or "---" in row:
                continue
            cols = [c.strip() for c in row.split("|") if c.strip()]
            if len(cols) >= 5:
                result["features"].append({
                    "feature": cols[0], "subtask": cols[1],
                    "priority": cols[2], "status": cols[3], "note": cols[4],
                })
    # Parse decision table (5-col: 日期|类型|决策|原因|影响范围)
    decision_match = re.search(
        r'\|\s*日期\s*\|\s*类型\s*\|\s*决策\s*\|\s*原因\s*\|\s*影响范围\s*\|(.*?)(?=\n\n|\n##|\Z)',
        content, re.DOTALL
    )
    if decision_match:
        for row in decision_match.group(1).strip().split("\n"):
            if "|" not in row or "---" in row:
                continue
            cols = [c.strip() for c in row.split("|") if c.strip()]
            if len(cols) >= 3:
                result["decisions"].append({
                    "date": cols[0], "type": cols[1],
                    "decision": cols[2], "reason": cols[3] if len(cols) > 3 else "",
                    "scope": cols[4] if len(cols) > 4 else "",
                })
    return result


def backup_v1_state(project_root):
    """Backup v1 .project-state.md to .rpd-backup-<timestamp>/ and write the
    v1-migrated freeze marker (the original file is preserved, never deleted).

    The marker (".rpd/v1-migrated.json") is the convergence signal: all v2
    tooling treats v1 as read-only reference from this point on (P1-1).
    """
    state_path = project_root / ".project-state.md"
    if not state_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / f".rpd-backup-{ts}"
    backup_dir.mkdir(exist_ok=True)
    dest = backup_dir / ".project-state.md"
    shutil.copy2(state_path, dest)
    marker = project_root / ".rpd" / "v1-migrated.json"
    marker.parent.mkdir(exist_ok=True)
    marker.write_text(json.dumps({
        "migrated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "backup_dir": str(backup_dir),
        "policy": "v1 frozen: read-only reference, never update .project-state.md again",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return backup_dir


def cold_start(project_root, do_migrate=False):
    """Run the 7-step cold-start. Returns report dict."""
    root = Path(project_root)
    rpd = root / ".rpd"
    report = {
        "project_root": str(root.resolve()),
        "steps": {},
        "v1_compat": None,
        "understand_anything": None,
        "warnings": [],
    }

    if not root.is_dir():
        report["error"] = f"Not a directory: {project_root}"
        return report

    # Migration (v1 -> v2): backup first, then ensure .rpd exists
    if do_migrate:
        backup_dir = backup_v1_state(root)
        if backup_dir:
            report["v1_backup"] = str(backup_dir)
        else:
            report["warnings"].append("未检测到 v1 .project-state.md，无需迁移备份")

    rpd.mkdir(exist_ok=True)

    # --- Step 1: read active-context ---
    ac_path = rpd / "active-context.md"
    ac_content = smart_read(str(ac_path)) if ac_path.exists() else None
    report["steps"]["01_active_context"] = {
        "found": ac_content is not None,
        "preview": (ac_content[:200] + "...") if ac_content and len(ac_content) > 200 else ac_content,
    }

    # v1 convergence check (P1-1): a migration marker means v1 is frozen —
    # reads for reference only, writes must never go back to the old file.
    if (rpd / "v1-migrated.json").is_file():
        report["v1_frozen"] = True
        if ac_content is None:
            report["warnings"].append(
                "v1 已迁移冻结（存在 v1-migrated 标记）但 .rpd/active-context.md 缺失："
                "请先完成 v2 状态文件生成，不要再更新 .project-state.md")

    # --- Step 2: red-line machine check ---
    meta = read_meta(root)
    redline = redline_check(root, meta)
    report["steps"]["02_redline"] = redline

    # --- Step 3: declare freshness + understand-anything degrade ---
    ua = detect_understand_anything(root)
    report["understand_anything"] = ua
    if ua.get("warning"):
        report["warnings"].append(ua["warning"])

    map_commit = meta.get("map_commit") or meta.get("head_commit") or "unknown"
    fresh_line = f"map 基于 commit {map_commit}，{len(redline['verified'])} 文件 verified，{len(redline['stale'])} 文件 stale"
    if redline["stale"]:
        fresh_line += "（stale: " + ", ".join(s["file"] for s in redline["stale"][:5]) + "）"
    report["freshness"] = fresh_line

    # --- Step 4: on-demand load (router) ---
    router_path = rpd / "code-map.router.json"
    router_loaded = router_path.exists()
    report["steps"]["04_router"] = {"loaded": router_loaded}
    if router_loaded:
        try:
            router = json.loads(smart_read(str(router_path)))
            report["steps"]["04_router"]["budget"] = router.get("budget", {})
        except Exception:
            report["steps"]["04_router"]["budget"] = {}

    # --- Step 5: locate (symbol addressing) ---
    report["steps"]["05_locate"] = {"mode": "map_navigation"}

    # --- Step 6: act (verify target first) ---
    report["steps"]["06_act"] = {
        "must_read_first": redline["stale"],
        "rule": "基于 map 动手前，目标文件必须 verified；否则先 Read",
    }

    # --- Step 7: wrap-up hooks ---
    report["steps"]["07_wrapup"] = {
        "update_active_context": True,
        "update_code_map": "未落盘变更需显式告警",
    }

    # --- v1 compatibility read (never overwrite v2 active-context) ---
    v1 = parse_v1_state(root)
    report["v1_compat"] = {
        "found": v1["found"],
        "features": v1["features"],
        "decisions": v1["decisions"],
        "blockers": v1["blockers"],
    }
    if v1["found"]:
        report["warnings"].append(
            "⚠️ 兼容读取：检测到 v1 .project-state.md，已读取其功能进度与关键决策作为参考，不覆盖 v2 active-context。"
        )

    return report


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python rpd-cold-start.py <project-root> [--json] [--migrate]")
        return 1

    project_root = args[0]
    as_json = "--json" in args
    do_migrate = "--migrate" in args

    if not Path(project_root).is_dir():
        print(f"Error: Not a directory: {project_root}", file=sys.stderr)
        return 1

    report = cold_start(project_root, do_migrate=do_migrate)
    if "error" in report:
        print(f"Error: {report['error']}", file=sys.stderr)
        return 1

    # Output warnings always to stderr (explicit warning, never silent)
    for w in report["warnings"]:
        print(w, file=sys.stderr)

    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Project root: {report['project_root']}")
        print(f"Freshness: {report.get('freshness', 'n/a')}")
        if report.get("v1_backup"):
            print(f"v1 迁移备份: {report['v1_backup']}")
        if report.get("understand_anything") and report["understand_anything"].get("detected"):
            ua = report["understand_anything"]
            print(f"understand-anything: {'复用' if ua['reused'] else '降级'} ({ua['source_path']})")
        print("Steps: " + ", ".join(k for k in report["steps"]))
        for w in report["warnings"]:
            print(w)

    return 0


if __name__ == "__main__":
    sys.exit(main())
