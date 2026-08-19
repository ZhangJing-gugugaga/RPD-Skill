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

def _load_generator_fns():
    """Load R-25 fns from the sibling code-map-generator.py (hyphenated filename
    cannot be plain-imported). Returns (check_dependency_drift, dependency_snapshot);
    both become no-op degrade stubs when the generator module is unavailable."""
    import importlib.util
    gen = Path(__file__).resolve().parent / "code-map-generator.py"
    if not gen.is_file():
        return None, None
    try:
        spec = importlib.util.spec_from_file_location("rpd_code_map_generator", gen)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.check_dependency_drift, mod.dependency_snapshot
    except Exception:
        return None, None


_check_drift, _dep_snapshot = _load_generator_fns()


def _load_exposure_guard():
    """Load R-23 run_exposure from the sibling exposure-guard.py (hyphenated
    filename cannot be plain-imported). Returns callable; no-op degrade stub
    when the module is unavailable (cold-start must never crash)."""
    import importlib.util
    eg = Path(__file__).resolve().parent / "exposure-guard.py"
    if not eg.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("rpd_exposure_guard", eg)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.run_exposure
    except Exception:
        return None


_run_exposure = _load_exposure_guard()


def _load_memory_layers():
    """Load R-21 memory report fns from the sibling memory-layers.py (hyphenated
    filename cannot be plain-imported). Returns (stats_fn, fast_path_fn) or
    (None, None) when the module is unavailable (cold-start must never crash)."""
    import importlib.util
    ml = Path(__file__).resolve().parent / "memory-layers.py"
    if not ml.is_file():
        return None, None
    try:
        spec = importlib.util.spec_from_file_location("rpd_memory_layers", ml)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.stats, mod.fast_path
    except Exception:
        return None, None


_mem_stats, _mem_fast = _load_memory_layers()


def memory_report(project_root):
    """R-21 layer-memory report (counts + fallback semantics). Degrades to a
    no-op note when the module is unavailable (never crashes cold-start)."""
    if _mem_stats is None:
        return {"checked": False, "note": "memory-layers module unavailable"}
    try:
        st = _mem_stats(Path(project_root))
        fp = _mem_fast(Path(project_root))
        return {
            "checked": True,
            "counts": st.get("counts"),
            "expired": st.get("expired"),
            "warnings": st.get("warnings", []),
            "fallback": st.get("fallback"),
            "fast_path": fp.get("path"),
            "scenario_count": len(fp.get("scenarios") or []),
            "profile_count": len(fp.get("profile") or []),
        }
    except Exception:
        return {"checked": False, "note": "memory report failed (degraded)"}


def exposure_layers(project_root):
    """R-23 progressive-exposure report (L1/L2/L3 budgets); degrades to a
    no-op note when the module is unavailable (never crashes cold-start)."""
    if _run_exposure is None:
        return {"checked": False, "note": "exposure-guard module unavailable"}
    try:
        payload = _run_exposure(project_root)
        return {
            "checked": True,
            "layers": {
                k: {
                    "allowed": v.get("allowed"),
                    "limit": v.get("limit"),
                    "estimated_tokens": v.get("estimated_tokens"),
                }
                for k, v in (payload.get("layers") or {}).items()
            },
            "task_budget": payload.get("task_budget"),
        }
    except Exception:
        return {"checked": False, "note": "exposure-guard check failed (degraded)"}


def check_dependency_drift(project_root, meta):
    """R-25 drift check (delegates to generator; degrades to no-op when unavailable)."""
    if _check_drift is None:
        return {"checked": False, "ok": True, "drift": [], "note": "generator module unavailable"}
    return _check_drift(project_root, meta)



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


def redline_check(project_root, meta):
    """Red-line machine check: fingerprint compare against meta.

    Returns dict: verified[], stale[], unverified[], git_ok, degraded_no_git.
    """
    result = {"verified": [], "stale": [], "unverified": [], "git_ok": False, "degraded_no_git": False}
    # R-25: dependency drift check (3rd pillar of the red-line check)
    result["dependency_drift"] = check_dependency_drift(project_root, meta)
    files_meta = meta.get("files", {})
    if not files_meta:
        return result

    git_ok = git_available(project_root)
    result["git_ok"] = git_ok
    head = current_head(project_root)
    map_commit = meta.get("map_commit") or meta.get("head_commit")

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
    """Backup v1 .project-state.md to .rpd-backup-<timestamp>/ (keeps original)."""
    state_path = project_root / ".project-state.md"
    if not state_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / f".rpd-backup-{ts}"
    backup_dir.mkdir(exist_ok=True)
    dest = backup_dir / ".project-state.md"
    shutil.copy2(state_path, dest)
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
        # R-21 (I4-6): L0-L3 layer-memory report (counts + fallback semantics)
        "memory": memory_report(root),
    }

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
    dep_drift = redline.get("dependency_drift") or {}
    dep_note = ""
    if dep_drift.get("checked") and not dep_drift.get("ok"):
        dep_note = "；⚠️ 依赖漂移 " + ", ".join(d["file"] for d in dep_drift["drift"][:5]) + " — 请重新生成图谱"
    fresh_line += dep_note
    if redline["stale"]:
        fresh_line += "（stale: " + ", ".join(s["file"] for s in redline["stale"][:5]) + "）"
    report["freshness"] = fresh_line

    # --- Step 4: on-demand load (router) + R-23 exposure report ---
    router_path = rpd / "code-map.router.json"
    router_loaded = router_path.exists()
    report["steps"]["04_router"] = {"loaded": router_loaded}
    if router_loaded:
        try:
            router = json.loads(smart_read(str(router_path)))
            report["steps"]["04_router"]["budget"] = router.get("budget", {})
        except Exception:
            report["steps"]["04_router"]["budget"] = {}
    # R-23 (I4-5): progressive exposure report (L1 resident / L2 on-demand /
    # L3 deep-follow-up) - always present, degrade never crashes
    report["steps"]["04_router"]["exposure_layers"] = exposure_layers(root)

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
