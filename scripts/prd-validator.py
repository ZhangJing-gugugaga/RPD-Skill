#!/usr/bin/env python3
"""Validate PRD completeness by checking feature sections and security checklist.

Usage: python prd-validator.py <prd-file> [--format json|text]

Exit codes:
  0 - All validations passed
  1 - Usage error
  2 - Gaps found (validation failed)

Output: JSON or text gap report to stdout.
"""

import json
import re
import sys
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

# --- Feature completeness check keywords ---

FEATURE_CHECKS = {
    "异常分支": {
        "name_en": "Error handling",
        "keywords": ["失败", "异常", "error", "fail", "错误", "exception", "fallback", "降级"],
    },
    "状态机": {
        "name_en": "State machine",
        "keywords": ["状态", "state", "状态机", "transition", "流转", "生命周期"],
    },
    "字段规范": {
        "name_en": "Field validation",
        "keywords": ["校验", "验证", "validation", "validate", "规则", "格式", "必填", "required"],
    },
    "文案规范": {
        "name_en": "Copy text",
        "keywords": ["文案", "copy", "提示文案", "提示语", "message", "toast", "alert", "反馈"],
    },
}


def safe_read_file(path, max_size=10 * 1024 * 1024):
    """Read file with size limit to prevent OOM."""
    try:
        if path.stat().st_size > max_size:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def parse_prd_features(content):
    """Parse PRD content to extract feature sections by ## or ### headings.

    Returns list of dicts with keys: name, content, line.
    """
    features = []
    lines = content.split("\n")
    current_feature = None
    current_content = []
    current_line = 0

    for i, line in enumerate(lines, 1):
        # Match ## to #### headings (feature sections)
        heading_match = re.match(r'^(#{2,4})\s+(.+)', line)
        if heading_match:
            # Save previous feature if exists
            if current_feature:
                features.append({
                    "name": current_feature,
                    "content": "\n".join(current_content),
                    "line": current_line,
                })
            current_feature = heading_match.group(2).strip()
            current_content = []
            current_line = i
        elif current_feature:
            current_content.append(line)

    # Don't forget the last feature
    if current_feature:
        features.append({
            "name": current_feature,
            "content": "\n".join(current_content),
            "line": current_line,
        })

    return features


def check_feature_completeness(feature):
    """Check if a feature section contains all required elements.

    Returns list of missing element names.
    """
    missing = []
    content_lower = feature["content"].lower()

    for check_name, check_info in FEATURE_CHECKS.items():
        found = False
        for keyword in check_info["keywords"]:
            if keyword.lower() in content_lower:
                found = True
                break
        if not found:
            missing.append(check_name)

    return missing


def parse_checklist(content):
    """Parse security checklist checkboxes in the PRD.

    Returns dict with total, completed, incomplete list.
    """
    total = 0
    completed = 0
    incomplete = []

    # Match [ ] and [x] checkboxes
    checkbox_pattern = re.compile(r'- \[([ xX])\]\s*(.+)', re.MULTILINE)

    for match in checkbox_pattern.finditer(content):
        total += 1
        is_checked = match.group(1).lower() == 'x'
        item_text = match.group(2).strip()

        if is_checked:
            completed += 1
        else:
            incomplete.append(item_text)

    return {
        "total": total,
        "completed": completed,
        "incomplete": incomplete,
    }


def validate_prd(prd_path):
    """Validate a PRD file for completeness.

    Returns validation result dict.
    """
    prd_file = Path(prd_path)
    if not prd_file.exists():
        return {"error": f"File not found: {prd_path}"}

    content = safe_read_file(prd_file)
    if content is None:
        return {"error": f"Cannot read file: {prd_path}"}

    # Parse features
    features = parse_prd_features(content)

    # Check each feature
    gaps = []
    for feature in features:
        # Skip non-feature headings (like "## 概述", "## 附录")
        if any(skip in feature["name"] for skip in ["概述", "附录", "术语", "参考", "变更", "overview", "appendix", "glossary"]):
            continue

        missing = check_feature_completeness(feature)
        if missing:
            gaps.append({
                "feature": feature["name"],
                "missing": missing,
                "line": feature["line"],
            })

    # Parse checklist
    checklist = parse_checklist(content)

    # Determine status
    has_gaps = len(gaps) > 0
    checklist_incomplete = checklist["total"] > 0 and checklist["completed"] < checklist["total"]
    status = "FAIL" if (has_gaps or checklist_incomplete) else "PASS"

    return {
        "status": status,
        "total_features": len([f for f in features if not any(skip in f["name"] for skip in ["概述", "附录", "术语", "参考", "变更", "overview", "appendix", "glossary"])]),
        "gaps": gaps,
        "checklist": checklist,
    }


def format_text_output(result):
    """Format validation result as human-readable text."""
    lines = []
    lines.append(f"PRD Validation: {result['status']}")
    lines.append(f"Total features: {result['total_features']}")
    lines.append("")

    if result["gaps"]:
        lines.append("Feature Gaps:")
        for gap in result["gaps"]:
            lines.append(f"  [{gap['line']}] {gap['feature']}: missing {', '.join(gap['missing'])}")
        lines.append("")

    checklist = result["checklist"]
    if checklist["total"] > 0:
        completion = checklist["completed"] / checklist["total"] * 100
        lines.append(f"Checklist: {checklist['completed']}/{checklist['total']} ({completion:.0f}%)")
        if checklist["incomplete"]:
            lines.append("  Incomplete:")
            for item in checklist["incomplete"]:
                lines.append(f"    - [ ] {item}")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python prd-validator.py <prd-file> [--format json|text]")
        return 1

    prd_file = args[0]
    output_format = "json"

    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            output_format = args[idx + 1]

    # Validate
    result = validate_prd(prd_file)

    if "error" in result:
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    # Output
    if output_format == "text":
        print(format_text_output(result))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
