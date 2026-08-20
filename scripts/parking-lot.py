#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RPD parking-lot governance (R-24/R-26/R-27/R-28/R-29, I4-7).

Four-trigger promotion mechanism (task_plan Phase I4-7):

  T1 dependency_ready : every listed dep requirement has LANDED (verified by
                        probing scripts/ for the implementing module, with a
                        built-in fact fallback).
  T2 user_signal      : entry.signal_count >= USER_SIGNAL_THRESHOLD (3).
  T3 cost_benefit_flip: explicit human flag on the entry.
  T4 review_due       : per-iteration periodic review; review_due date passed.

Promotion requires THREE mandatory elements (no "顺手混入"):
  --id <req-id>   --impact <scope>   --budget <cost estimate>
Missing any -> refused (exit 1). If NO trigger is ready the promotion is
refused too (exit 2) - promotions need evidence, never convenience.

Promise guard: frozen entries must NOT claim "已规划交付" style commitments;
--promise-check machine-scans titles/notes for commitment phrasing.

Storage: <.rpd>/parking-lot.json (human readable, versioned).
Degrade : missing store -> built-in default five entries (R-24/26/27/28/29)
          are served read-only, nothing crashes; unwritable -> exit 2.

Zero external deps (Q1). Budget guard (R-07): list output capped.

Usage:
  python parking-lot.py <root> [--json]                          # summary list
  python parking-lot.py <root> --add --id R-26 --title "ACL" [--deps R-21] [--signals 0] [--notes "..."] [--json]
  python parking-lot.py <root> --audit [--json]                  # four-trigger machine check
  python parking-lot.py <root> --upgrade --id R-26 --impact "..." --budget "..." [--json]
  python parking-lot.py <root> --promise-check [--json]          # no-delivery-promise scan
  python parking-lot.py <root> --remove --id R-26 [--json]

Exit codes: 0 ok (incl. legitimate empty); 1 usage / missing promotion
elements; 2 write failure / promotion without any ready trigger.
"""

import json
import os
import re
import sys
from datetime import datetime, date
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PARKING_FILE = ".rpd/parking-lot.json"
SCHEMA_VERSION = 1
USER_SIGNAL_THRESHOLD = 3
LIST_LIMIT = 50
PROMISE_WORDS = ("已规划交付", "即将交付", "计划交付", "planned delivery", "shipping soon", "已排期交付")

# Requirement id -> implementing module in scripts/ (probe-based, machine checkable)
IMPLEMENTING_SCRIPTS = {
    "R-19": "code-map-generator.py",   # edges (KG map + dangling drop)
    "R-20": "impact-analyzer.py",      # PRD<->code impact
    "R-21": "memory-layers.py",        # L0-L3 layered memory
    "R-22": "retriever.py",            # hybrid retrieval
    "R-23": "exposure-guard.py",       # progressive exposure
    "R-25": "code-map-generator.py",   # dependency lock (same module)
}
# Built-in fact fallback when scripts/ cannot be probed
LANDED_FALLBACK = {"R-19", "R-20", "R-21", "R-22", "R-23", "R-25"}

DEFAULT_ENTRIES = [
    {"id": "R-24", "title": "经验资产化", "status": "frozen",
     "triggers": ["dependency_ready", "review_due"], "deps": ["R-21"],
     "signal_count": 0, "cost_benefit_flip": False, "review_due": None,
     "notes": "parking-lot 冻结；待 L0-L3 分层记忆稳定后按四档触发评估升级"},
    {"id": "R-26", "title": "ACL 访问控制（先过滤后检索）", "status": "frozen",
     "triggers": ["dependency_ready"], "deps": ["R-21"],
     "signal_count": 0, "cost_benefit_flip": False, "review_due": None,
     "notes": "依赖 R-21 分层记忆；默认私有，先过滤后检索"},
    {"id": "R-27", "title": "全图影响分析（2-hop+）", "status": "frozen",
     "triggers": ["dependency_ready"], "deps": ["R-19"],
     "signal_count": 0, "cost_benefit_flip": False, "review_due": None,
     "notes": "依赖 R-19 边数据；在 R-20 1-hop 基础上扩 2-hop"},
    {"id": "R-28", "title": "团队记忆", "status": "frozen",
     "triggers": ["dependency_ready"], "deps": ["R-21", "R-26"],
     "signal_count": 0, "cost_benefit_flip": False, "review_due": None,
     "notes": "依赖 R-21 分层记忆 + R-26 ACL；组织级组合（L3 阶段 C）"},
    {"id": "R-29", "title": "多语言支持", "status": "frozen",
     "triggers": ["dependency_ready"], "deps": ["R-22"],
     "signal_count": 0, "cost_benefit_flip": False, "review_due": None,
     "notes": "依赖 R-22 检索；主语言外走未索引→按需 Read（R-16 同族）"},
]


def today_iso():
    return date.today().isoformat()


def load(project_root):
    """Return (entries:dict, source:"store"|"builtin"). Degrade never crashes."""
    p = Path(project_root) / PARKING_FILE
    if not p.exists():
        return {e["id"]: dict(e) for e in DEFAULT_ENTRIES}, "builtin"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data.get("entries", {})
        if not isinstance(entries, dict) or not entries:
            return {e["id"]: dict(e) for e in DEFAULT_ENTRIES}, "builtin"
        return entries, "store"
    except Exception:
        return {e["id"]: dict(e) for e in DEFAULT_ENTRIES}, "builtin"


def save(project_root, entries):
    p = Path(project_root) / PARKING_FILE
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": SCHEMA_VERSION, "updated": today_iso(), "entries": entries}
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, p)
        return True
    except Exception:
        return False


def landed_set(project_root):
    """Machine-checked landed set: probe scripts/ modules, fallback to facts."""
    landed = set()
    scripts_dir = Path(project_root) / "scripts"
    for req, mod in IMPLEMENTING_SCRIPTS.items():
        if (scripts_dir / mod).exists():
            landed.add(req)
    return landed if landed else set(LANDED_FALLBACK)


def entry_ready(entry, landed, today):
    """Evaluate the four triggers for one entry -> list of {trigger, ready, reason}."""
    out = []
    # T1 dependency_ready
    deps = entry.get("deps") or []
    if entry.get("triggers") and "dependency_ready" in entry.get("triggers", []):
        missing = [d for d in deps if d not in landed]
        out.append({
            "trigger": "dependency_ready", "ready": len(missing) == 0,
            "reason": ("deps landed: " + (",".join(deps) if deps else "none"))
                       if not missing else "missing deps: " + ",".join(missing),
        })
    else:
        out.append({"trigger": "dependency_ready", "ready": False, "reason": "not enabled"})
    # T2 user_signal
    n = int(entry.get("signal_count") or 0)
    out.append({
        "trigger": "user_signal", "ready": n >= USER_SIGNAL_THRESHOLD,
        "reason": "signal_count=%d (>=%d needed)" % (n, USER_SIGNAL_THRESHOLD),
    })
    # T3 cost_benefit_flip
    flip = bool(entry.get("cost_benefit_flip"))
    out.append({
        "trigger": "cost_benefit_flip", "ready": flip,
        "reason": "human flag set" if flip else "not flagged",
    })
    # T4 review_due
    due = entry.get("review_due")
    if due:
        due_dt = date.fromisoformat(due) if isinstance(due, str) else due
        out.append({
            "trigger": "review_due", "ready": today >= due_dt,
            "reason": "review_due=%s" % due,
        })
    else:
        out.append({"trigger": "review_due", "ready": False, "reason": "no review_due set"})
    return out


def cmd_summary(entries, source):
    rows = []
    for eid in sorted(entries):
        e = entries[eid]
        rows.append({
            "id": eid, "title": e.get("title", ""), "status": e.get("status", "frozen"),
            "deps": e.get("deps") or [], "signals": int(e.get("signal_count") or 0),
        })
    return {"ok": True, "source": source, "count": len(rows), "entries": rows[:LIST_LIMIT]}


def cmd_add(entries, source, project_root, args):
    eid = args.get("--id", "")
    title = args.get("--title", "")
    if not eid or not title:
        return {"ok": False, "error": "usage: --add requires --id and --title"}, 1
    if not re.match(r"^R-\d+$", eid):
        return {"ok": False, "error": "id must match R-<number>, got: " + eid}, 1
    deps = [d.strip() for d in (args.get("--deps", "") or "").split(",") if d.strip()]
    triggers = [t.strip() for t in (args.get("--triggers", "") or "").split(",") if t.strip()] \
        or ["dependency_ready"]
    entries[eid] = {
        "id": eid, "title": title, "status": "frozen",
        "triggers": triggers, "deps": deps,
        "signal_count": int(args.get("--signals", "0") or 0),
        "cost_benefit_flip": False, "review_due": None,
        "notes": args.get("--notes", "") or "",
    }
    if not save(project_root, entries):
        return {"ok": False, "error": "write failed"}, 2
    return {"ok": True, "id": eid, "status": "frozen"}, 0


def cmd_audit(entries, source, project_root):
    landed = sorted(landed_set(project_root))
    today = date.today()
    items = []
    for eid in sorted(entries):
        e = entries[eid]
        trig = entry_ready(e, set(landed), today)
        items.append({
            "id": eid, "status": e.get("status", "frozen"),
            "triggers": trig, "any_ready": any(t["ready"] for t in trig),
        })
    return {
        "ok": True, "source": source, "landed": landed,
        "threshold_user_signal": USER_SIGNAL_THRESHOLD, "items": items,
    }, 0


def cmd_upgrade(entries, source, project_root, args):
    eid = args.get("--id", "")
    impact = (args.get("--impact", "") or "").strip()
    budget = (args.get("--budget", "") or "").strip()
    missing = []
    if not eid:
        missing.append("id")
    if not impact:
        missing.append("impact")
    if not budget:
        missing.append("budget")
    if missing:
        return {"ok": False, "error": "missing promotion elements",
                "missing": missing, "hint": "upgrade requires --id + --impact + --budget"}, 1
    if eid not in entries:
        return {"ok": False, "error": "unknown id: " + eid}, 1
    today = date.today()
    trig = entry_ready(entries[eid], set(landed_set(project_root)), today)
    if not any(t["ready"] for t in trig):
        return {"ok": False, "error": "no trigger ready - promotion needs evidence, not convenience",
                "triggers": trig}, 2
    e = entries[eid]
    e["status"] = "upgraded"
    e["promotion"] = {
        "impact": impact, "budget": budget,
        "trigger_snapshot": [{"trigger": t["trigger"], "ready": t["ready"]} for t in trig],
        "upgraded_at": today_iso(),
    }
    if not save(project_root, entries):
        return {"ok": False, "error": "write failed"}, 2
    return {"ok": True, "id": eid, "status": "upgraded", "promotion": e["promotion"]}, 0


def cmd_promise_check(entries, source):
    violations = []
    for eid in sorted(entries):
        e = entries[eid]
        if e.get("status") != "frozen":
            continue
        blob = (e.get("title", "") + " " + (e.get("notes") or ""))
        for w in PROMISE_WORDS:
            if w.lower() in blob.lower():
                violations.append({"id": eid, "word": w, "title": e.get("title", "")})
    return {
        "ok": len(violations) == 0, "scanned": len(entries), "violations": violations,
        "note": "frozen entries must not claim scheduled delivery",
    }, 0


def cmd_remove(entries, source, project_root, args):
    eid = args.get("--id", "")
    if not eid or eid not in entries:
        return {"ok": False, "error": "unknown id: " + str(eid)}, 1
    del entries[eid]
    if not save(project_root, entries):
        return {"ok": False, "error": "write failed"}, 2
    return {"ok": True, "removed": eid}, 0


def main(argv):
    if len(argv) < 2:
        print(json.dumps({"ok": False, "error": "usage: parking-lot.py <project-root> [opts]"},
                         ensure_ascii=False))
        return 1
    project_root = argv[1]
    args = {}
    i = 2
    while i < len(argv):
        k = argv[i]
        if k.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            args[k] = argv[i + 1]
            i += 2
        else:
            args[k] = True
            i += 1
    use_json = bool(args.get("--json", False))
    entries, source = load(project_root)
    op = None
    for flag in ("--audit", "--upgrade", "--promise-check", "--add", "--remove"):
        if args.get(flag):
            op = flag
            break
    if op is None:
        payload, code = cmd_summary(entries, source), 0
    elif op == "--audit":
        payload, code = cmd_audit(entries, source, project_root)
    elif op == "--upgrade":
        payload, code = cmd_upgrade(entries, source, project_root, args)
    elif op == "--promise-check":
        payload, code = cmd_promise_check(entries, source)
    elif op == "--add":
        payload, code = cmd_add(entries, source, project_root, args)
    elif op == "--remove":
        payload, code = cmd_remove(entries, source, project_root, args)
    else:
        payload, code = {"ok": False, "error": "unknown op"}, 1
    out = json.dumps(payload, ensure_ascii=False, indent=2) if use_json \
        else json.dumps(payload, ensure_ascii=False)
    print(out)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
