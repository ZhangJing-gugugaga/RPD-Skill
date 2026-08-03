#!/usr/bin/env python3
"""RPD v2 metrics: capture and aggregate M1/M2/M3 primary metrics.

Primary metrics (multi-indicator, net_tokens_to_first_action is secondary only):
  M1 理解连续性 (continuity): does a fresh session retain project understanding
      via code-map (structure, key symbols, last progress, key decisions) without
      re-scanning? A/B: with-map vs without-map.
  M2 定位成本 (locate cost): time + token cost to locate a symbol/interface call
      relationship via map (entry lookup) vs re-scan.
  M3 文档引用 (doc ref): time + token cost to locate README/CHANGELOG/decision docs
      and their mapping to code.

Observations are appended to <project-root>/.rpd/metrics.jsonl (one JSON per line).
The aggregator reports the current summary.

Usage:
  python rpd-metrics.py <project-root> record --metric M1 --value 0.8 --unit continuity --notes "reused map, no rescan"
  python rpd-metrics.py <project-root> record --metric net_tokens_to_first_action --value 1200 --unit token --notes "secondary"
  python rpd-metrics.py <project-root> report [--json]

Exit codes:
  0 - Success
  1 - Usage error
"""

import json
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

PRIMARY_METRICS = {"M1", "M2", "M3"}
SECONDARY_METRICS = {"net_tokens_to_first_action"}


def metrics_path(project_root):
    return Path(project_root) / ".rpd" / "metrics.jsonl"


def cmd_record(root, args):
    """Record an observation. Primary M1/M2/M3 or secondary net_tokens."""
    opts = {}
    for i, a in enumerate(args):
        if a.startswith("--") and i + 1 < len(args):
            opts[a] = args[i + 1]
    metric = opts.get("--metric", "")
    if metric not in PRIMARY_METRICS and metric not in SECONDARY_METRICS:
        print(f"Error: unknown metric '{metric}'. Use M1|M2|M3 or net_tokens_to_first_action", file=sys.stderr)
        return 1
    try:
        value = float(opts.get("--value", "0"))
    except ValueError:
        print("Error: --value must be numeric", file=sys.stderr)
        return 1
    rec = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metric": metric,
        "value": value,
        "unit": opts.get("--unit", ""),
        "notes": opts.get("--notes", ""),
    }
    path = metrics_path(root)
    path.parent.mkdir(exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"recorded {metric}={value} {rec['unit']}")
    return 0


def cmd_report(root, as_json=False):
    """Aggregate observations into an M1/M2/M3 summary report."""
    path = metrics_path(root)
    recs = []
    if path.exists():
        for line in smart_read(str(path)).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except Exception:
                continue

    def avg(metric):
        vals = [r["value"] for r in recs if r["metric"] == metric]
        return (sum(vals) / len(vals)) if vals else None

    def count(metric):
        return sum(1 for r in recs if r["metric"] == metric)

    report = {
        "primary_metrics": {
            "M1_continuity": {"count": count("M1"), "avg": avg("M1"), "unit": "continuity (0-1)"},
            "M2_locate_cost": {"count": count("M2"), "avg": avg("M2"), "unit": "tokens"},
            "M3_doc_ref": {"count": count("M3"), "avg": avg("M3"), "unit": "tokens"},
        },
        "secondary": {
            "net_tokens_to_first_action": {"count": count("net_tokens_to_first_action"),
                                            "avg": avg("net_tokens_to_first_action"), "unit": "token"},
        },
        "note": "net_tokens_to_first_action 仅作次要观测指标，不作为 Gate 卡口。",
        "observations": recs,
    }
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("RPD v2 主指标汇总:")
        print(f"  M1 理解连续性   : {report['primary_metrics']['M1_continuity']}")
        print(f"  M2 定位成本     : {report['primary_metrics']['M2_locate_cost']}")
        print(f"  M3 文档引用     : {report['primary_metrics']['M3_doc_ref']}")
        print(f"  net_tokens_to_first_action (次要): {report['secondary']['net_tokens_to_first_action']}")
        print(report["note"])
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    root = args[0]
    if len(args) < 2:
        print("Error: missing command (record|report)", file=sys.stderr)
        return 1
    cmd = args[1]
    rest = args[2:]
    if cmd == "record":
        return cmd_record(root, rest)
    if cmd == "report":
        return cmd_report(root, "--json" in rest)
    print(f"Error: unknown command '{cmd}'", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
