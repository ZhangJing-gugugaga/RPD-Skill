#!/usr/bin/env python3
"""Scan project code for hardcoded secrets, prompt injection, and business-level security issues.

Usage: python security-scanner.py <project-directory> [--state-file <path>]

Exit codes:
  0 - No security issues found
  1 - Usage error or file not readable
  2 - Security issues detected (hard block)
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

# --- Secret detection patterns ---

SECRET_PATTERNS = [
    # API Keys
    (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\'][A-Za-z0-9_\-]{20,}["\']', "Hardcoded API key"),
    (r'(?:secret[_-]?key|secretkey)\s*[=:]\s*["\'][A-Za-z0-9_\-]{16,}["\']', "Hardcoded secret key"),
    # AWS
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'(?:aws[_-]?secret)\s*[=:]\s*["\'][A-Za-z0-9/+]{40}["\']', "AWS Secret Access Key"),
    # Tokens
    (r'(?:token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\'][A-Za-z0-9_\-.]{20,}["\']', "Hardcoded token"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI-style API key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
    (r'glpat-[A-Za-z0-9\-]{20,}', "GitLab Personal Access Token"),
    # Passwords
    (r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']', "Hardcoded password"),
    # Private keys
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private key in code"),
    # Generic high-entropy strings assigned to sensitive-looking variables
    (r'(?:secret|key|token|password|credential)\s*=\s*["\'][A-Za-z0-9+/=_\-]{32,}["\']', "Possible hardcoded secret"),
]

# --- Code-level security rules (business logic) ---

CODE_SECURITY_RULES = [
    # SEC-001: SMS/Email API without rate limiting
    {
        "id": "SEC-001",
        "name": "SMS/Email API without rate limiting",
        "name_zh": "短信/邮件发送接口缺少频率限制",
        "pattern": r'(?:sendSMS|sendEmail|sendCode|sendVerification|sendVerify)\s*\(',
        "check": lambda content, match: "rateLimit" not in content and "rate-limit" not in content and "rateLimiter" not in content,
        "severity": "CRITICAL",
        "message": "SMS/Email sending API lacks rate limiting, vulnerable to bombing attacks",
        "message_zh": "短信/邮件发送接口缺少频率限制，易被短信轰炸攻击",
        "recommendation": "Add rate-limit middleware, set daily limit per phone/IP",
        "recommendation_zh": "添加 rate-limit middleware，设置单手机号/IP 每日上限",
    },
    # SEC-002: UGC write without content moderation
    {
        "id": "SEC-002",
        "name": "UGC write without content moderation",
        "name_zh": "用户生成内容(UGC)写入无审核机制",
        "pattern": r'(?:Comment|Post|Wish|Message|Review|Article|Reply)\.create\s*\(',
        "check": lambda context, match: not re.search(
            r'(?:contentModerat|moderat(?:e|ion)|audit|contentSafe)\s*\(|审核\s*\(',
            context, re.IGNORECASE
        ),
        "severity": "CRITICAL",
        "message": "User-generated content written without moderation, risk of illegal content",
        "message_zh": "用户生成内容写入无审核机制，存在违法违规内容传播风险",
        "recommendation": "Integrate content safety API (e.g., Aliyun Green/NetEase Yidun), implement review-before-publish",
        "recommendation_zh": "接入内容安全API（网易易盾/阿里云内容安全），实现先审后发",
    },
    # SEC-003: File upload without type validation
    {
        "id": "SEC-003",
        "name": "File upload without type validation",
        "name_zh": "文件上传缺少文件类型校验",
        "pattern": r'multer\s*\(\s*\{[^}]*storage',
        "check": lambda content, match: "fileFilter" not in content,
        "severity": "HIGH",
        "message": "File upload lacks file type validation, malicious files may be uploaded",
        "message_zh": "文件上传缺少文件类型校验，可能被上传恶意文件",
        "recommendation": "Add fileFilter to restrict allowed types (jpg/png/gif), limit file size",
        "recommendation_zh": "添加 fileFilter 限制允许的文件类型（jpg/png/gif），限制文件大小",
    },
    # SEC-004: File storage on local disk
    {
        "id": "SEC-004",
        "name": "File storage on local disk",
        "name_zh": "文件存储在服务器本地磁盘",
        "pattern": r'diskStorage\s*\(',
        "check": lambda content, match: True,
        "severity": "MEDIUM",
        "message": "Files stored on local disk, risk of link theft and disk exhaustion",
        "message_zh": "文件存储在服务器本地磁盘，存在被盗链和磁盘占满风险",
        "recommendation": "Migrate to cloud object storage (Aliyun OSS/AWS S3), enable anti-leech",
        "recommendation_zh": "迁移至云对象存储（阿里云OSS/AWS S3），设置防盗链",
    },
    # SEC-005: Hardcoded System Prompt
    {
        "id": "SEC-005",
        "name": "Hardcoded System Prompt",
        "name_zh": "AI System Prompt 硬编码在代码中",
        "pattern": r'(?:SYSTEM_PROMPT|system_prompt|systemPrompt|SYSTEM_MESSAGE)\s*=\s*[`"\']',
        "check": lambda content, match: True,
        "severity": "HIGH",
        "message": "AI System Prompt hardcoded in code, risk of leakage",
        "message_zh": "AI System Prompt 硬编码在代码中，存在泄露风险",
        "recommendation": "Separate System Prompt from code, store in env vars or encrypted config",
        "recommendation_zh": "将 System Prompt 从代码中分离，存储在环境变量或加密配置文件中",
    },
    # SEC-006: Direct file URL without access control
    {
        "id": "SEC-006",
        "name": "Direct file URL without access control",
        "name_zh": "文件URL直接可访问，无防盗链保护",
        "pattern": r'res\.json\s*\(\s*\{[^}]*url.*(?:uploads|files|static)',
        "check": lambda content, match: "signed" not in content.lower() and "token" not in content.lower() and "referer" not in content.lower(),
        "severity": "MEDIUM",
        "message": "File URLs directly accessible without anti-leech protection",
        "message_zh": "文件URL直接可访问，无防盗链保护",
        "recommendation": "Use signed URLs or Referer validation for anti-leech",
        "recommendation_zh": "使用签名URL或Referer校验实现防盗链",
    },
    # SEC-007: API route without authentication middleware
    {
        "id": "SEC-007",
        "name": "API route without authentication middleware",
        "name_zh": "API 路由缺少认证中间件",
        # Match Express/Go-Gin style routes: app/router/server/r.get/post/put/delete
        "pattern": r'(?:app|router|server|r)\.(get|post|put|delete|patch)\s*\(\s*[\'"][^\'"]+[\'"]',
        "check": lambda content, match: not re.search(
            r'(?:auth|authenticate|verify|protect|guard|checkLogin|isLoggedIn|requireAuth|ensureAuth)\s*\(',
            content, re.IGNORECASE
        ),
        "severity": "HIGH",
        "message": "API route lacks authentication middleware, accessible without login",
        "message_zh": "API 路由缺少认证中间件，未登录用户可直接访问",
        "recommendation": "Add auth middleware to verify JWT/Session",
        "recommendation_zh": "添加 auth middleware 验证 JWT/Session",
        "context_mode": "to_top",  # Use larger context window for this rule
    },
    # SEC-008: System Prompt constructed via string concatenation
    {
        "id": "SEC-008",
        "name": "System Prompt constructed via string concatenation",
        "name_zh": "AI System Prompt 通过字符串拼接构造",
        "pattern": r'(?:SYSTEM_PROMPT|system_prompt|systemPrompt|SYSTEM_MESSAGE)\s*=\s*\w+\s*\+',
        "check": lambda context, match: True,
        "severity": "LOW",
        "message": "System Prompt assembled via variable concatenation, may hide injection or leakage vectors",
        "message_zh": "System Prompt 通过变量拼接构造，可能存在注入或泄露风险",
        "recommendation": "Use a single literal string or encrypted config for System Prompt",
        "recommendation_zh": "使用单一字符串字面量或加密配置存储 System Prompt",
    },
]

# Sensitive files that shouldn't be in version control
SENSITIVE_FILES = {
    ".env": "Environment file with potential secrets",
    ".env.local": "Local environment overrides",
    ".env.production": "Production environment config",
    ".env.development": "Development environment config",
    ".npmrc": "npm config (may contain auth tokens)",
    ".pypirc": "PyPI config (may contain upload tokens)",
    ".htpasswd": "Apache password file",
    "id_rsa": "SSH private key",
    "id_ed25519": "SSH private key",
}

# Files to skip (binary, generated, dependencies)
SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2',
    '.ttf', '.eot', '.mp3', '.mp4', '.avi', '.mov', '.zip', '.tar',
    '.gz', '.rar', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.exe',
    '.map',
}

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
}

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB - skip files larger than this

# --- Prompt injection detection ---

INJECTION_PATTERNS = [
    r'ignore\s+(?:all\s+)?previous\s+instructions',
    r'you\s+are\s+now\s+(?:a|an)\s+',
    r'system\s*:\s*you\s+are',
    r'IMPORTANT\s*:\s*(?:ignore|disregard|forget)',
    r'<\s*system\s*>',
    r'```system',
    r'INST\s*:\s*(?:ignore|override)',
]


def should_skip_file(path):
    """Check if file should be skipped based on extension."""
    name = path.name.lower()
    for ext in SKIP_EXTENSIONS:
        if name.endswith(ext):
            return True
    return False


def should_skip_dir(dirname):
    """Check if directory should be skipped."""
    return dirname in SKIP_DIRS


def safe_read_file(path, max_size=MAX_FILE_SIZE):
    """Read file with size limit to prevent OOM."""
    try:
        if os.path.getsize(path) > max_size:
            return None
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def get_context_window(content, match_pos, window_lines=20, mode="fixed"):
    """Extract context window around a match position for function-level detection.

    Instead of checking the entire file for security measures, this extracts
    lines around the match to enable per-function (per-route) detection.

    Args:
        content: Full file content string
        match_pos: Character position of the match in content
        window_lines: Number of lines to extract in fixed mode
        mode: "fixed" for ±window_lines, "to_top" for scan to file top

    Returns:
        Extracted context string
    """
    lines = content.split("\n")
    match_line = content[:match_pos].count("\n")

    if mode == "to_top":
        # Scan from match position to file top (or to previous route definition)
        start = 0
        # Look for previous route definition to bound the context
        for i in range(match_line - 1, -1, -1):
            line = lines[i].strip()
            # Stop at previous route definition or top-level function
            if re.match(r'(?:app|router|server|r)\.(get|post|put|delete|patch)\s*\(', line, re.IGNORECASE):
                start = i + 1
                break
            if re.match(r'@(?:app|router|api)\.(get|post|put|delete|patch)\s*\(', line, re.IGNORECASE):
                start = i + 1
            if re.match(r'@(?:app|router|api)\.route\s*\(', line, re.IGNORECASE):
                start = i + 1
            if re.match(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)', line, re.IGNORECASE):
                start = i + 1
        end = min(len(lines), match_line + window_lines + 1)
    else:
        # Fixed window mode (original behavior)
        start = max(0, match_line - window_lines)
        end = min(len(lines), match_line + window_lines + 1)

    return "\n".join(lines[start:end])


def scan_sensitive_files(project_dir):
    """Check for sensitive files that shouldn't be committed."""
    findings = []
    p = Path(project_dir)

    for filename, description in SENSITIVE_FILES.items():
        filepath = p / filename
        if filepath.exists():
            findings.append({
                "type": "sensitive_file",
                "file": str(filepath),
                "line": 0,
                "description": f"{description} — consider adding to .gitignore",
                "evidence": f"File exists: {filename}",
            })

    # Check .gitignore for missing entries
    gitignore = p / ".gitignore"
    if gitignore.exists():
        content = safe_read_file(gitignore)
        if content:
            for filename in SENSITIVE_FILES:
                if filename not in content:
                    findings.append({
                        "type": "missing_gitignore",
                        "file": ".gitignore",
                        "line": 0,
                        "description": f"{filename} not in .gitignore",
                        "evidence": f"Missing entry for {filename}",
                    })

    return findings


def scan_for_secrets(project_dir):
    """Scan project files for hardcoded secrets. Returns list of findings."""
    findings = []
    project_path = Path(project_dir)

    for path in project_path.rglob("*"):
        # Skip directories
        if path.is_dir():
            continue

        # Skip excluded dirs
        if any(should_skip_dir(part) for part in path.relative_to(project_path).parts):
            continue

        # Skip binary files
        if should_skip_file(path):
            continue

        # Read file content with size limit
        content = safe_read_file(path)
        if content is None:
            continue

        # Scan each line
        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern, description in SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "type": "secret",
                        "file": str(path),
                        "line": line_num,
                        "description": description,
                        "evidence": line.strip()[:100],
                    })

    return findings


def scan_code_security(project_dir):
    """Scan code for logic-level security issues (business security)."""
    findings = []
    p = Path(project_dir)
    seen = set()

    code_extensions = {".js", ".ts", ".py", ".jsx", ".tsx", ".go", ".java"}

    for f in p.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in code_extensions:
            continue

        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue

        content = safe_read_file(f)
        if content is None:
            continue

        rel_path = str(f.relative_to(p)).replace("\\", "/")

        for rule in CODE_SECURITY_RULES:
            for match in re.finditer(rule["pattern"], content, re.IGNORECASE):
                # Use rule-specific context mode if defined (e.g., SEC-007 uses "to_top")
                context_mode = rule.get("context_mode", "fixed")
                context_window = get_context_window(content, match.start(), mode=context_mode)
                if rule["check"](context_window, match):
                    key = (rule["id"], rel_path, match.start())
                    if key not in seen:
                        seen.add(key)
                        line_num = content[:match.start()].count("\n") + 1
                        findings.append({
                            "type": "code_security",
                            "rule_id": rule["id"],
                            "severity": rule["severity"],
                            "file": rel_path,
                            "line": line_num,
                            "description": rule["name"],
                            "description_zh": rule["name_zh"],
                            "message": rule["message"],
                            "message_zh": rule["message_zh"],
                            "recommendation": rule["recommendation"],
                            "recommendation_zh": rule["recommendation_zh"],
                            "evidence": content.split("\n")[line_num - 1].strip()[:100] if line_num <= len(content.split("\n")) else "",
                        })

    return findings


def scan_for_injection(state_file_path):
    """Scan state file for prompt injection attempts. Returns list of findings."""
    findings = []
    seen = set()
    path = Path(state_file_path)

    if not path.exists():
        return findings

    content = safe_read_file(path)
    if content is None:
        return findings

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                key = (str(path), line_num, pattern)
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        "type": "injection",
                        "file": str(path),
                        "line": line_num,
                        "description": "Possible prompt injection attempt",
                        "evidence": line.strip()[:100],
                    })

    return findings


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python security-scanner.py <project-directory> [--state-file <path>]")
        return 1

    project_dir = args[0]
    state_file = None

    if "--state-file" in args:
        idx = args.index("--state-file")
        if idx + 1 < len(args):
            state_file = args[idx + 1]

    if not Path(project_dir).is_dir():
        print(f"Error: Not a directory: {project_dir}", file=sys.stderr)
        return 1

    all_findings = []

    # Scan for sensitive files
    sensitive_findings = scan_sensitive_files(project_dir)
    all_findings.extend(sensitive_findings)

    # Scan project code for secrets
    secret_findings = scan_for_secrets(project_dir)
    all_findings.extend(secret_findings)

    # Scan for code-level security issues (business logic)
    code_security_findings = scan_code_security(project_dir)
    all_findings.extend(code_security_findings)

    # Scan state file for injection (if provided)
    if state_file:
        injection_findings = scan_for_injection(state_file)
        all_findings.extend(injection_findings)

    # Report
    if all_findings:
        # Categorize findings
        critical = [f for f in all_findings if f.get("severity") == "CRITICAL"]
        high = [f for f in all_findings if f.get("severity") == "HIGH"]
        medium = [f for f in all_findings if f.get("severity") == "MEDIUM"]
        other = [f for f in all_findings if f.get("severity") not in ("CRITICAL", "HIGH", "MEDIUM")]

        print(json.dumps({
            "status": "BLOCKED",
            "total_findings": len(all_findings),
            "summary": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "other": len(other),
            },
            "findings": all_findings,
        }, indent=2, ensure_ascii=False))
        return 2

    print(json.dumps({"status": "CLEAR", "total_findings": 0}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
