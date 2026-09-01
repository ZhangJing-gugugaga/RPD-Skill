#!/usr/bin/env python3
"""RPD v2 decisions.md decision log with grill-me flow + write-time reconciliation.

Each decision follows the format:
## D-<n> <Title>
- **date**: YYYY-MM-DD
- **type**: 技术选型 | 架构模式 | 安全策略 | 业务逻辑 | 范围 | 其他
- **status**: proposed | accepted | rejected | superseded
- **decision**: <one-line decision>
- **reason**: <why>
- **impact**: <affected scope>
- **confirmed_by**: <user confirmation record>
- **anchor**: <file>:<line>[@<commit>]   (optional, machine-verifiable)
- **confidence**: high | medium | low    (downgraded when anchor breaks)
- **modified**: <ISO timestamp>

Write authority (R-14, Q5, hard constraint):
- agent MAY write decisions.md, but EVERY decision must be grilled to the
  user BEFORE it is confirmed. Only proposed can be written pre-confirmation.
- user confirms -> accepted + confirmed_by; user vetoes -> rejected;
  replaced by later decision -> superseded (new entry points via supersedes).

Write-time reconciliation (mem0 ADD/UPDATE/DELETE/NOOP operators, anti
contradiction-stacking): `reconcile "<decision text>"` classifies the write
before it lands — NOOP (exact duplicate), UPDATE (supersedes contradicting
entry), or ADD (new). Purely deterministic text heuristics; ambiguity is
reported, never silently dropped.

All mutations go through timestamped backups + atomic replace (the old
direct write_text bypassed every protection — P2-3).

Usage:
  python rpd-decisions.py <project-root> propose "<title>" --decision "..." --type 技术选型 --reason "..." --impact "..." [--anchor "<file>:<line>"] [--commit "<sha>"] [--confidence high]
  python rpd-decisions.py <project-root> accept <n> --confirmed-by "<user/time>"
  python rpd-decisions.py <project-root> reject <n>
  python rpd-decisions.py <project-root> supersede <n> --by <new-n>
  python rpd-decisions.py <project-root> reconcile "<decision text>" [--json]
  python rpd-decisions.py <project-root> verify        [--json]   # anchor checks
  python rpd-decisions.py <project-root> list [--json]

Exit codes:
  0 - Success
  1 - Usage error
  3 - Not found / invalid
  2 - verify found broken anchors (downgraded)
"""

import json
import os
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
MAX_BACKUPS = 10
CONTRADICTION_MARKERS = re.compile(
    r"改用|改为|改用|弃用|不再使用|下线|替换|切换到|instead of|replace|switch to|deprecate",
    re.IGNORECASE,
)
_STOPWORDS = {"的", "了", "和", "与", "在", "是", "用", "为", "及", "或", "the",
              "a", "an", "of", "to", "for", "and", "with", "by"}


def decisions_path(project_root):
    return Path(project_root) / ".rpd" / "decisions.md"


def _now_ts():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _backup(path):
    """Timestamped backup of decisions.md (keep MAX_BACKUPS)."""
    if not path.exists():
        return None
    bdir = path.parent / "decisions-backups"
    bdir.mkdir(exist_ok=True)
    dest = bdir / f"decisions-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.md"
    dest.write_text(smart_read(str(path)) or "", encoding="utf-8")
    backups = sorted(bdir.glob("decisions-*.md"))
    for old in backups[:-MAX_BACKUPS]:
        try:
            old.unlink()
        except OSError:
            pass
    return dest


def _atomic_write(path, content):
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def ensure_file(project_root):
    path = decisions_path(project_root)
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        _atomic_write(path, "# 决策日志（decisions.md）\n\n> 所有决策在确定前必须先经 grill-me 拷问用户确认；写入前先 reconcile 对账。\n\n")
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
    """Replace one entry with backup + atomic write (P2-3 fix)."""
    _backup(path)
    content = smart_read(str(path)) or ""
    pattern = re.compile(rf'^## D-{n} .*?(?=^## D-|\Z)', re.MULTILINE | re.DOTALL)
    content, count = pattern.subn(new_block.strip() + "\n\n", content, count=1)
    if count:
        _atomic_write(path, content)
    return count


def _tokens(text):
    """Significant tokens of a decision text for overlap comparison."""
    return {t for t in re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
            if len(t) >= 2 and t not in _STOPWORDS}


def _normalize(text):
    return re.sub(r"\s+", "", text).lower()


def cmd_propose(root, args):
    if len(args) < 3:
        print("Usage: propose \"<title>\" --decision D --type T --reason R --impact I "
              "[--anchor f:l] [--commit sha] [--confidence high]", file=sys.stderr)
        return 1
    title = args[0]
    opts = _parse_opts(args[1:])
    decision = opts.get("--decision", "")
    dtype = opts.get("--type", "其他")
    reason = opts.get("--reason", "")
    impact = opts.get("--impact", "")
    anchor = opts.get("--anchor", "")
    commit = opts.get("--commit", "")
    confidence = opts.get("--confidence", "high" if anchor else "medium")
    if confidence not in ("high", "medium", "low"):
        confidence = "medium"
    if dtype not in TYPES:
        dtype = "其他"
    if not decision:
        print("Error: --decision required", file=sys.stderr)
        return 1
    path = ensure_file(root)
    n = next_dnum(path)
    today = datetime.now().strftime("%Y-%m-%d")
    anchor_val = anchor + (f"@{commit}" if commit else "")
    block = (
        f"## D-{n} {title}\n"
        f"- **date**: {today}\n"
        f"- **type**: {dtype}\n"
        f"- **status**: proposed\n"
        f"- **decision**: {decision}\n"
        f"- **reason**: {reason}\n"
        f"- **impact**: {impact}\n"
        f"- **confirmed_by**: 未确认（grill-me 待用户确认）\n"
        f"- **anchor**: {anchor_val or '无'}\n"
        f"- **confidence**: {confidence}\n"
        f"- **modified**: {_now_ts()}\n"
    )
    _backup(path)
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
        elif line.startswith("- **modified**"):
            lines.append(f"- **modified**: {_now_ts()}")
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


def cmd_reconcile(root, text, as_json=False):
    """Classify a pending decision write: NOOP | UPDATE(supersede) | ADD.

    Deterministic heuristics only:
      - normalized exact match -> NOOP
      - contradiction marker + significant-token overlap with an accepted
        entry -> UPDATE (the new write supersedes the old entry)
      - otherwise ADD, with any partial overlaps reported for review.
    """
    path = ensure_file(root)
    entries = []
    content = smart_read(str(path)) or ""
    for m in re.finditer(r'^## D-(\d+) (.+?)\n((?:^- \*\*.*\n)+)', content, re.MULTILINE):
        fields = {}
        for line in m.group(3).split("\n"):
            fm = re.match(r'^- \*\*(\w+)\*\*: (.+)$', line.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2)
        if fields.get("status") in ("accepted", "proposed"):
            entries.append({"n": int(m.group(1)), **fields})

    norm = _normalize(text)
    new_tokens = _tokens(text)

    for e in entries:
        if _normalize(e.get("decision", "")) == norm and norm:
            result = {"operator": "NOOP", "duplicate_of": f"D-{e['n']}",
                      "note": "完全相同的决策已存在，无需重复写入"}
            break
    else:
        conflicts = []
        for e in entries:
            old_tokens = _tokens(e.get("decision", "") + " " + e.get("title", ""))
            overlap = new_tokens & old_tokens
            if overlap and CONTRADICTION_MARKERS.search(text):
                conflicts.append((e, overlap))
        if conflicts:
            result = {"operator": "UPDATE",
                      "supersedes": [f"D-{e['n']}" for e, _ in conflicts],
                      "note": ("检测到改用/替换语义且主题重叠：新决策应 supersedes 旧条目"
                               "（propose 后用 supersede 关联），不要让两条矛盾决策并存")}
        else:
            partials = []
            for e in entries:
                old_tokens = _tokens(e.get("decision", "") + " " + e.get("title", ""))
                overlap = new_tokens & old_tokens
                if overlap:
                    partials.append(f"D-{e['n']} (重叠: {', '.join(sorted(overlap)[:4])})")
            result = {"operator": "ADD",
                      "note": "无确定性冲突；如主题相关请人工复核",
                      "related": partials[:5]}
    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"对账结果: {result['operator']}")
        print(f"  {result['note']}")
        for r in result.get("supersedes", []) or result.get("related", []):
            print(f"  - {r}")
    return 0


def cmd_verify(root, as_json=False):
    """Machine-verify anchors: broken anchors downgrade confidence (differential
    vs every other memory scheme: anchors are git-checkable, so staleness is
    scriptable, not vibes)."""
    path = decisions_path(root)
    if not path.exists():
        print(json.dumps({"checked": 0, "broken": []} if as_json else "No decisions.md.")
              if as_json else "No decisions.md.")
        return 0
    content = smart_read(str(path)) or ""
    broken = []
    checked = 0
    for m in re.finditer(r'^## D-(\d+) .*?(?=^## D-|\Z)', content, re.MULTILINE | re.DOTALL):
        block = m.group(0)
        am = re.search(r'^- \*\*anchor\*\*: (.+)$', block, re.MULTILINE)
        if not am:
            continue
        checked += 1
        anchor = am.group(1).strip()
        if anchor in ("无", ""):
            continue
        file_part = anchor.split("@")[0].strip()
        line_ref = None
        if ":" in file_part:
            file_part, _, line_s = file_part.rpartition(":")
            try:
                line_ref = int(line_s)
            except ValueError:
                line_ref = None
        p = Path(root) / file_part
        ok = p.is_file()
        if ok and line_ref is not None:
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
                ok = 1 <= line_ref <= len(lines)
            except OSError:
                ok = False
        if not ok:
            broken.append({"n": f"D-{m.group(1)}", "anchor": anchor})
            new_block = block.replace(
                f"- **confidence**: high", "- **confidence**: low").replace(
                f"- **confidence**: medium", "- **confidence**: low")
            if "**confidence**" not in new_block:
                new_block = new_block.replace(
                    "- **modified**:", f"- **confidence**: low\n- **modified**:")
            new_block = re.sub(
                r'(- \*\*modified\*\*: )\S+',
                rf'\g<1>{_now_ts()}', new_block)
            replace_entry(path, int(m.group(1)), new_block)
    if as_json:
        print(json.dumps({"checked": checked, "broken": broken}, indent=2, ensure_ascii=False))
    else:
        print(f"锚点校验: {checked} 条带锚点，{len(broken)} 条失效降级")
        for b in broken:
            print(f"  - {b['n']}: {b['anchor']}（confidence -> low）")
    return 0 if not broken else 2


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
        print("Error: missing command (propose|accept|reject|supersede|reconcile|verify|list)",
              file=sys.stderr)
        return 1
    cmd = args[1]
    rest = args[2:]
    if cmd == "propose":
        return cmd_propose(root, rest)
    if cmd == "list":
        return cmd_list(root, "--json" in rest)
    if cmd == "reconcile":
        if not rest:
            print("Error: reconcile requires decision text", file=sys.stderr)
            return 1
        return cmd_reconcile(root, rest[0], "--json" in rest[1:])
    if cmd == "verify":
        return cmd_verify(root, "--json" in rest)
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
