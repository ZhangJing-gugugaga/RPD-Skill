#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RPD v2 PRD<->code impact analyzer (R-20).

Answers the M2 change-loop questions over the mapped graph (R-19 edges):
  - PRD -> code : "改 PRD 需求 -> 定位受影响代码模块并分级"
      changed_nodes  (direct PRD-feature matches in code-map entries)
      affected_nodes (1-hop: edges / calls / called_by neighbors)
      affected_layers(distinct entry.layer values)
      blast_radius   (Critical / High / Medium / Low)
  - code -> PRD : "改代码 -> 反查受影响 PRD 需求"
      resolve symbol -> entry -> PRD features matching it or its 1-hop set

Data sources (read-only):
  - <project-root>/.rpd/code-map.json   (R-11 symbol table + R-19 edges)
  - PRD markdown parsed from the RPD PRD template structure (Q3):
      * 功能列表 table: | 模块 | 功能名称 | 子任务 | 功能说明 | 优先级 |
      * 页面结构 headings (#### <页面名称>) + navigation code fences
      * 概念版 MVP list ("  1. [功能一]")
  - degrade: no code-map -> direct source-file scan for feature terms;
             no PRD file / bad args -> error result (ok:false), never crash.

Zero external deps (Q1). Budget guard: result payload <= RESULT_MAX_TOKENS.

Usage:
  python impact-analyzer.py <project-root> --prd <prd.md> [--json]
  python impact-analyzer.py <project-root> --code-to-prd <symbol> --prd <prd.md> [--json]
"""

import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- retriever reuse (same scripts dir); standalone degrade keeps this file runnable ---
try:
    from retriever import load_code_map, resolve_symbol, estimate_tokens  # noqa: F401
except Exception:  # pragma: no cover - standalone fallback (no code-map support)
    def load_code_map(project_root):
        return None, None

    def resolve_symbol(entries, symbol):
        return None

    def estimate_tokens(obj):
        try:
            return max(1, len(json.dumps(obj, ensure_ascii=False, separators=(",", ":"))) // 4)
        except Exception:
            return 0

RESULT_MAX_TOKENS = 300
HOP1_NEIGHBORS_MAX = 48
CHANGED_MAX = 32

STOPWORDS = {
    "功能", "模块", "页面", "名称", "说明", "优先级", "子任务", "需求",
    "用户", "系统", "包括", "包含", "提供", "支持", "完成", "展示",
    "the", "and", "for", "with", "this", "that", "feature", "module", "page",
}
# RPD PRD template section headings to skip when parsing page headings
SECTION_HEADING = re.compile(r"^[一二三四五六七八九十]+[、.．]")


def smart_read(path):
    """Multi-encoding read (same fallback chain as run-eval)."""
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp1252", "latin-1"):
        try:
            return Path(path).read_text(encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return Path(path).read_text(encoding="utf-8", errors="replace")


# --- PRD parsing (Q3: parse from existing PRD docs, no domain registry) ------

def parse_prd(prd_text):
    """Extract PRD nodes from the RPD PRD template structure.

    Returns a list of {"kind", "term", "module"} where term is a matching
    candidate (feature name / page name / MVP item), deduped, stopword-free.
    """
    nodes = []
    seen = set()

    def add(kind, term, module=""):
        term = (term or "").strip()
        term = re.sub(r"^[*`>~\d.\s\-]+", "", term).strip().strip("[]")
        if not term or len(term) > 40:
            return
        if term.lower() in STOPWORDS:
            return
        if term not in seen:
            seen.add(term)
            nodes.append({"kind": kind, "term": term, "module": module})

    # 1) feature table: | 模块 | 功能名称 | 子任务 | 功能说明 | 优先级 |
    in_feature_table = False
    for line in prd_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            in_feature_table = False
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        joined = "".join(cells).lower()
        if "功能名称" in joined or joined.startswith("模块"):
            in_feature_table = True
            continue
        if in_feature_table:
            add("feature", cells[0], cells[0])
            add("feature", cells[1], cells[0])

    # 2) page headings (#### <页面名称>) + navigation code fences
    for m in re.finditer(r"^####\s+([^\n]+)$", prd_text, re.MULTILINE):
        title = m.group(1).strip()
        if SECTION_HEADING.match(title):
            continue
        add("page", title)
    for m in re.finditer(r"^(?:├─|└─)\s*\[([^\]]+)\]", prd_text, re.MULTILINE):
        add("page", m.group(1).strip())

    # 3) concept MVP list ("  1. [功能一]")
    for m in re.finditer(r"^\s*\d+\.\s*\[([^\]]+)\]", prd_text, re.MULTILINE):
        add("mvp", m.group(1).strip())

    return nodes


# --- matching (PRD feature term -> code-map entries) -------------------------

def _entry_hits(entries, term):
    """Rank code-map entries matching a PRD feature term.

    Score: exact name 4 > name substring 3 > file substring 2 > doc/sig 1.
    Returns [(score, eid, entry)] sorted desc (stable by id).
    """
    hits = []
    t = (term or "").strip()
    if not t or t.lower() in STOPWORDS:
        return hits
    tl = t.lower()
    for eid, e in entries.items():
        name = (e.get("name", "") or "").lower()
        file = (e.get("file", "") or "").lower()
        doc = (e.get("doc", "") or "").lower()
        sig = (e.get("signature", "") or "").lower()
        score = 0
        if name == tl:
            score = 4
        elif tl in name:
            score = 3
        elif tl in file:
            score = 2
        elif tl in doc or tl in sig:
            score = 1
        if score:
            hits.append((score, eid, e))
    hits.sort(key=lambda x: (-x[0], x[1]))
    return hits


def _hop1_neighbors(entries, eid, seen):
    """1-hop neighbors over edges + calls + called_by (bounded)."""
    out = []
    entry = entries.get(eid, {})
    targets = []
    for e in entry.get("edges", []):
        t = e.get("target", "")
        if t and t in entries and t not in seen:
            seen.add(t)
            targets.append(t)
    for c in entry.get("calls", []):
        t = c.get("target", "")
        if t and t in entries and t not in seen:
            seen.add(t)
            targets.append(t)
    for cb in entry.get("called_by", []):
        t = cb.get("caller", "")
        if t and t in entries and t not in seen:
            seen.add(t)
            targets.append(t)
    for t in targets[:HOP1_NEIGHBORS_MAX]:
        out.append(entries[t])
    return out


def _grade_blast(changed_n, layers_n):
    """Risk grading aligned with /understand-diff (changedNodes/affectedLayers)."""
    if changed_n >= 5 or layers_n >= 3:
        return "Critical"
    if changed_n >= 3 or layers_n >= 2:
        return "High"
    if changed_n >= 1:
        return "Medium"
    return "Low"


def _entry_brief(e):
    return {
        "id": e.get("id", ""),
        "name": e.get("name", ""),
        "kind": e.get("kind", ""),
        "file": e.get("file", ""),
        "layer": e.get("layer", "unknown"),
    }


def _enforce_budget(payload, limit=RESULT_MAX_TOKENS):
    """Trim affected_nodes until the result payload fits <= limit tokens."""
    est = estimate_tokens(payload)
    while est > limit and payload.get("affected_nodes"):
        payload["affected_nodes"] = payload["affected_nodes"][:-1]
        est = estimate_tokens(payload)
    payload["budget"] = {
        "result_max_tokens": limit,
        "estimated_results_tokens": est,
    }
    return payload


# --- degrade path: no code-map -> direct source scan -------------------------

SOURCE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
               ".hpp", ".cc", ".go", ".rs", ".cs", ".php", ".rb", ".swift",
               ".kt", ".vue", ".html", ".css", ".sh", ".sql", ".md", ".txt"}


def _degrade_scan(project_root, terms):
    """Fallback when code-map is missing: direct source-file grep (never crash)."""
    out = []
    terms = [t for t in terms if t and t.lower() not in STOPWORDS]
    if not terms:
        return out
    root = Path(project_root)
    try:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            if rel.startswith(".rpd") or "/.rpd/" in rel or "/.git/" in rel:
                continue
            if p.suffix.lower() not in SOURCE_EXTS:
                continue
            try:
                text = smart_read(p)
            except Exception:
                continue
            if any(t in text for t in terms):
                out.append({"id": "file:" + rel, "name": p.name, "kind": "file",
                            "file": rel, "layer": "unknown"})
                if len(out) >= CHANGED_MAX:
                    break
    except Exception:
        pass
    return out


# --- two analysis directions -------------------------------------------------

def analyze_prd_to_code(project_root, prd_text, prd_path):
    """PRD -> code: changed / affected(1-hop) / layers / blast radius."""
    nodes = parse_prd(prd_text)
    entries, _index = load_code_map(project_root)
    changed, seen_ids = [], set()
    matched_terms = []

    if entries:
        for node in nodes:
            hits = _entry_hits(entries, node["term"])
            if hits:
                matched_terms.append({
                    "term": node["term"], "kind": node["kind"],
                    "hits": [h[1] for h in hits[:8]],
                })
            for _score, eid, _e in hits:
                if eid not in seen_ids:
                    seen_ids.add(eid)
                    changed.append(entries[eid])
                if len(changed) >= CHANGED_MAX:
                    break
        changed = changed[:CHANGED_MAX]
        # 1-hop over the changed set (bounded, dedup)
        affected, seen2 = [], set(seen_ids)
        for eid in list(seen_ids):
            for nb in _hop1_neighbors(entries, eid, seen2):
                affected.append(nb)
    else:
        # degrade: direct source scan (no code-map required)
        changed = _degrade_scan(project_root, [n["term"] for n in nodes])
        affected = []

    layers = sorted({(e.get("layer") or "unknown") for e in changed + affected})
    real_layers = [l for l in layers if l != "unknown"]
    payload = {
        "ok": True,
        "mode": "prd-to-code",
        "prd_path": str(prd_path),
        "prd_nodes": nodes,
        "matched_terms": matched_terms,
        "changed_nodes": [_entry_brief(e) for e in changed],
        "affected_nodes": [_entry_brief(e) for e in affected],
        "affected_layers": layers,
        "blast_radius": _grade_blast(len(changed), len(real_layers)),
    }
    return _enforce_budget(payload)


def analyze_code_to_prd(project_root, prd_text, prd_path, symbol):
    """code -> PRD: resolve symbol, collect 1-hop set, match PRD features."""
    entries, _index = load_code_map(project_root)
    if entries is None:
        return {"ok": False,
                "error": "impact-analyzer: .rpd/code-map.json missing - run code-map-generator.py first"}
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {"ok": True, "mode": "code-to-prd", "symbol": symbol,
                "resolved": False, "prd_features": []}
    affected_ids = {eid}
    for nb in _hop1_neighbors(entries, eid, set()):
        affected_ids.add(nb["id"])
    # candidate strings: name / id / file / doc of the affected set
    cands = set()
    for i in affected_ids:
        e = entries.get(i, {})
        for field in ("name", "file"):
            v = e.get(field, "")
            if isinstance(v, str) and v:
                cands.add(v.lower())
        doc = e.get("doc", "")
        if isinstance(doc, str) and doc:
            cands.add(doc.lower())
    nodes = parse_prd(prd_text)
    hits = []
    for node in nodes:
        t = node["term"].lower()
        if any(t == c or t in c or c in t for c in cands):
            hits.append(node)
    payload = {
        "ok": True,
        "mode": "code-to-prd",
        "symbol": symbol,
        "resolved": True,
        "entry_id": eid,
        "affected_ids": sorted(affected_ids),
        "prd_features": hits,
    }
    return _enforce_budget(payload)


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print("Usage: python impact-analyzer.py <project-root> --prd <prd.md> [--json]")
        print("       python impact-analyzer.py <project-root> --code-to-prd <symbol> --prd <prd.md> [--json]")
        return 1
    project_root = args[0]
    as_json = "--json" in args
    prd_path = ""
    if "--prd" in args:
        pi = args.index("--prd") + 1
        if pi < len(args):
            prd_path = args[pi]
    if not prd_path:
        print("Error: --prd <prd.md> is required", file=sys.stderr)
        return 1
    prd_file = Path(prd_path)
    if not prd_file.is_file():
        payload = {"ok": False,
                   "error": "impact-analyzer: PRD file not found: " + str(prd_path)}
        if as_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Error: " + payload["error"], file=sys.stderr)
        return 1
    try:
        prd_text = smart_read(prd_file)
    except Exception as e:
        payload = {"ok": False, "error": "impact-analyzer: unreadable PRD: " + str(e)}
        if as_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Error: " + payload["error"], file=sys.stderr)
        return 1

    if "--code-to-prd" in args:
        ci = args.index("--code-to-prd") + 1
        symbol = args[ci] if ci < len(args) else ""
        if not symbol:
            print("Error: --code-to-prd requires a symbol", file=sys.stderr)
            return 1
        payload = analyze_code_to_prd(project_root, prd_text, prd_path, symbol)
    else:
        payload = analyze_prd_to_code(project_root, prd_text, prd_path)

    if not payload.get("ok"):
        if as_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Error: " + payload.get("error", "unknown"), file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["mode"] == "prd-to-code":
            print("PRD -> code impact (R-20):")
            print("  prd_nodes=" + str(len(payload["prd_nodes"])) +
                  " changed=" + str(len(payload["changed_nodes"])) +
                  " affected(1-hop)=" + str(len(payload["affected_nodes"])) +
                  " layers=" + ",".join(payload["affected_layers"]) +
                  " blast=" + payload["blast_radius"])
            for e in payload["changed_nodes"]:
                print("  * " + e["name"] + " (" + e["kind"] + ") " + e["file"] +
                      " layer=" + e["layer"])
        else:
            print("code -> PRD (R-20): " + payload["symbol"] +
                  (" resolved -> " + payload.get("entry_id", "") +
                   " prd_features=" + str([f["term"] for f in payload.get("prd_features", [])])
                   if payload.get("resolved") else "  (unresolved)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
