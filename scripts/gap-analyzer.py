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
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
}

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB - skip files larger than this


def safe_read_file(path, max_size=MAX_FILE_SIZE):
    """Read file with size limit to prevent OOM."""
    try:
        if os.path.getsize(path) > max_size:
            return None
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


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


# --- Deterministic interface detection ---

def detect_api_routes(project_dir):
    """Detect API routes from code (deterministic)."""
    p = Path(project_dir)
    routes = []

    # Express/Flask/FastAPI route patterns
    route_pattern = re.compile(
        r'(?:app|router|server|api)\.(get|post|put|delete|patch|all|route)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    py_route_pattern = re.compile(
        r'@(?:app|router|api)\.(get|post|put|delete|patch|route)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    code_extensions = {".js", ".ts", ".py"}
    for ext in code_extensions:
        for f in p.rglob(f"*{ext}"):
            parts = f.relative_to(p).parts
            if any(skip in parts for skip in SKIP_DIRS):
                continue
            content = safe_read_file(f)
            if content is None:
                continue
            for match in route_pattern.finditer(content):
                routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": str(f.relative_to(p))})
            for match in py_route_pattern.finditer(content):
                routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": str(f.relative_to(p))})

    return routes


def detect_page_routes(project_dir):
    """Detect page routes from router config (deterministic)."""
    p = Path(project_dir)
    page_routes = []

    # React Router patterns: <Route path="/xxx" component={Xxx} />
    react_route_pattern = re.compile(
        r'<Route\s+.*?path\s*=\s*["\']([^"\']+)["\'].*?(?:component|element)\s*[={]\s*(\w+)',
        re.DOTALL
    )
    # Vue Router patterns: { path: '/xxx', component: Xxx }
    vue_route_pattern = re.compile(
        r'path\s*:\s*["\']([^"\']+)["\'].*?component\s*:\s*(\w+)',
        re.DOTALL
    )
    # Next.js file-based routing: pages/xxx.tsx or app/xxx/page.tsx
    next_page_pattern = re.compile(r'(?:pages|app)/(.+)\.(?:tsx|jsx|ts|js)$')

    for f in p.rglob("*"):
        if not f.is_file():
            continue
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue

        content = safe_read_file(f)
        if content is None:
            continue

        # React Router
        for match in react_route_pattern.finditer(content):
            page_routes.append({"path": match.group(1), "component": match.group(2), "file": str(f.relative_to(p))})

        # Vue Router
        for match in vue_route_pattern.finditer(content):
            page_routes.append({"path": match.group(1), "component": match.group(2), "file": str(f.relative_to(p))})

        # Next.js file-based routing
        rel = str(f.relative_to(p))
        next_match = next_page_pattern.match(rel)
        if next_match:
            page_path = "/" + next_match.group(1).replace("\\", "/")
            if page_path.endswith("/index"):
                page_path = page_path[:-6] or "/"
            page_routes.append({"path": page_path, "component": f.stem, "file": rel})

    return page_routes


def detect_data_models(project_dir):
    """Detect data models from ORM schemas (deterministic)."""
    p = Path(project_dir)
    models = []

    # Prisma: model User { ... }
    prisma_pattern = re.compile(r'model\s+(\w+)\s*\{', re.MULTILINE)
    # SQLAlchemy: class User(Base): or class User(db.Model):
    sqlalchemy_pattern = re.compile(r'class\s+(\w+)\s*\([^)]*(?:Base|Model)[^)]*\)\s*:', re.MULTILINE)
    # Mongoose: const UserSchema = new Schema({ or mongoose.model('User', ...)
    mongoose_pattern = re.compile(r'(?:const\s+(\w+)Schema\s*=\s*new\s+Schema|mongoose\.model\s*\(\s*["\'](\w+)["\'])', re.MULTILINE)

    for f in p.rglob("*"):
        if not f.is_file():
            continue
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue

        content = safe_read_file(f)
        if content is None:
            continue

        # Prisma
        for match in prisma_pattern.finditer(content):
            models.append({"name": match.group(1), "type": "prisma", "file": str(f.relative_to(p))})

        # SQLAlchemy
        for match in sqlalchemy_pattern.finditer(content):
            models.append({"name": match.group(1), "type": "sqlalchemy", "file": str(f.relative_to(p))})

        # Mongoose
        for match in mongoose_pattern.finditer(content):
            name = match.group(1) or match.group(2)
            models.append({"name": name, "type": "mongoose", "file": str(f.relative_to(p))})

    return models


def feature_name_keyword_match(feature_name, target):
    """Check if feature name matches a target string (path, component, model name)."""
    feature_lower = feature_name.lower()
    target_lower = target.lower()

    # Direct match
    if feature_lower in target_lower or target_lower in feature_lower:
        return True

    # Chinese to English keyword mapping for common terms
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
        if cn in feature_lower:
            for term in en_terms:
                if term in target_lower:
                    return True

    return False


def detect_feature_by_interface(project_dir, feature_name):
    """Deterministic detection: check if feature is implemented via interfaces.

    Detection layers:
    1. API route (Express/FastAPI/Flask route definitions)
    2. Page route (React Router / Vue Router / Next.js file-based)
    3. Data model (Prisma / SQLAlchemy / Mongoose)

    Returns: (status, evidence_list)
    """
    evidence = []

    # Layer 1: API routes
    api_routes = detect_api_routes(project_dir)
    feature_routes = [r for r in api_routes if feature_name_keyword_match(feature_name, r["path"])]
    if feature_routes:
        evidence.append({"type": "api_route", "items": feature_routes})

    # Layer 2: Page routes
    page_routes = detect_page_routes(project_dir)
    feature_pages = [p for p in page_routes if feature_name_keyword_match(feature_name, p["path"])]
    if feature_pages:
        evidence.append({"type": "page_route", "items": feature_pages})

    # Layer 3: Data models
    data_models = detect_data_models(project_dir)
    feature_models = [m for m in data_models if feature_name_keyword_match(feature_name, m["name"])]
    if feature_models:
        evidence.append({"type": "data_model", "items": feature_models})

    # Deterministic status decision
    if len(evidence) >= 2:
        return "completed", evidence
    elif len(evidence) == 1:
        return "in_progress", evidence
    else:
        return "not_started", evidence


def scan_code_for_features(project_dir, features):
    """Check which features have corresponding code (deterministic)."""
    results = []

    for feature in features:
        name = feature["name"]
        detected_status, evidence = detect_feature_by_interface(project_dir, name)

        # Build human-readable evidence string
        evidence_parts = []
        for ev in evidence:
            if ev["type"] == "api_route":
                paths = [r["path"] for r in ev["items"][:3]]
                evidence_parts.append(f"API routes: {', '.join(paths)}")
            elif ev["type"] == "page_route":
                paths = [p["path"] for p in ev["items"][:3]]
                evidence_parts.append(f"Page routes: {', '.join(paths)}")
            elif ev["type"] == "data_model":
                names = [m["name"] for m in ev["items"][:3]]
                evidence_parts.append(f"Data models: {', '.join(names)}")

        results.append({
            "feature": name,
            "prd_status": feature["status"],
            "detected_status": detected_status,
            "evidence": "; ".join(evidence_parts) if evidence_parts else "No interface evidence found",
            "interface_evidence": evidence,
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
    """Detect deviations between PRD intent and actual code.

    Checks:
    1. Tech stack mismatch: PRD says X but code uses Y
    2. Architecture deviation: PRD says cloud but code uses local storage
    3. Scope creep: Code has features not in PRD
    """
    deviations = []
    p = Path(project_dir)

    # Check tech stack deviation
    pkg_json = p / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
            all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            # Check for database mismatch
            prd_text = json.dumps(prd_summary, ensure_ascii=False).lower()
            if "云端" in prd_text or "云数据库" in prd_text:
                # PRD says cloud, but check if code uses local storage
                local_storage_usage = False
                for f in p.rglob("*.{js,jsx,ts,tsx}"):
                    content = safe_read_file(f)
                    if content and "localStorage" in content:
                        local_storage_usage = True
                        break
                if local_storage_usage:
                    deviations.append({
                        "type": "tech_mismatch",
                        "feature": "数据存储",
                        "prd_says": "云端数据库",
                        "code_says": "localStorage",
                        "severity": "high",
                        "suggestion": "PRD 要求云端存储但代码使用了 localStorage，需要确认是否需要修改"
                    })

            # Check for scope creep: code has features not mentioned in PRD
            core_features = prd_summary.get("core_features", "")
            if "auth" in all_deps and "登录" not in core_features and "auth" not in core_features:
                deviations.append({
                    "type": "scope_creep",
                    "feature": "认证系统",
                    "prd_says": "未提及",
                    "code_says": f"Found auth dependency: {[k for k in all_deps if 'auth' in k.lower()]}",
                    "severity": "medium",
                    "suggestion": "代码中存在认证相关依赖但 PRD 未提及，请确认是否在范围内"
                })

        except Exception:
            pass

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
