#!/usr/bin/env python3
"""Compare PRD feature list from .project-state.md against actual code.

Usage: python gap-analyzer.py <project-directory> [--state-file <path>]

Exit codes:
  0 - Analysis complete
  1 - Usage error
  2 - State file missing or invalid
  3 - No features defined in state file

Output: JSON to stdout with gap analysis report.
"""

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
}


def parse_state_file(state_path):
    """Parse .project-state.md to extract features and blockers."""
    content = Path(state_path).read_text(encoding="utf-8")

    # Extract features from the progress table
    features = []
    feature_table_pattern = re.compile(
        r'\|\s*功能\s*\|\s*优先级\s*\|\s*状态\s*\|\s*备注\s*\|(.*?)(?=\n\n|\n##|\Z)',
        re.DOTALL
    )
    match = feature_table_pattern.search(content)
    if match:
        rows = match.group(1).strip().split("\n")
        for row in rows:
            if "|" not in row or "---" in row:
                continue
            cols = [c.strip() for c in row.split("|") if c.strip()]
            if len(cols) >= 3:
                name = cols[0]
                priority = cols[1]
                status_text = cols[2]
                # Determine status
                if "已完成" in status_text or "✅" in status_text:
                    status = "completed"
                elif "进行中" in status_text or "🔨" in status_text:
                    status = "in_progress"
                else:
                    status = "not_started"
                features.append({
                    "name": name,
                    "priority": priority,
                    "status": status,
                    "status_text": status_text,
                })

    # Extract blockers
    blockers = []
    blocker_pattern = re.compile(r'- \[ \]\s*(.+)')
    in_blockers = False
    for line in content.split("\n"):
        if "当前阻塞项" in line:
            in_blockers = True
            continue
        if in_blockers:
            if line.startswith("##") or line.startswith("#"):
                break
            m = blocker_pattern.match(line)
            if m:
                blockers.append(m.group(1).strip())

    # Extract PRD summary
    prd_summary = {}
    if "核心功能" in content:
        core_match = re.search(r'核心功能.*?：(.+)', content)
        if core_match:
            prd_summary["core_features"] = core_match.group(1).strip()

    return {
        "features": features,
        "blockers": blockers,
        "prd_summary": prd_summary,
    }


def scan_code_for_features(project_dir, features):
    """Check which features have corresponding code."""
    p = Path(project_dir)
    results = []

    for feature in features:
        name = feature["name"]
        # Simple heuristic: look for files/keywords related to the feature name
        search_terms = [name.lower()]

        # Also search for common English equivalents
        keyword_map = {
            "登录": ["login", "signin", "auth"],
            "注册": ["register", "signup"],
            "列表": ["list", "index", "table"],
            "详情": ["detail", "show", "view"],
            "搜索": ["search", "filter"],
            "导出": ["export", "download"],
            "导入": ["import", "upload"],
            "编辑": ["edit", "update", "modify"],
            "删除": ["delete", "remove", "destroy"],
            "创建": ["create", "new", "add"],
            "用户": ["user", "profile"],
            "设置": ["setting", "config", "preference"],
            "报表": ["report", "chart", "analytics"],
            "通知": ["notification", "alert", "message"],
            "支付": ["payment", "pay", "checkout"],
            "订单": ["order"],
            "分页": ["pagination", "paginate", "pager"],
            "记账": ["accounting", "ledger", "transaction"],
            "分类": ["category", "classify"],
            "统计": ["statistics", "stats", "summary"],
        }

        for cn, en_terms in keyword_map.items():
            if cn in name:
                search_terms.extend(en_terms)

        # Search for matching files
        matching_files = []
        code_extensions = {".js", ".jsx", ".ts", ".tsx", ".py", ".vue", ".svelte", ".go", ".java"}

        for f in p.rglob("*"):
            if not f.is_file():
                continue
            parts = f.relative_to(p).parts
            if any(skip in parts for skip in SKIP_DIRS):
                continue
            if f.suffix not in code_extensions:
                continue
            fname = f.name.lower()
            fpath = str(f.relative_to(p)).lower()
            for term in search_terms:
                if term in fname or term in fpath:
                    matching_files.append(str(f.relative_to(p)))
                    break

        # Determine status based on code evidence
        if len(matching_files) >= 2:
            detected_status = "completed"
            evidence = f"Found {len(matching_files)} related files"
        elif len(matching_files) == 1:
            detected_status = "in_progress"
            evidence = "Found 1 related file"
        else:
            detected_status = "not_started"
            evidence = "No related code found"

        results.append({
            "feature": name,
            "prd_status": feature["status"],
            "detected_status": detected_status,
            "evidence": evidence,
            "matching_files": matching_files[:5],  # Limit to 5
        })

    return results


def check_blockers_resolved(project_dir, blockers):
    """Check if blockers have been resolved based on code evidence."""
    resolved = []
    open_blockers = []

    for blocker in blockers:
        resolved_evidence = None

        # Check if blocker mentions a technology that's now in dependencies
        pkg_json = Path(project_dir) / "package.json"
        if pkg_json.exists():
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                all_deps = " ".join({**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}.keys())
                if "分页" in blocker and ("paginate" in all_deps or "pagination" in all_deps):
                    resolved_evidence = "Pagination library found in dependencies"
                elif "图表" in blocker and ("chart" in all_deps or "echarts" in all_deps):
                    resolved_evidence = "Chart library found in dependencies"
            except Exception:
                pass

        if resolved_evidence:
            resolved.append({"blocker": blocker, "resolution": resolved_evidence})
        else:
            open_blockers.append({"blocker": blocker, "suggestion": "Manual review needed"})

    return resolved, open_blockers


def detect_deviations(project_dir, features, prd_summary):
    """Detect deviations between PRD intent and actual code."""
    deviations = []
    # Placeholder for more sophisticated deviation detection
    return deviations


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python gap-analyzer.py <project-directory> [--state-file <path>]")
        return 1

    project_dir = args[0]
    state_file = None

    if "--state-file" in args:
        idx = args.index("--state-file")
        if idx + 1 < len(args):
            state_file = args[idx + 1]

    # Default state file location
    if state_file is None:
        state_file = str(Path(project_dir) / ".project-state.md")

    if not Path(project_dir).is_dir():
        print(f"Error: Not a directory: {project_dir}", file=sys.stderr)
        return 1

    if not Path(state_file).exists():
        print(json.dumps({
            "error": "STATE_FILE_NOT_FOUND",
            "message": f"No .project-state.md found at {state_file}. Please run 'analyze project' or 'new project' first."
        }, indent=2, ensure_ascii=False))
        return 2

    # Parse state file
    try:
        state_data = parse_state_file(state_file)
    except Exception as e:
        print(f"Error: Cannot parse state file: {e}", file=sys.stderr)
        return 2

    features = state_data["features"]
    if not features:
        print(json.dumps({
            "error": "NO_FEATURES",
            "message": "No features defined in state file. Please complete requirement alignment first."
        }, indent=2, ensure_ascii=False))
        return 3

    # Analyze gaps
    feature_analysis = scan_code_for_features(project_dir, features)
    resolved, open_blockers = check_blockers_resolved(project_dir, state_data["blockers"])
    deviations = detect_deviations(project_dir, features, state_data["prd_summary"])

    # Build summary
    completed = sum(1 for f in feature_analysis if f["detected_status"] == "completed")
    in_progress = sum(1 for f in feature_analysis if f["detected_status"] == "in_progress")
    not_started = sum(1 for f in feature_analysis if f["detected_status"] == "not_started")

    result = {
        "summary": {
            "total_features": len(features),
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "completion_rate": round(completed / len(features), 3) if features else 0,
        },
        "details": feature_analysis,
        "blockers_resolved": resolved,
        "blockers_open": open_blockers,
        "deviations": deviations,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
