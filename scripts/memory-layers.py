#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RPD v2 layered memory (R-21): L0 evidence -> L1 atom -> L2 scenario -> L3 profile.

TAM-style four-layer memory mapped onto the .rpd/ product layer, keeping
"low layers keep evidence, high layers keep structure":

  L0 evidence  : raw decision/scan fingerprints (sha256 + path reference only,
                 content NEVER resident; --evidence re-checks live fingerprint)
  L1 atom      : atomic decision/requirement facts (one entry per fact,
                 independently referenceable, e.g. "User requires TypeScript")
  L2 scenario  : scenario blocks (PRD generation / take-over / continue-dev
                 context bundles)
  L3 profile   : long-stable project profile (tech stack, red lines, team
                 conventions)

Rules:
  - Storage: <.rpd>/memory-layers.json (product layer, human readable).
  - Import: `--import-decisions` reads .rpd/decisions.md READ-ONLY, imports
    only accepted entries into L1 (+ registers decisions.md in L0). The
    grill-me write authority (R-14) is untouched - we never write decisions.
  - Expiry: entries carry an optional `expires` (YYYY-MM-DD); expired entries
    stay readable but are flagged, and can be dropped via `--expired --drop`.
  - Retrieval fallback (R-21): default guidance reads L2+L3 only; `--fact`
    falls back to L1; `--evidence` falls back to L0 (fingerprint check, no
    content injection). Never guesses: `--fact` with no hit returns
    fallback_evidence hint + resolved:false.
  - Bloat guard: per-layer caps (L1<=500 atoms, L2<=100 scenarios) surface a
    warning in `--stats`; single-layer growth is contained, never silently.
  - Degrade: missing / corrupted store never crashes (ok stays true, empty).

Zero external deps (Q1). Budget-guard spirit (R-07): list outputs are capped.

Usage:
  python memory-layers.py <project-root> --add --layer L1 --id m1 --title "..." --text "..." [--meta '{}'] [--expires 2026-09-01]
  python memory-layers.py <project-root> --import-decisions [--json]
  python memory-layers.py <project-root> [--json]                     # fast path L2+L3
  python memory-layers.py <project-root> --fact <keyword> [--json]    # fallback L1
  python memory-layers.py <project-root> --evidence <path> [--json]   # fallback L0
  python memory-layers.py <project-root> --list [--layer L1|L2|L3] [--json]
  python memory-layers.py <project-root> --read --layer L1 --id m1 [--json]
  python memory-layers.py <project-root> --stats [--json]
  python memory-layers.py <project-root> --expired [--layer L1|L2|L3] [--drop-clean]

Exit codes: 0 ok (incl. legitimate empty); 1 usage/not-found; 2 write failure.
"""

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MEMORY_FILE = ".rpd/memory-layers.json"
DECISIONS_REL = ".rpd/decisions.md"
LAYERS = ("L0", "L1", "L2", "L3")
WRITABLE = ("L1", "L2", "L3")
DEFAULT_LIST_LIMIT = 20
BLOAT_L1 = 500
BLOAT_L2 = 200
SCENARIO_DEFAULT = "project"


def now_iso():
    return datetime.now().strftime("%Y-%m-%d")


def sha256_of_file(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def smart_read(file_path):
    encodings = ["utf-8-sig", "utf-8", "gbk", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json_atomic(path, obj):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        return True
    except Exception:
        return False


def ensure_store(root):
    data = read_json(root / MEMORY_FILE)
    if isinstance(data, dict) and isinstance(data.get("layers"), dict):
        for l in LAYERS:
            if not isinstance(data["layers"].get(l), dict):
                data["layers"][l] = {}
        return data
    return {"layers": {l: {} for l in LAYERS}, "updated_at": None}


def entry_expired(entry):
    exp = entry.get("expires")
    if not exp:
        return False
    try:
        return exp <= now_iso()
    except Exception:
        return False


def _norm_evidence_key(path_ref):
    """Normalize an evidence path to a stable store key (keep .rpd/ prefix:
    keys double as real project-relative paths for fingerprint re-checks)."""
    s = str(path_ref).replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s


# --- core write / read ------------------------------------------------------


def add_entry(root, layer, entry):
    """Add one L1/L2/L3 entry. Returns (ok, err_or_data). L0 is index-only."""
    if layer not in WRITABLE:
        return False, "L0 is index-only (use --evidence to fingerprint a file)"
    store = ensure_store(root)
    eid = entry.get("id") or entry.get("title")
    if not eid:
        return False, "--id required"
    store["layers"][layer][eid] = {
        "title": entry.get("title", ""),
        "text": entry.get("text", ""),
        "meta": entry.get("meta", {}),
        "scope": entry.get("scope", SCENARIO_DEFAULT) if layer == "L2" else None,
        "expires": entry.get("expires"),
        "updated_at": now_iso(),
        "source": entry.get("source"),
        "source_ref": entry.get("source_ref"),
    }
    if not write_json_atomic(root / MEMORY_FILE, store):
        return False, "write failed"
    return True, eid


def register_evidence(root, path_ref):
    """L0: register an evidence file (fingerprint only, never content)."""
    p = root / path_ref
    store = ensure_store(root)
    key = _norm_evidence_key(path_ref)
    store["layers"]["L0"][key] = {
        "path_ref": key,
        "fingerprint": sha256_of_file(p) if p.is_file() else None,
        "updated_at": now_iso(),
    }
    if not write_json_atomic(root / MEMORY_FILE, store):
        return False, "write failed"
    return True, key


def import_decisions(root):
    """L0+L1 from decisions.md: ONLY accepted entries, read-only source.
    Grill-me write authority (R-14) untouched - we never modify decisions.md."""
    dp = root / DECISIONS_REL
    if not dp.is_file():
        return {"ok": True, "imported": 0, "total_accepted": 0, "note": "no decisions.md"}
    content = smart_read(str(dp))
    accepted = []
    for m in re.finditer(
        r"(?m)^## D-(\d+)[ \t]+([^\n]+)\n((?:^- \*\*[^*\n]+\*\*: .*\n)+)",
        content,
    ):
        n, title = int(m.group(1)), m.group(2).strip()
        fields = {}
        for line in m.group(3).strip().split("\n"):
            fm = re.match(r"^- \*\*([A-Za-z_]+)\*\*: (.*)$", line.strip())
            if fm:
                fields[fm.group(1)] = fm.group(2).strip()
        if fields.get("status", "").strip().lower() == "accepted":
            accepted.append({"n": n, "title": title, **fields})
    store = ensure_store(root)
    imported = 0
    for a in accepted:
        eid = f"d{a['n']}"
        if eid in store["layers"]["L1"]:
            continue
        store["layers"]["L1"][eid] = {
            "title": a.get("title", ""),
            "text": a.get("decision", ""),
            "meta": {"type": a.get("type", ""), "impact": a.get("impact", ""),
                     "confirmed_by": a.get("confirmed_by", "")},
            "scope": None,
            "expires": None,
            "updated_at": now_iso(),
            "source": "decisions.md",
            "source_ref": f"{DECISIONS_REL}#D-{a['n']}",
        }
        imported += 1
    # L0: index decisions.md itself
    store["layers"]["L0"][_norm_evidence_key(DECISIONS_REL)] = {
        "path_ref": DECISIONS_REL,
        "fingerprint": sha256_of_file(dp),
        "updated_at": now_iso(),
    }
    write_json_atomic(root / MEMORY_FILE, store)
    return {"ok": True, "imported": imported, "total_accepted": len(accepted)}


# --- retrieval (R-21 fallback ordering) -------------------------------------


def fast_path(root, scope=SCENARIO_DEFAULT, limit=DEFAULT_LIST_LIMIT):
    """Default fast guidance: L2 scenarios (scope) + L3 profile ONLY.
    L1/L0 are NOT injected here (progressive exposure, R-23 spirit)."""
    store = ensure_store(root)
    l2 = []
    for eid, e in (store["layers"].get("L2") or {}).items():
        if (e.get("scope") or SCENARIO_DEFAULT) == scope:
            l2.append({"id": eid, **e, "expired": entry_expired(e)})
    l2.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    l3 = [{"id": eid, **e, "expired": entry_expired(e)}
          for eid, e in (store["layers"].get("L3") or {}).items()]
    l3.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return {
        "ok": True,
        "path": "L2+L3",
        "scenarios": l2[:limit],
        "profile": l3[:limit],
        "fallback_hint": "需事实: --fact <kw> 回退 L1; 需原始证据: --evidence <path> 回退 L0",
    }


def _kw_atoms(store, keyword, limit=DEFAULT_LIST_LIMIT):
    toks = {t.lower() for t in re.findall(r"[A-Za-z0-9_\-.\u4e00-\u9fff]+", keyword or "")}
    hits = []
    for eid, e in (store["layers"].get("L1") or {}).items():
        hay = " ".join([str(e.get("title", "")), str(e.get("text", "")),
                        str(e.get("meta", {}))]).lower()
        if toks and any(t in hay for t in toks):
            hits.append({"id": eid, **e, "expired": entry_expired(e)})
    hits.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return hits[:limit]


def fact_fallback(root, keyword, limit=DEFAULT_LIST_LIMIT):
    """--fact: fall back from L2/L3 to L1 atoms; miss -> fallback_evidence hint
    (resolved:false, never guesses/invents)."""
    store = ensure_store(root)
    hits = _kw_atoms(store, keyword, limit)
    if not hits:
        return {
            "ok": True,
            "resolved": False,
            "fallback_evidence": DECISIONS_REL,
            "hint": "L1 无匹配；可用 --evidence .rpd/decisions.md 回退 L0 原始证据（不猜）",
        }
    return {"ok": True, "resolved": True, "matches": hits}


def evidence_fallback(root, path_ref):
    """--evidence: L0 record (fingerprint + read location), live re-check,
    content is NOT injected (low layers keep evidence)."""
    key = _norm_evidence_key(path_ref)
    store = ensure_store(root)
    rec = (store["layers"].get("L0") or {}).get(key)
    fp = sha256_of_file(root / key)
    if rec is None:
        rec = {"path_ref": key, "fingerprint": fp, "updated_at": now_iso(),
               "registered_on_demand": True}
    live_matches = (fp is not None and rec.get("fingerprint") == fp)
    return {
        "ok": True,
        "path": key,
        "record": rec,
        "live_fingerprint": fp,
        "content_matches": live_matches,
        "hint": "L0 只存指纹，需原文请按 path 直接 Read（证据不常驻）",
    }


def list_entries(root, layer=None, limit=DEFAULT_LIST_LIMIT):
    store = ensure_store(root)
    layers = {l: {} for l in LAYERS}
    targets = (layer,) if layer else LAYERS
    for l in targets:
        items = [{"id": eid, **e, "expired": entry_expired(e)}
                 for eid, e in (store["layers"].get(l) or {}).items()]
        items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        layers[l] = items[:limit]
    return {"ok": True, "layers": layers}


def read_entry(root, layer, eid):
    store = ensure_store(root)
    entry = (store["layers"].get(layer) or {}).get(eid)
    if entry is None:
        return {"ok": False, "error": f"{layer}:{eid} not found"}
    return {"ok": True, "layer": layer, "id": eid, **entry, "expired": entry_expired(entry)}


def expired_report(root, drop=False, layer=None):
    store = ensure_store(root)
    targets = (layer,) if layer else WRITABLE
    dropped, expired = {}, {}
    for l in targets:
        cands = store["layers"].get(l) or {}
        exp = {eid: e for eid, e in cands.items() if entry_expired(e)}
        expired[l] = list(exp.keys())
        if drop:
            for eid in exp:
                del store["layers"][l][eid]
            dropped[l] = len(exp)
    if drop:
        write_json_atomic(root / MEMORY_FILE, store)
    return {"ok": True, "expired": expired, "dropped": dropped}


def stats(root):
    store = ensure_store(root)
    counts = {l: len(store["layers"].get(l) or {}) for l in LAYERS}
    expired = {l: sum(1 for e in (store["layers"].get(l) or {}).values() if entry_expired(e))
               for l in LAYERS}
    warnings = []
    if counts["L1"] > BLOAT_L1:
        warnings.append(f"L1 原子数 {counts['L1']} > {BLOAT_L1}，单层膨胀，建议蒸馏/清理")
    if counts["L2"] > BLOAT_L2:
        warnings.append(f"L2 场景块 {counts['L2']} > {BLOAT_L2}，单层膨胀，考虑归档")
    return {
        "ok": True,
        "counts": counts,
        "expired": expired,
        "warnings": warnings,
        "fallback": "L2/L3 引导 -> --fact 回退 L1 -> --evidence 回退 L0",
    }


# --- CLI ---------------------------------------------------------------------


def _take(args, key):
    """Pop --key <val> from args; returns (rest, val-or-None)."""
    for i, a in enumerate(args):
        if a == key and i + 1 < len(args):
            return args[:i] + args[i + 2:], args[i + 1]
    return args, None


def _emit(obj, as_json):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        def _fmt_item(it):
            head = it.get("title") or it.get("text") or ""
            mark = " [expired]" if it.get("expired") else ""
            return f"  {it.get('id','?')}: {str(head)[:70]}{mark}"
        for key, label in (("scenarios", "L2 scenarios"), ("profile", "L3 profile"),
                           ("matches", "L1 matches"), ("record", "L0 record")):
            val = obj.get(key)
            if val is None:
                continue
            if isinstance(val, list):
                print(f"[{label}]")
                for it in val:
                    print(_fmt(it))
            else:
                print(f"[{label}] {val}")
        cur = obj.get("counts")
        if cur:
            print("counts: " + " ".join(f"{k}={v}" for k, v in cur.items()))
            for w in obj.get("warnings", []):
                print("WARN: " + w)
        if "imported" in obj:
            print(f"imported={obj['imported']} total_accepted={obj.get('total_accepted', 0)}")
        if obj.get("ok") is False:
            print("error: " + obj.get("error", "?"))



def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    root = Path(args[0])
    if not root.is_dir():
        print(f"Error: not a directory: {root}", file=sys.stderr)
        return 1
    rest = args[1:]
    as_json = "--json" in rest
    rest = [a for a in rest if a != "--json"]

    if not rest:
        _emit(fast_path(root), as_json)
        return 0

    cmd = rest[0]
    tail = rest[1:]

    if cmd == "--add":
        tail, layer = _next_val(tail, "--layer")
        tail, eid = _next_val(tail, "--id")
        tail, title = _next_val(tail, "--title")
        tail, text = _next_val(tail, "--text")
        tail, meta_raw = _next_val(tail, "--meta")
        tail, scope = _next_val(tail, "--scope")
        tail, expires = _next_val(tail, "--expires")
        if not layer or not eid:
            print("Error: --add needs --layer and --id", file=sys.stderr)
            return 1
        meta = {}
        if meta_raw:
            try:
                meta = json.loads(meta_raw)
            except Exception:
                meta = {"raw": meta_raw}
        entry = {"id": eid, "title": title or "", "text": text or "", "meta": meta,
                 "scope": scope, "expires": expires}
        ok, res = add_entry(root, layer, entry)
        if not ok:
            print(f"Error: {res}", file=sys.stderr)
            return 2
        print(json.dumps({"ok": True, "layer": layer, "id": res}, ensure_ascii=False) if as_json
              else f"added {layer}:{res}")
        return 0

    if cmd == "--evidence":
        tail2, path_ref = _next_val(tail, "--path")
        if not path_ref and tail2:
            path_ref = tail2[0]
        if not path_ref:
            print("Error: --evidence needs a path", file=sys.stderr)
            return 1
        _emit(evidence_fallback(root, path_ref), as_json)
        return 0

    if cmd == "--import-decisions":
        _emit(import_decisions(root), as_json)
        return 0

    if cmd == "--fact":
        tail2, kw = _next_val(tail, "--keyword")
        if not kw and tail2:
            kw = tail2[0]
        if not kw:
            print("Error: --fact needs a keyword", file=sys.stderr)
            return 1
        _emit(fact_fallback(root, kw), as_json)
        return 0

    if cmd == "--list":
        tail2, layer = _next_val(tail, "--layer")
        _emit(list_entries(root, layer=layer), as_json)
        return 0

    if cmd == "--read":
        tail2, layer = _next_val(tail, "--layer")
        _, eid = _next_val(tail2, "--id")
        if not layer or not eid:
            print("Error: --read requires --layer and --id", file=sys.stderr)
            return 1
        _emit(read_entry(root, layer, eid), as_json)
        return 0

    if cmd == "--stats":
        _emit(stats(root), as_json)
        return 0

    if cmd == "--expired":
        drop = "--drop-clean" in tail
        _, layer = _next_val(tail, "--layer")
        _emit(expired_report(root, drop=drop, layer=layer), as_json)
        return 0

    print(f"Error: unknown command '{cmd}'", file=sys.stderr)
    return 1




def _next_val(args, key, default=None):
    """Read --key <val> from args (do not mutate); returns (args, val-or-default)."""
    for i, a in enumerate(args):
        if a == key and i + 1 < len(args):
            tail = args[:i] + args[i + 2:]
            return tail, args[i + 1]
    return args, default

if __name__ == "__main__":
    sys.exit(main())
