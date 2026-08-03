#!/usr/bin/env python3
"""RPD v2 decisions.md append-only decision log with grill-me flow.

Each decision follows the format:
## D-<n> <Title>
- **date**: YYYY-MM-DD
- **type**: 技术选型 | 架构模式 | 安全策略 | 业务逻辑 | 范围 | 其他
- **status**: proposed | accepted | rejected | superseded
- **decision**: <one-line decision>
- **reason**: <why>
- **impact**: <affected scope>
- **confirmed_by**: <user confirmation record>

Write authority (R-14, Q5, hard constraint):
- agent MAY write decisions.md, but EVERY decision must be grilled to the
  user BEFORE it is confirmed. Only proposed can be written pre-confirmation.
- user confirms -> accepted + confirmed_by; user vetoes -> rejected;
  replaced by later decision -> superseded (new entry points via supersedes).

Usage:
  python rpd-decisions.py <project-root> propose "<title>" --decision "..." --type 技术选型 --reason "..." --impact "..."
  python rpd-decisions.py <project-root> accept <n> --confirmed-by "<user/time>"
  python rpd-decisions.py <project-root> reject <n>
  python rpd-decisions.py <project-root> supersede <n> --by <new-n>
  python rpd-decisions.py <project-root> list [--json]

Exit codes:
  0 - Success
  1 - Usage error
  3 - Not found / invalid
"""

import json
import re
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

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TYPES = ["技术选型", "架构模式", "安全策略", "业务逻辑", "范围", "其他"]


def decisions_path(project_root):
    return Path(project_root) / ".rpd" / "decisions.md"


def ensure_file(project_root):
    path = decisions_path(project_root)
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text("# 决策日志（decisions.md）\n\n> 追加式日志。所有决策在确定前必须先经 grill-me 拷问用户确认。\n\n", encoding="utf-8")
    return path


def next_dnum(path):
    content = smart_read(str(path)) or ""
    nums = [int(m) for m in re.findall(r'^## D-(\d+)', content, re.MULTILINE)]
    return max(nums) + 1 if nums else 1


def get_entry(path, n):
    content = smart_read(str(path)) or ""
    pattern = re.compile(rf'^## D-{n} .*?(?=^## D-|\Z)', re.MULTILINE | re.DOTALL)
    m = pattern.search(content)
    if not m:
        return None, None
    block = m.group(0).strip()
    title = block.split("\n", 1)[0].replace(f"## D-{n} ", "")
    fields = {}
    for line in block.split("\n"):
        fm = re.match(r'^- \*\*(\w+)\*\*: (.+)$', line.strip())
        if fm:
            fields[fm.group(1)] = fm.group(2)
    return block, {"title": title, **fields}


def replace_entry(path, n, new_block):
    content = smart_read(str(path)) or ""
    pattern = re.compile(rf'^## D-{n} .*?(?=^## D-|\Z)', re.MULTILINE | re.DOTALL)
    content, count = pattern.subn(new_block.strip() + "\n\n", content, count=1)
    path.write_text(content, encoding="utf-8")
    return count


def cmd_propose(root, args):
    if len(args) < 3:
        print("Usage: propose \"<title>\" --decision D --type T --reason R --impact I", file=sys.stderr)
        return 1
    title = args[0]
    opts = _parse_opts(args[1:])
    decision = opts.get("--decision", "")
    dtype = opts.get("--type", "其他")
    reason = opts.get("--reason", "")
    impact = opts.get("--impact", "")
    if dtype not in TYPES:
        dtype = "其他"
    if not decision:
        print("Error: --decision required", file=sys.stderr)
        return 1
    path = ensure_file(root)
    n = next_dnum(path)
    today = datetime.now().strftime("%Y-%m-%d")
    block = (
        f"## D-{n} {title}\n"
        f"- **date**: {today}\n"
        f"- **type**: {dtype}\n"
        f"- **status**: proposed\n"
        f"- **decision**: {decision}\n"
        f"- **reason**: {reason}\n"
        f"- **impact**: {impact}\n"
        f"- **confirmed_by**: 未确认（grill-me 待用户确认）\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block + "\n")
    print(f"D-{n} proposed 已写入 {path.as_posix()}")
    print(f"⚠️ grill-me 前置：D-{n} 必须经用户确认后才可 accept。")
    return 0


def _parse_opts(args):
    opts = {}
    for i, a in enumerate(args):
        if a.startswith("--") and i + 1 < len(args):
            opts[a] = args[i + 1]
    return opts


def cmd_status(root, n, status, extra_fields=None):
    path = ensure_file(root)
    block, entry = get_entry(path, n)
    if block is None:
        print(f"Error: D-{n} not found", file=sys.stderr)
        return 3
    lines = []
    for line in block.split("\n"):
        if line.startswith("- **status**"):
            lines.append(f"- **status**: {status}")
        elif status == "accepted" and line.startswith("- **confirmed_by**"):
            cb = extra_fields.get("--confirmed-by", "") if extra_fields else ""
            lines.append(f"- **confirmed_by**: {cb}" if cb else line)
        elif status == "superseded" and line.startswith("- **confirmed_by**"):
            by = extra_fields.get("--by", "") if extra_fields else ""
            lines.append(f"- **superseded_by**: D-{by}" if by else line)
        else:
            lines.append(line)
    new_block = "\n".join(lines)
    replace_entry(path, n, new_block)
    print(f"D-{n} -> {status}")
    return 0


def cmd_list(root, as_json=False):
    path = ensure_file(root)
    content = smart_read(str(path)) or ""
    entries = []
    for m in re.finditer(r'^## D-(\d+) (.+?)\n((?:^- \*\*.*\n)+)', content, re.MULTILINE):
        n = int(m.group(1))
        title = m.group(2)
        fields = {}
        for line in m.group(3).split("\n"):
            fm = re.match(r'^- \*\*(\w+)\*\*: (.+)$', line.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2)
        entries.append({"n": n, "title": title, **fields})
    if as_json:
        print(json.dumps(entries, indent=2, ensure_ascii=False))
    else:
        if not entries:
            print("No decisions yet.")
        for e in entries:
            print(f"D-{e['n']} [{e.get('status','?')}] {e['title']}: {e.get('decision','')}")
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    root = args[0]
    if len(args) < 2:
        print("Error: missing command (propose|accept|reject|supersede|list)", file=sys.stderr)
        return 1
    cmd = args[1]
    rest = args[2:]
    if cmd == "propose":
        return cmd_propose(root, rest)
    if cmd == "list":
        return cmd_list(root, "--json" in rest)
    if cmd in ("accept", "reject", "supersede"):
        if not rest or not rest[0].isdigit():
            print(f"Error: {cmd} requires decision number", file=sys.stderr)
            return 1
        n = int(rest[0])
        status = {"accept": "accepted", "reject": "rejected", "supersede": "superseded"}[cmd]
        return cmd_status(root, n, status, _parse_opts(rest[1:]))
    print(f"Error: unknown command '{cmd}'", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
