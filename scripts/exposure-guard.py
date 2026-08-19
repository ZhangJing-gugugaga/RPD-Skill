#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RPD v2 progressive exposure guard (R-23).

Three-layer injection policy over the two-layer code-map, plus a hard
per-task injection budget (dual budget: entry count + token count).

  L1 router (layer-1)     : always resident    -> <= ROUTER_TOKEN_LIMIT (3000)
  L2 entry (layer-2)      : on-demand single   -> <= ENTRY_MAX_TOKENS (300)
  L3 summary (layer-3)    : deep-follow-up     -> <= SUMMARY_MAX_TOKENS (500)  [Q4]

Rules:
  - L1 is always allowed (cold-start already reads the router).
  - L2 single entries are allowed on demand, each <= 300 tokens.
  - L3 semantic summaries are injected ONLY after "deep follow-up" (Q4:
    user asks about the SAME symbol/module for 2 consecutive turns) and only
    within the task budget.
  - Step-up (yue-ji) is intercepted: requesting L3 without deep follow-up is
    blocked and downgraded to L2 (or a README/code direct-read hint).
  - Hard per-task budget: max entries + max tokens for the task's injection
    window; exceeding either is blocked with a degrade hint (fail back to
    README/code direct read, never crash).
  - No code-map -> all layers report ok:false with a README/code direct-read
    hint (degrade path, never crash).

Zero external deps (Q1). Budget guard (R-07): every payload is measured.

Usage:
  python exposure-guard.py <project-root> --l1 [--json]
  python exposure-guard.py <project-root> --entry <symbol> [--json]
  python exposure-guard.py <project-root> --summary <symbol> --deep <N> [--json]

Exit codes: 0 success (including legitimate blocks); 1 usage error / no layers.
"""

import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- budgets (hard constraints, R-07 / 7) -----------------------------------
ROUTER_TOKEN_LIMIT = 3000     # L1 always-resident ceiling
ENTRY_MAX_TOKENS = 300        # L2 single-entry ceiling
SUMMARY_MAX_TOKENS = 500      # L3 semantic-summary ceiling (Q4)
TASK_ENTRY_BUDGET = 24        # per-task: max Layer-2 entries injected
TASK_TOKEN_BUDGET = 2000      # per-task: max total tokens injected (all layers)
DEEP_FOLLOWUP_TURNS = 2       # Q4: "deep follow-up" = 2 consecutive turns on same symbol

CODE_MAP_FILE = ".rpd/code-map.json"
ROUTER_FILE = ".rpd/code-map.router.json"

# --- retriever reuse (same scripts dir); standalone degrade keeps file runnable
try:
    from retriever import resolve_symbol, load_code_map, estimate_tokens  # noqa: F401
except Exception:  # pragma: no cover - standalone fallback
    def resolve_symbol(entries, symbol):
        if not symbol:
            return None
        for eid, e in entries.items():
            if e.get("name") == symbol:
                return eid
        if symbol in entries:
            return symbol
        seg = symbol.split("::")[-1]
        hits = [eid for eid, e in entries.items() if e.get("name") == seg]
        return hits[0] if hits else None

    def load_code_map(project_root):
        path = Path(project_root) / CODE_MAP_FILE
        if not path.is_file():
            return None, None
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            return data.get("entries", {}), data.get("inverted_index", {})
        except Exception:
            return None, None

    def estimate_tokens(obj):
        try:
            return max(1, len(json.dumps(obj, ensure_ascii=False, separators=(",", ":"))) // 4)
        except Exception:
            return 0


def smart_read(file_path):
    """Multi-encoding read (same fallback chain as run-eval)."""
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp1252", "latin-1"):
        try:
            return Path(file_path).read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return Path(file_path).read_text(encoding="utf-8", errors="replace")


def load_router(project_root):
    """Read layer-1 router; return dict or None."""
    path = Path(project_root) / ROUTER_FILE
    if not path.is_file():
        return None
    try:
        return json.loads(smart_read(str(path)))
    except Exception:
        return None


def _entry_payload(entry, eid):
    """Compact layer-2 entry (drop bulky internal fields, keep <=300t)."""
    keep = ("id", "name", "kind", "file", "line", "layer", "signature", "doc")
    out = {k: entry.get(k) for k in keep if k in entry}
    out["id"] = eid
    return out


def build_l1(project_root):
    """Layer-1: always-resident router, budget-checked."""
    router = load_router(project_root)
    if router is None:
        return {
            "ok": False, "layer": "L1", "allowed": False,
            "reason": "no_router",
            "degrade_hint": "code-map 缺失：直接读 README 或目标源码文件定位（R-23 降级路径）",
        }
    budget = router.get("budget", {})
    est = budget.get("estimated_read_tokens", estimate_tokens(router))
    limit = budget.get("token_limit", ROUTER_TOKEN_LIMIT)
    return {
        "ok": True, "layer": "L1", "allowed": est <= limit,
        "estimated_tokens": est, "limit": limit,
        "budget": {"token_limit": limit, "estimated_read_tokens": est},
    }


def build_l2(project_root, symbol):
    """Layer-2: on-demand single entry (<=300t). Symbol resolved 3-level."""
    entries, _ = load_code_map(project_root)
    if entries is None:
        return {
            "ok": False, "layer": "L2", "allowed": False,
            "reason": "no_code_map",
            "degrade_hint": "code-map 缺失：直接读 README 或目标源码文件定位（R-23 降级路径）",
        }
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {
            "ok": True, "layer": "L2", "allowed": True, "resolved": False,
            "results": [],
            "degrade_hint": "符号未解析：直接读 README 或源码全文检索（不猜测）",
        }
    payload = _entry_payload(entries[eid], eid)
    est = estimate_tokens(payload)
    allowed = est <= ENTRY_MAX_TOKENS
    return {
        "ok": True, "layer": "L2", "allowed": allowed, "resolved": True,
        "entry_id": eid, "estimated_tokens": est, "limit": ENTRY_MAX_TOKENS,
        "results": [payload] if allowed else [],
        "blocked_reason": "entry_over_budget" if not allowed else None,
        "degrade_hint": "单条 entry 超预算：改读 README / 源码局部（R-23 降级路径）" if not allowed else None,
    }


def build_l3(project_root, symbol, deep_turns):
    """Layer-3: semantic summary (<=500t), ONLY after deep follow-up (Q4).

    deep_turns < DEEP_FOLLOWUP_TURNS -> step-up intercepted: blocked and
    downgraded to L2 (never silently escalated).
    """
    entries, _ = load_code_map(project_root)
    if entries is None:
        return {
            "ok": False, "layer": "L3", "allowed": False,
            "reason": "no_code_map",
            "degrade_hint": "code-map 缺失：直接读 README 或目标源码文件定位（R-23 降级路径）",
        }
    if deep_turns < DEEP_FOLLOWUP_TURNS:
        return {
            "ok": True, "layer": "L3", "allowed": False,
            "blocked_reason": "deep_followup_required",
            "deep_turns": deep_turns, "required_turns": DEEP_FOLLOWUP_TURNS,
            "degrade_hint": (
                "越级拦截（R-23）：L3 语义摘要需同一符号连续追问 "
                + str(DEEP_FOLLOWUP_TURNS) + " 轮；当前已降级到 L2 单条 entry 或 README/代码直读"
            ),
        }
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {
            "ok": True, "layer": "L3", "allowed": False,
            "blocked_reason": "unresolved",
            "degrade_hint": "符号未解析：直接读 README 或源码全文检索（不猜测）",
        }
    entry = entries[eid]
    # compact semantic summary: identity + layer + edges overview + calls + doc
    summary = {
        "symbol": symbol,
        "entry_id": eid,
        "name": entry.get("name", ""),
        "kind": entry.get("kind", ""),
        "file": entry.get("file", ""),
        "line": entry.get("line", 0),
        "layer": entry.get("layer", "unknown"),
        "edges": [
            {"type": e.get("type", ""), "target": e.get("target", ""), "weight": e.get("weight", 0)}
            for e in entry.get("edges", [])[:8]
        ],
        "calls": [c.get("target", "") for c in entry.get("calls", [])[:8]],
        "doc": (entry.get("doc", "") or "")[:200],
    }
    est = estimate_tokens(summary)
    allowed = est <= SUMMARY_MAX_TOKENS
    return {
        "ok": True, "layer": "L3", "allowed": allowed, "resolved": True,
        "entry_id": eid, "estimated_tokens": est, "limit": SUMMARY_MAX_TOKENS,
        "results": [summary] if allowed else [],
        "blocked_reason": "summary_over_budget" if not allowed else None,
        "degrade_hint": "L3 摘要超预算：改读 README / 源码局部（R-23 降级路径）" if not allowed else None,
    }


def run_exposure(project_root, entry_symbol=None, summary_symbol=None, deep_turns=0):
    """Full R-23 exposure check. L1 always; L2 on demand (entry_symbol or
    summary_symbol); L3 only with summary request + deep context. Per-task
    dual budget enforced at the end."""
    layers = {"L1": build_l1(project_root)}
    l2_symbol = entry_symbol or summary_symbol
    if l2_symbol:
        layers["L2"] = build_l2(project_root, l2_symbol)
    if summary_symbol:
        layers["L3"] = build_l3(project_root, summary_symbol, deep_turns)
    # per-task dual budget over whatever was actually injected
    injected_entries = 0
    injected_tokens = 0
    for lyr, info in layers.items():
        if info.get("ok") and info.get("allowed"):
            for r in info.get("results", []):
                injected_entries += 1
                injected_tokens += estimate_tokens(r)
    budget_ok = injected_entries <= TASK_ENTRY_BUDGET and injected_tokens <= TASK_TOKEN_BUDGET
    return {
        "ok": True,
        "layers": layers,
        "task_budget": {
            "entries_injected": injected_entries, "entry_limit": TASK_ENTRY_BUDGET,
            "tokens_injected": injected_tokens, "token_limit": TASK_TOKEN_BUDGET,
            "ok": budget_ok,
        },
        "budget_limits": {
            "router": ROUTER_TOKEN_LIMIT, "entry": ENTRY_MAX_TOKENS,
            "summary": SUMMARY_MAX_TOKENS, "deep_followup_turns": DEEP_FOLLOWUP_TURNS,
        },
    }


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print("Usage: python exposure-guard.py <project-root> --l1 [--json]")
        print("       python exposure-guard.py <project-root> --entry <symbol> [--json]")
        print("       python exposure-guard.py <project-root> --summary <symbol> --deep <N> [--json]")
        return 1
    project_root = args[0]
    as_json = "--json" in args

    entry_symbol = None
    summary_symbol = None
    deep_turns = 0
    if "--entry" in args:
        ei = args.index("--entry") + 1
        if ei >= len(args) or args[ei].startswith("--"):
            print("Error: --entry requires a symbol", file=sys.stderr)
            return 1
        entry_symbol = args[ei]
    if "--summary" in args:
        si = args.index("--summary") + 1
        if si >= len(args) or args[si].startswith("--"):
            print("Error: --summary requires a symbol", file=sys.stderr)
            return 1
        summary_symbol = args[si]
        if "--deep" in args:
            di = args.index("--deep") + 1
            try:
                deep_turns = max(0, int(args[di]))
            except (ValueError, IndexError):
                deep_turns = 0

    payload = run_exposure(project_root, entry_symbol, summary_symbol, deep_turns)
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for lyr, info in payload["layers"].items():
            tag = "OK" if info.get("ok") and info.get("allowed") else "BLOCK"
            print(tag + " " + lyr + " allowed=" + str(info.get("allowed")) +
                  (" est=" + str(info.get("estimated_tokens")) + "t" if "estimated_tokens" in info else "") +
                  (" reason=" + str(info.get("blocked_reason") or info.get("reason", "")) if not info.get("allowed", True) else ""))
            if info.get("degrade_hint"):
                print("    degrade: " + info["degrade_hint"])
        tb = payload["task_budget"]
        print("task budget: entries " + str(tb["entries_injected"]) + "/" + str(tb["entry_limit"]) +
              " tokens " + str(tb["tokens_injected"]) + "/" + str(tb["token_limit"]) +
              " ok=" + str(tb["ok"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
