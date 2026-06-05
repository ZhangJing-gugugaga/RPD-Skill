#!/usr/bin/env python3
"""Scan project code for hardcoded secrets and prompt injection attempts.

Usage: python security-scanner.py <project-directory> [--state-file <path>]

Exit codes:
  0 - No security issues found
  1 - Usage error or file not readable
  2 - Security issues detected (hard block)
"""

import json
import re
import sys
from pathlib import Path

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

        # Read file content
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Scan each line
        for line_num, line in enumerate(content.split("\n"), 1):
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


def scan_for_injection(state_file_path):
    """Scan state file for prompt injection attempts. Returns list of findings."""
    findings = []
    path = Path(state_file_path)

    if not path.exists():
        return findings

    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return findings

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
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

    # Scan project code for secrets
    secret_findings = scan_for_secrets(project_dir)
    all_findings.extend(secret_findings)

    # Scan state file for injection (if provided)
    if state_file:
        injection_findings = scan_for_injection(state_file)
        all_findings.extend(injection_findings)

    # Report
    if all_findings:
        print(json.dumps({
            "status": "BLOCKED",
            "total_findings": len(all_findings),
            "findings": all_findings,
        }, indent=2, ensure_ascii=False))
        return 2

    print(json.dumps({"status": "CLEAR", "total_findings": 0}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
