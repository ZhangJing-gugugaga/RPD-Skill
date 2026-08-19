#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RPD v2 hybrid retriever (R-22): BM25 lexical + exact-name + RRF fusion.

Reads <project-root>/.rpd/code-map.json and answers a plain-language or
exact-name query with ranked Layer-2 entries.

  - exact channel : R-11 compatible - symbol exact hits surface first
  - bm25 channel   : zero-dependency BM25 over name/file/signature/doc
  - vector channel : R-22 Q1 - disabled (zero external deps); TODO note
  - rrf            : Reciprocal Rank Fusion over active channels (k=60)

Budget guard (R-07): result list truncated to <= RESULT_MAX_TOKENS.

Usage:
  python retriever.py <project-root> --query "payment retry" [--top 5] [--json]
  python retriever.py <project-root> --who-calls <symbol> [--json]   (R-19 edges)
  python retriever.py <project-root> --deps-of  <symbol> [--json]   (R-19 edges)
  python retriever.py <project-root> --layer-of <symbol> [--json]   (R-19 layer)

R-19 edge queries answer three questions over the mapped graph:
  - who-calls : entries whose edges point to <symbol> (incoming callers)
  - deps-of   : <symbol> own edges (outgoing dependencies)
  - layer-of  : <symbol> architecture layer (entry.layer, or via contains parent)

Exit codes: 0 success; 1 usage error / code-map.json missing.
NOTE: .rpd/code-map.json is READ-ONLY here.
"""

import json
import math
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CODE_MAP_FILE = ".rpd/code-map.json"
RESULT_MAX_TOKENS = 300
RRF_K = 60
BM25_K1 = 1.5
BM25_B = 0.75

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+")


def tokenize(text):
    """Lowercase vocab tokens; split underscore and camelCase.

    CJK runs are emitted both whole and as bigrams so Chinese queries can
    overlap with Chinese doc comments (e.g. query "支付重试逻辑" vs doc
    "支付重试逻辑：失败后指数退避重试").
    """
    out = []
    for m in _TOKEN_RE.finditer(text or ""):
        tok = m.group(0)
        if tok[0].isascii():
            for piece in re.split(r"_+", tok):
                if not piece:
                    continue
                for sub in re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[0-9]+", piece):
                    if sub:
                        out.append(sub.lower())
        else:
            out.append(tok)
            if len(tok) > 1:
                for i in range(len(tok) - 1):
                    out.append(tok[i:i + 2])
    return out


def normalize_name(name):
    """Loose identity: strip spaces and ::."""
    return re.sub(r"[\s:]+", "", (name or "")).lower()


def load_code_map(project_root):
    """Return (entries, inverted_index) or (None, None) if missing."""
    path = Path(project_root) / CODE_MAP_FILE
    if not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None, None
    return data.get("entries", {}), data.get("inverted_index", {})

# --- BM25 (zero dependency) -------------------------------------------------


def build_docs(entries):
    """Term-frequency map per entry over name(2x)/file/signature/doc."""
    docs = {}
    for eid, entry in entries.items():
        parts = [
            entry.get("name", ""),
            entry.get("name", ""),
            entry.get("file", ""),
            entry.get("signature", ""),
            entry.get("doc", ""),
        ]
        text = " ".join(parts)
        tf = {}
        for t in tokenize(text):
            tf[t] = tf.get(t, 0) + 1
        docs[eid] = tf
    return docs


def bm25_rank(query_terms, docs, k1=BM25_K1, b=BM25_B):
    """Pure-Python BM25 over term-freq maps. Returns [(eid, score)] desc."""
    if not query_terms:
        return []
    N = max(1, len(docs))
    doc_lens = {eid: sum(tf.values()) for eid, tf in docs.items()}
    avg_dl = sum(doc_lens.values()) / N if N else 0.0
    df = {}
    for tf in docs.values():
        for t in query_terms:
            if t in tf:
                df[t] = df.get(t, 0) + 1
    scores = {}
    for eid, tf in docs.items():
        dl = doc_lens[eid]
        s = 0.0
        for t in query_terms:
            f = tf.get(t, 0)
            if f == 0:
                continue
            n_t = df.get(t, 0)
            idf = math.log(1.0 + (N - n_t + 0.5) / (n_t + 0.5))
            denom = f + k1 * (1.0 - b + b * (dl / avg_dl if avg_dl else 1.0))
            s += idf * (f * (k1 + 1.0)) / denom
        if s > 0:
            scores[eid] = s
    return sorted(scores.items(), key=lambda kv: -kv[1])


def search_bm25(query_terms, docs, top_n=None):
    ranked = bm25_rank(query_terms, docs)
    if top_n is not None:
        ranked = ranked[:top_n]
    return [eid for eid, _ in ranked]


# --- exact channel (R-11 guarantee) -----------------------------------------


def exact_matches(entries, index, query_raw, query_terms):
    """Exact-name / last-segment / inverted-index hits. Ordered dedup [eid]."""
    out, seen = [], set()
    q_norm = normalize_name(query_raw)
    for eid, entry in entries.items():
        if normalize_name(entry.get("name", "")) == q_norm and eid not in seen:
            out.append(eid)
            seen.add(eid)
    for eid, entry in entries.items():
        seg = (entry.get("name", "") or "").split("::")[-1]
        if seg and seg.lower() == q_norm and eid not in seen:
            out.append(eid)
            seen.add(eid)
    for tok in query_terms:
        for key, ids in index.items():
            if key.lower() == tok:
                for eid in ids:
                    if eid not in seen:
                        out.append(eid)
                        seen.add(eid)
    for tok in query_terms:
        if not tok.isascii():
            continue
        for eid, entry in entries.items():
            if eid in seen:
                continue
            if tok in normalize_name(entry.get("name", "")):
                out.append(eid)
                seen.add(eid)
    return out

# --- RRF + budget ------------------------------------------------------------


def rrf_fuse(ranked_lists, k=RRF_K):
    """Reciprocal Rank Fusion over ranked eid lists."""
    scores = {}
    for lst in ranked_lists:
        for rank, eid in enumerate(lst):
            scores[eid] = scores.get(eid, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def estimate_tokens(obj):
    try:
        return max(1, len(json.dumps(obj, ensure_ascii=False, separators=(",", ":"))) // 4)
    except Exception:
        return 0


def build_results(entries, fused, exact_ids):
    results = []
    for rank, (eid, score) in enumerate(fused):
        entry = entries.get(eid)
        if entry is None:
            continue
        res = {
            "rank": rank + 1,
            "score": round(score, 6),
            "channel": "exact" if eid in exact_ids else "bm25",
            "id": eid,
            "name": entry.get("name", ""),
            "kind": entry.get("kind", ""),
            "file": entry.get("file", ""),
            "line": entry.get("line", 0),
            "ref": "code-map.json#" + eid,
            "estimated_tokens": 0,
        }
        res["estimated_tokens"] = estimate_tokens(res)
        results.append(res)
    return results


def enforce_budget(results, limit=RESULT_MAX_TOKENS):
    total, kept = 0, []
    for r in results:
        if total + r["estimated_tokens"] > limit and kept:
            break
        total += r["estimated_tokens"]
        kept.append(r)
    return kept


# --- R-19 edge queries (who-calls / deps-of / layer-of) ----------------------
#
# The three questions I4-2 must answer over the mapped graph:
#   - "who calls X"        -> entries whose edges point AT X (incoming callers)
#   - "X depends on whom"  -> X's own edges (outgoing dependencies)
#   - "which layer is X in"-> entry.layer (enriched from KG node), else "unknown"
# Query routing is by CLI flag; falls back to exact-name resolution (same 3-level
# mapping as the generator: entry id -> name -> bare last segment).


def resolve_symbol(entries, symbol):
    """Map a user-supplied symbol to an entry id (exact name first, then id,
    then bare last segment). Returns None when unresolved (degrade, no guess)."""
    s = (symbol or "").strip()
    if not s:
        return None
    for eid, e in entries.items():
        if e.get("name") == s:
            return eid
    if s in entries:
        return s
    seg = s.split("::")[-1]
    hits = [eid for eid, e in entries.items() if e.get("name") == seg]
    return hits[0] if hits else None


def who_calls(entries, symbol, top_n=24):
    """Incoming callers: entries whose edges target the resolved symbol."""
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {"ok": True, "symbol": symbol, "resolved": False, "results": []}
    callers = []
    for other_id, e in entries.items():
        if other_id == eid:
            continue
        for edge in e.get("edges", []):
            if edge.get("target") == eid:
                callers.append({
                    "id": other_id,
                    "name": e.get("name", ""),
                    "kind": e.get("kind", ""),
                    "file": e.get("file", ""),
                    "edge_type": edge.get("type", ""),
                    "weight": edge.get("weight", 0),
                })
                break
    callers.sort(key=lambda c: (-c["weight"], c["name"]))
    return {
        "ok": True, "symbol": symbol, "resolved": True,
        "entry_id": eid, "count": len(callers),
        "results": callers[:top_n],
    }


def deps_of(entries, symbol, top_n=24):
    """Outgoing dependencies: the symbol's own edges (targets it depends on)."""
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {"ok": True, "symbol": symbol, "resolved": False, "results": []}
    entry = entries.get(eid, {})
    deps = []
    for edge in entry.get("edges", []):
        tgt = entries.get(edge.get("target", ""), {})
        deps.append({
            "id": edge.get("target", ""),
            "name": tgt.get("name", edge.get("target", "")),
            "kind": tgt.get("kind", ""),
            "file": tgt.get("file", ""),
            "edge_type": edge.get("type", ""),
            "weight": edge.get("weight", 0),
        })
    deps.sort(key=lambda d: (-d["weight"], d["name"]))
    return {
        "ok": True, "symbol": symbol, "resolved": True,
        "entry_id": eid, "count": len(deps),
        "results": deps[:top_n],
    }


def layer_of(entries, symbol):
    """Architecture layer: entry.layer (KG-enriched) else 'unknown'."""
    eid = resolve_symbol(entries, symbol)
    if eid is None:
        return {"ok": True, "symbol": symbol, "resolved": False, "layer": None}
    return {
        "ok": True, "symbol": symbol, "resolved": True,
        "entry_id": eid,
        "layer": entries.get(eid, {}).get("layer", "unknown"),
    }


def run_edge_query(project_root, qtype, symbol, top_n=24):
    """R-19 edge query over .rpd/code-map.json. qtype in who-calls|deps-of|layer-of."""
    entries, _ = load_code_map(project_root)
    if entries is None:
        return {
            "ok": False,
            "error": "retriever: " + CODE_MAP_FILE + " missing - run code-map-generator.py first",
        }
    if qtype == "who-calls":
        payload = who_calls(entries, symbol, top_n)
    elif qtype == "deps-of":
        payload = deps_of(entries, symbol, top_n)
    elif qtype == "layer-of":
        payload = layer_of(entries, symbol)
    else:
        return {"ok": False, "error": "retriever: unknown edge query type: " + str(qtype)}
    payload["budget"] = {
        "result_max_tokens": RESULT_MAX_TOKENS,
        "estimated_results_tokens": estimate_tokens(payload.get("results", [])),
    }
    return payload


def run(project_root, query, top_n=5):
    """Hybrid retrieval over .rpd/code-map.json. Returns dict."""
    entries, index = load_code_map(project_root)
    if entries is None:
        return {
            "ok": False,
            "error": "retriever: " + CODE_MAP_FILE + " missing - run code-map-generator.py first",
        }
    query_terms = tokenize(query)
    docs = build_docs(entries)
    exact_ids = set(exact_matches(entries, index, query, query_terms))
    exact_list = [eid for eid in exact_ids][: top_n * 2]
    bm25_list = search_bm25(query_terms, docs, top_n=top_n * 3)
    fused = rrf_fuse([exact_list, bm25_list])
    if not fused:
        fused = [(eid, 0.0) for eid in sorted(entries)[:top_n]]
    results = enforce_budget(build_results(entries, fused, exact_ids))
    return {
        "ok": True,
        "query": query,
        "top_k": top_n,
        "channels": {
            "exact": {"enabled": True, "matched": len(exact_list)},
            "bm25": {"enabled": True},
            "vector": {
                "enabled": False,
                "note": "R-22 Q1 zero-dep first: vector channel TODO until an external embedding dep is added",
            },
        },
        "results": results,
        "budget": {
            "result_max_tokens": RESULT_MAX_TOKENS,
            "estimated_results_tokens": sum(r["estimated_tokens"] for r in results),
        },
    }


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        print("Usage: python retriever.py <project-root> --query <text> [--top 5] [--json]")
        print("       python retriever.py <project-root> --who-calls|--deps-of|--layer-of <symbol> [--json]")
        return 1
    project_root = args[0]
    as_json = "--json" in args

    # R-19 edge queries: --who-calls / --deps-of / --layer-of <symbol>
    for flag in ("--who-calls", "--deps-of", "--layer-of"):
        if flag in args:
            fi = args.index(flag) + 1
            symbol = args[fi] if fi < len(args) else ""
            if not symbol:
                print("Error: " + flag + " requires a symbol", file=sys.stderr)
                return 1
            qtype = flag[2:]  # who-calls / deps-of / layer-of
            payload = run_edge_query(project_root, qtype, symbol)
            if not payload["ok"]:
                print(payload["error"], file=sys.stderr)
                return 1
            if as_json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(qtype + ": " + symbol +
                      ("  resolved -> " + payload.get("entry_id", "") +
                       ("  layer=" + payload.get("layer", "") if "layer" in payload else "")
                       if payload.get("resolved") else "  (unresolved)"))
                for r in payload.get("results", []):
                    print("  - " + r["name"] + " (" + r["kind"] + ") " + r["file"] +
                          " [" + r["edge_type"] + " w=" + str(r["weight"]) + "]")
                if payload.get("resolved") and not payload.get("results"):
                    print("  (no " + qtype + " results)")
            return 0

    query = ""
    if "--query" in args:
        qi = args.index("--query") + 1
        if qi >= len(args):
            print("Error: --query requires a value", file=sys.stderr)
            return 1
        query = args[qi]
    top_n = 5
    if "--top" in args:
        ti = args.index("--top") + 1
        if ti < len(args):
            try:
                top_n = max(1, int(args[ti]))
            except ValueError:
                pass
    payload = run(project_root, query, top_n)
    if not payload["ok"]:
        print(payload["error"], file=sys.stderr)
        return 1
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print('query: "' + query + '"  top_k=' + str(top_n))
        print("  channels: exact + bm25 fused (vector TODO)")
        for r in payload["results"]:
            print("  #" + str(r["rank"]) + " [" + r["channel"] + "] " + r["name"] +
                  " (" + r["kind"] + ") " + r["file"] + ":" + str(r["line"]) +
                  " ~" + str(r["estimated_tokens"]) + "t ref=" + r["ref"])
        if not payload["results"]:
            print("  (no results)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
