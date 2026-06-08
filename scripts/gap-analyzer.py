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

# Fix Windows encoding for JSON output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
    seen = set()

    # Express/Go-Gin style routes (including single letter variables like r.GET)
    route_pattern = re.compile(
        r'(?:app|router|server|r)\.(get|post|put|delete|patch|all)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    # Flask route with methods parameter
    flask_route_pattern = re.compile(
        r'@(?:app|router|api)\.route\s*\(\s*["\']([^"\']+)["\'].*?methods\s*=\s*\[([^\]]+)\]',
        re.DOTALL
    )

    # Simple Flask/FastAPI decorator routes
    py_route_pattern = re.compile(
        r'@(?:app|router|api)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    code_extensions = {".js", ".ts", ".go", ".py"}
    for ext in code_extensions:
        for f in p.rglob(f"*{ext}"):
            parts = f.relative_to(p).parts
            if any(skip in parts for skip in SKIP_DIRS):
                continue
            content = safe_read_file(f)
            if content is None:
                continue
            rel_path = str(f.relative_to(p)).replace("\\", "/")

            # Express/Go-Gin style
            for match in route_pattern.finditer(content):
                key = (match.group(1).upper(), match.group(2), rel_path)
                if key not in seen:
                    seen.add(key)
                    routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": rel_path})

            # Flask route with methods
            for match in flask_route_pattern.finditer(content):
                path = match.group(1)
                methods = [m.strip().strip('"\'').upper() for m in match.group(2).split(",")]
                for method in methods:
                    key = (method, path, rel_path)
                    if key not in seen:
                        seen.add(key)
                        routes.append({"method": method, "path": path, "file": rel_path})

            # Simple decorator routes
            for match in py_route_pattern.finditer(content):
                key = (match.group(1).upper(), match.group(2), rel_path)
                if key not in seen:
                    seen.add(key)
                    routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": rel_path})

    # Java Spring routes
    spring_route_pattern = re.compile(
        r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    METHOD_MAP = {
        "GetMapping": "GET", "PostMapping": "POST",
        "PutMapping": "PUT", "DeleteMapping": "DELETE",
        "PatchMapping": "PATCH", "RequestMapping": "ALL",
    }
    for f in p.rglob("*.java"):
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue
        content = safe_read_file(f)
        if content is None:
            continue
        rel_path = str(f.relative_to(p)).replace("\\", "/")
        for match in spring_route_pattern.finditer(content):
            method = METHOD_MAP.get(match.group(1), "ALL")
            key = (method, match.group(2), rel_path)
            if key not in seen:
                seen.add(key)
                routes.append({"method": method, "path": match.group(2), "file": rel_path})

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

        rel_path = str(f.relative_to(p)).replace("\\", "/")

        # React Router
        for match in react_route_pattern.finditer(content):
            page_routes.append({"path": match.group(1), "component": match.group(2), "file": rel_path})

        # Vue Router
        for match in vue_route_pattern.finditer(content):
            page_routes.append({"path": match.group(1), "component": match.group(2), "file": rel_path})

        # Next.js file-based routing
        next_match = next_page_pattern.match(rel_path)
        if next_match:
            page_path = "/" + next_match.group(1).replace("\\", "/")
            if page_path.endswith("/index"):
                page_path = page_path[:-6] or "/"
            page_routes.append({"path": page_path, "component": f.stem, "file": rel_path})

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

        rel_path = str(f.relative_to(p)).replace("\\", "/")

        # Prisma
        for match in prisma_pattern.finditer(content):
            models.append({"name": match.group(1), "type": "prisma", "file": rel_path})

        # SQLAlchemy
        for match in sqlalchemy_pattern.finditer(content):
            models.append({"name": match.group(1), "type": "sqlalchemy", "file": rel_path})

        # Mongoose
        for match in mongoose_pattern.finditer(content):
            name = match.group(1) or match.group(2)
            models.append({"name": name, "type": "mongoose", "file": rel_path})

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
        # Auth & User
        "登录": ["login", "signin", "auth"],
        "注册": ["register", "signup"],
        "用户": ["user", "profile"],
        "权限": ["permission", "role", "access"],
        "密码": ["password", "pwd"],
        # CRUD
        "添加": ["add", "create", "new"],
        "创建": ["create", "new", "add"],
        "编辑": ["edit", "update", "modify"],
        "删除": ["delete", "remove", "destroy"],
        "修改": ["update", "modify", "edit"],
        # Data display
        "列表": ["list", "index", "table"],
        "详情": ["detail", "show", "view"],
        "信息": ["info", "detail", "profile"],
        # Search & Filter
        "搜索": ["search", "filter", "find"],
        "查询": ["query", "search", "find"],
        "筛选": ["filter", "筛选"],
        # Import & Export
        "导出": ["export", "download"],
        "导入": ["import", "upload"],
        "上传": ["upload", "import"],
        "下载": ["download", "export"],
        # Todo & Task
        "待办": ["todo", "task"],
        "任务": ["task", "todo", "job"],
        "标记": ["mark", "flag", "tag"],
        "完成": ["complete", "done", "finish"],
        # Communication
        "通知": ["notification", "alert", "message"],
        "消息": ["message", "notification", "msg"],
        "评论": ["comment", "review"],
        "回复": ["reply", "respond", "comment"],
        # Social
        "收藏": ["favorite", "bookmark"],
        "分享": ["share"],
        "点赞": ["like", "favorite"],
        "关注": ["follow", "subscribe"],
        # Commerce
        "支付": ["payment", "pay", "checkout"],
        "订单": ["order"],
        "购物": ["cart", "shopping"],
        "商品": ["product", "goods", "item"],
        # Settings & Config
        "设置": ["setting", "config", "preference"],
        "配置": ["config", "setting", "configuration"],
        # Analytics & Reports
        "报表": ["report", "chart", "analytics"],
        "统计": ["statistics", "stats", "summary"],
        "分析": ["analytics", "analysis"],
        # Pagination
        "分页": ["pagination", "paginate", "pager"],
        # Accounting
        "记账": ["accounting", "ledger", "transaction"],
        "账单": ["bill", "invoice", "statement"],
        # Category
        "分类": ["category", "classify"],
        # Submit & Review
        "提交": ["submit", "post"],
        "审核": ["review", "audit", "approve"],
        "审批": ["approve", "review"],
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


def detect_security_gaps(project_dir):
    """Detect missing security measures in the codebase.

    Checks for common security gaps in Vibe Coding projects:
    1. SMS/Email service without rate limiting
    2. File upload without cloud storage
    3. AI features without content moderation
    4. Missing authentication dependencies
    """
    gaps = []
    p = Path(project_dir)
    pkg_json = p / "package.json"

    if not pkg_json.exists():
        return gaps

    try:
        pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
        all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

        # SMS/Email without rate limiting
        has_sms = any(k in all_deps for k in ["twilio", "aliyun-sms", "nodemailer", "sendgrid", "aliyun-dysms"])
        has_rate_limit = any(k in all_deps for k in ["express-rate-limit", "rate-limiter", "bottleneck", "rate-limit-flexible"])
        if has_sms and not has_rate_limit:
            gaps.append({
                "type": "missing_security",
                "feature": "频率限制",
                "feature_en": "Rate Limiting",
                "severity": "CRITICAL",
                "message": "项目使用了短信/邮件服务但未安装频率限制库",
                "message_en": "Project uses SMS/Email service but has no rate limiting library",
                "recommendation": "npm install express-rate-limit",
            })

        # File upload without cloud storage
        has_upload = any(k in all_deps for k in ["multer", "formidable", "busboy", "express-fileupload"])
        has_cloud = any(k in all_deps for k in ["aliyun-oss", "aws-sdk", "@aws-sdk/client-s3", "qiniu", "cos-nodejs-sdk-v5"])
        if has_upload and not has_cloud:
            gaps.append({
                "type": "missing_security",
                "feature": "云存储",
                "feature_en": "Cloud Storage",
                "severity": "MEDIUM",
                "message": "项目使用了文件上传但未集成云对象存储",
                "message_en": "Project uses file upload but has no cloud object storage integration",
                "recommendation": "集成阿里云OSS或AWS S3，避免本地磁盘存储",
            })

        # AI without content moderation
        has_ai = any(k in all_deps for k in ["openai", "anthropic", "langchain", "@anthropic-ai/sdk", "zhipu-ai", "baidu-ai"])
        has_moderation = any(k in all_deps for k in ["aliyun-green", "nsfwjs", "content-moderation", "tencent-ai"])
        if has_ai and not has_moderation:
            gaps.append({
                "type": "missing_security",
                "feature": "内容审核",
                "feature_en": "Content Moderation",
                "severity": "HIGH",
                "message": "项目使用了AI功能但未集成内容安全审核",
                "message_en": "Project uses AI features but has no content safety/moderation integration",
                "recommendation": "接入内容安全API，对AI输出进行合规审核",
            })

        # Web framework without security headers
        has_web = any(k in all_deps for k in ["express", "koa", "fastify", "hapi"])
        has_helmet = any(k in all_deps for k in ["helmet", "lusca", "express-csp"])
        if has_web and not has_helmet:
            gaps.append({
                "type": "missing_security",
                "feature": "安全头",
                "feature_en": "Security Headers",
                "severity": "LOW",
                "message": "Web 框架未配置安全响应头",
                "message_en": "Web framework has no security headers configured",
                "recommendation": "npm install helmet，添加安全响应头",
            })

    except Exception:
        pass

    return gaps


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
    security_gaps = detect_security_gaps(project_dir)

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
        "security_gaps": security_gaps,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
