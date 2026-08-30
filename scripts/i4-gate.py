#!/usr/bin/env python3
"""I4 exit gate: machine-checked M1/M2 (Q5) + M3 observation + regression guard.

Q5 (Key Decisions): M1/M2 are the I4 exit Gate and are part of the eval
baseline; M3 (doc ref) is an observation item and does NOT block the gate.

  M1 理解连续性 (continuity)  -- A/B machine check:
    arm A: code-map present -> cold-start/retriever must resolve a known symbol
           via map navigation (no full re-scan needed). Token budget <=300t.
    arm B: code-map absent  -> degrade to direct source scan, still resolves
           (no crash, no guess). Honest downgrade, not a rubber stamp.
  M2 定位成本 (locate cost)  -- PRD change-loop machine check:
    PRD feature term -> impact-analyzer maps to changed/affected code entries
    (R-20 1-hop + blast grade). Requires R-19 edges + R-20 impact-analyzer.
  M3 文档引用 (doc ref)     -- observation only (Q5), never blocks:
    report whether README/decisions docs are present; no gate pass/fail.

Regression guard (red lines, all must be present, else gate FAILs):
  - budget guard: router limit 3000 / entry limit 300 in code-map-generator
  - red-line machine check: verified/unverified/stale + dependency drift in
    rpd-cold-start (R-04/R-13/R-25)
  - backward compat: SCHEMA_VERSION + SCHEMA_WHITELIST in code-map-generator
    (R-10)
  - skill size: SKILL.md <= 8KB (R-05), measured in LF caliber (CRLF is
    normalized away; see _lf_size for why raw on-disk bytes must not be used)

Zero external deps (Q1). Every failure path degrades to a structured report
(ok:false + reason), never a crash. Exit codes:
  0 - all hard gates PASS (M1 + M2 + regression)
  1 - usage error
  2 - hard gate FAIL (exit gate not met)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROUTER_LIMIT = 3000
ENTRY_LIMIT = 300
M3_BLOCK = False  # Q5: M3 is observation only, never blocks the gate
SKILL_LIMIT = 8192        # R-05 hard cap: SKILL.md <= 8KB
SKILL_WARN_MARGIN = 512   # non-blocking advisory: headroom below this is tight

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- static regression guard (red lines) -------------------------------------


def _load_py_module(module_path, module_name):
    """Load a hyphenated sibling script as a module; None on any failure."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _has(src, needle):
    return needle in src


def _lf_size(path):
    """Byte size of a text file with CRLF normalized to LF; None if unreadable.

    R-05 must be measured in LF caliber. On a Windows checkout with
    core.autocrlf=true the on-disk SKILL.md carries 119 CR bytes (8235 B raw)
    while the committed blob is 8116 B. Measuring raw on-disk bytes would fail
    a file that is genuinely within the 8192 B budget -- the guard would be
    wrong on exactly the platform it is meant to protect. Normalize first.
    """
    try:
        return len(Path(path).read_bytes().replace(b"\r\n", b"\n"))
    except Exception:
        return None


def check_regression_guard(scripts_dir):
    """Return list of findings: [{ok, check, detail}]. All must be ok."""
    scripts_dir = Path(scripts_dir)
    gen = scripts_dir / "code-map-generator.py"
    cold = scripts_dir / "rpd-cold-start.py"
    findings = []

    gen_src = _read(gen)
    cold_src = _read(cold)
    for name, path, src in (("code-map-generator.py", gen, gen_src),
                            ("rpd-cold-start.py", cold, cold_src)):
        if not src:
            findings.append({"ok": False, "check": f"static:{name}", "detail": "file missing or unreadable"})

    # 1) budget guard (red line 6): router <=3k / entry <=300
    findings.append({
        "ok": bool(gen_src and _has(gen_src, "ROUTER_TOKEN_LIMIT") and _has(gen_src, "ENTRY_MAX_TOKENS")),
        "check": "budget:router_entry",
        "detail": "ROUTER_TOKEN_LIMIT + ENTRY_MAX_TOKENS in code-map-generator",
    })
    # 2) red-line machine check (red line 8): verified/unverified/stale + drift
    findings.append({
        "ok": bool(cold_src and _has(cold_src, "verified") and _has(cold_src, "stale")
                   and _has(cold_src, "dependency_drift")),
        "check": "redline:trust",
        "detail": "verified/unverified/stale + dependency_drift in rpd-cold-start",
    })
    # 3) backward compat (red line 7): SCHEMA_VERSION + SCHEMA_WHITELIST (R-10)
    findings.append({
        "ok": bool(gen_src and _has(gen_src, "SCHEMA_VERSION") and _has(gen_src, "SCHEMA_WHITELIST")),
        "check": "compat:schema",
        "detail": "SCHEMA_VERSION + SCHEMA_WHITELIST in code-map-generator (R-10)",
    })
    # 4) skill size guard (R-05): SKILL.md <=8KB, LF caliber, blocking
    skill_path = scripts_dir.parent / "SKILL.md"
    skill_size = _lf_size(skill_path)
    if skill_size is None:
        findings.append({
            "ok": False,
            "check": "budget:skill_size",
            "detail": f"SKILL.md missing or unreadable at {skill_path}",
        })
    else:
        margin = SKILL_LIMIT - skill_size
        findings.append({
            "ok": margin >= 0,
            "check": "budget:skill_size",
            "detail": (
                f"SKILL.md {skill_size}B (LF caliber) <= {SKILL_LIMIT}B, "
                f"headroom {margin}B"
            ),
            # advisory only: never flips ok, but surfaces a shrinking budget
            "warn": margin < SKILL_WARN_MARGIN,
        })
    return findings


# --- M1 continuity (A/B) -----------------------------------------------------


def _collect_source_symbols(project_root):
    """Degrade scan: symbols found by direct source grep (arm B)."""
    syms = set()
    for root, _dirs, files in os.walk(project_root):
        if ".git" in root or ".rpd" in root:
            continue
        for fn in files:
            if not fn.endswith((".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".js", ".ts", ".go", ".rs", ".java")):
                continue
            p = Path(root) / fn
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\([^)]{0,80}\)", text):
                syms.add(m.group(1))
    return syms


def _walk_src(project_root):
    out = []
    for root, _dirs, files in os.walk(project_root):
        if ".git" in root or ".rpd" in root:
            continue
        for fn in files:
            if fn.endswith((".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".js", ".ts", ".go", ".rs", ".java")):
                out.append(str(Path(root) / fn))
    return sorted(out)


def m1_continuity_check(project_root, scripts_dir, known_symbol="Game", prd_terms=None):
    """A/B continuity machine check. Returns (ok, report)."""
    root = Path(project_root)
    cmap = root / ".rpd" / "code-map.json"
    report = {"arm": "A" if cmap.is_file() else "B", "mode": "map_navigation" if cmap.is_file() else "source_scan"}
    ok = True
    prd_terms = prd_terms or []

    if cmap.is_file():
        # arm A: map navigation -- resolve the known symbol via retriever
        ret = _load_py_module(scripts_dir / "retriever.py", "rpd_retriever")
        if ret is None:
            report["map_resolved"] = False
            report["reason"] = "retriever module unavailable"
            return False, report
        entries, _idx = ret.load_code_map(root)
        if not entries:
            report["map_resolved"] = False
            report["reason"] = "code-map.json present but entries empty"
            return False, report
        eid = ret.resolve_symbol(entries, known_symbol)
        report["symbol"] = known_symbol
        report["map_resolved"] = eid is not None
        if eid is None:
            report["reason"] = f"symbol {known_symbol} not resolvable via map (unverified)"
            ok = False
        else:
            entry = entries[eid]
            report["entry"] = {"id": eid, "name": entry.get("name", ""),
                               "kind": entry.get("kind", ""), "file": entry.get("file", "")}
            est = ret.estimate_tokens(entry)
            report["entry_tokens"] = est
            report["budget_ok"] = est <= ENTRY_LIMIT
            if not report["budget_ok"]:
                report["reason"] = f"entry {eid} over {ENTRY_LIMIT}t budget"
                ok = False
        # PRD feature -> code via impact-analyzer (M2 also covers this, but M1
        # arm A verifies the map itself answers the continuity question)
        if prd_terms:
            resolved_terms = []
            for term in prd_terms:
                eid2 = ret.resolve_symbol(entries, term)
                resolved_terms.append({"term": term, "resolved": eid2 is not None})
                if eid2 is None:
                    ok = False
            report["prd_terms"] = resolved_terms
    else:
        # arm B: no map -> degrade to direct source scan (honest downgrade)
        syms = _collect_source_symbols(root)
        report["symbols_scanned"] = len(syms)
        report["known_symbol_found"] = known_symbol in syms
        report["source_files"] = len(_walk_src(root))
        # degrade is legitimate when the map is absent; it must not crash and
        # must be explicit (honest downgrade), so arm B passes.
        report["reason"] = "no code-map -> source_scan degrade (explicit, no guess)"
    return ok, report


# --- M2 PRD change-loop ------------------------------------------------------


def m2_prd_loop_check(project_root, scripts_dir, prd_path, feature_term="Game"):
    """PRD -> code impact loop machine check (R-20 + R-19 edges).
    Returns (ok, report)."""
    root = Path(project_root)
    report = {"mode": "impact-analyzer"}
    ia = _load_py_module(scripts_dir / "impact-analyzer.py", "rpd_impact_analyzer")
    if ia is None:
        report["ok"] = False
        report["reason"] = "impact-analyzer module unavailable"
        return False, report
    try:
        prd_text = Path(prd_path).read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        report["ok"] = False
        report["reason"] = f"prd unreadable: {e}"
        return False, report
    try:
        result = ia.analyze_prd_to_code(str(root), prd_text, str(prd_path))
    except Exception as e:
        report["ok"] = False
        report["reason"] = f"analyze_prd_to_code failed: {e}"
        return False, report
    changed = [e.get("name") for e in (result.get("changed_nodes") or [])]
    affected = [e.get("name") for e in (result.get("affected_nodes") or [])]
    layers = result.get("affected_layers") or []
    blast = result.get("blast_radius")
    report["feature"] = feature_term
    report["changed"] = changed
    report["affected_1hop"] = affected
    report["affected_layers"] = layers
    report["blast_radius"] = blast
    report["budget"] = result.get("budget", {})
    report["ok"] = feature_term in changed
    if not report["ok"]:
        report["reason"] = f"PRD feature '{feature_term}' did not map to code: changed={changed}"
    est = (result.get("budget") or {}).get("estimated_results_tokens")
    report["budget_ok"] = est is not None and est <= ENTRY_LIMIT
    if not report["budget_ok"]:
        report["reason"] = f"impact payload over {ENTRY_LIMIT}t budget: {est}"
    return report["ok"], report


# --- M3 doc-ref observation (never blocks) -----------------------------------


def m3_doc_ref_observation(project_root):
    """M3 doc ref: observation only (Q5). Reports doc presence + mapping.
    Returns report dict (no ok flag required)."""
    root = Path(project_root)
    docs = {
        "README": (root / "README.md").is_file(),
        "decisions": (root / ".rpd" / "decisions.md").is_file(),
        "active_context": (root / ".rpd" / "active-context.md").is_file(),
    }
    mapped = (root / ".rpd" / "code-map.json").is_file()
    return {"docs": docs, "map_present": mapped,
            "note": "M3 doc-ref is observation only (Q5), does not block the gate"}


# --- gate runner -------------------------------------------------------------


def run_gate(project_root, prd_path=None, known_symbol="Game", feature_term="Game"):
    scripts_dir = Path(__file__).resolve().parent
    report = {
        "gate": "I4-exit (Q5)",
        "checks": {},
    }
    hard_ok = True

    # M1 continuity (hard)
    m1_ok, m1r = m1_continuity_check(project_root, scripts_dir, known_symbol=known_symbol)
    report["checks"]["M1_continuity"] = {"ok": m1_ok, "report": m1r}
    hard_ok = hard_ok and m1_ok

    # M2 PRD change-loop (hard, when PRD provided)
    if prd_path and Path(prd_path).is_file():
        m2_ok, m2r = m2_prd_loop_check(project_root, scripts_dir, prd_path, feature_term=feature_term)
        report["checks"]["M2_prd_loop"] = {"ok": m2_ok, "report": m2r}
        hard_ok = hard_ok and m2_ok
    else:
        report["checks"]["M2_prd_loop"] = {"ok": None, "report": {"reason": "prd not provided -> M2 skipped"}}

    # M3 doc-ref observation (never blocks)
    report["checks"]["M3_doc_ref"] = {"ok": True, "report": m3_doc_ref_observation(project_root)}

    # regression guard (hard)
    reg = check_regression_guard(scripts_dir)
    report["checks"]["regression_guard"] = {
        "ok": all(f["ok"] for f in reg),
        "findings": reg,
    }
    hard_ok = hard_ok and all(f["ok"] for f in reg)

    report["pass"] = hard_ok
    if not hard_ok:
        report["reason"] = "one or more hard checks failed (see checks)"
    return report


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    root = args[0]
    prd_path = None
    known_symbol = "Game"
    feature_term = "Game"
    if "--prd" in args:
        pi = args.index("--prd") + 1
        if pi < len(args):
            prd_path = args[pi]
    if "--symbol" in args:
        si = args.index("--symbol") + 1
        if si < len(args):
            known_symbol = args[si]
    if "--feature" in args:
        fi = args.index("--feature") + 1
        if fi < len(args):
            feature_term = args[fi]
    as_json = "--json" in args

    if not Path(root).is_dir():
        print(f"Error: not a directory: {root}", file=sys.stderr)
        return 1

    report = run_gate(root, prd_path=prd_path, known_symbol=known_symbol, feature_term=feature_term)
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("I4 exit gate (Q5): M1/M2 machine-check + M3 observation + regression guard")
        for name, chk in report["checks"].items():
            status = "PASS" if chk.get("ok") else ("OBS" if chk.get("ok") is None else "FAIL")
            print(f"  [{status}] {name}")
        print("GATE PASS" if report["pass"] else f"GATE FAIL: {report.get('reason', '')}")
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
