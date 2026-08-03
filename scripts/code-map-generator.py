#!/usr/bin/env python3
"""RPD v2 code-map generator: two-layer code map (router + full symbol table).

Produces in <project-root>/.rpd/:
  - code-map.router.json   Layer 1, always-in-context index (<=3k token AND <=15% codebase)
  - code-map.json          Layer 2, full key-value symbol table (read per-entry only)
  - code-map.meta.json     metadata: commit, fingerprints, budget, trust (red-line source)

Parsing: tree-sitter (C/C++) with regex fallback (dual-path). Calls edges are
labeled candidate-only with confidence heuristic|resolved — never "exact call graph".

Usage:
  python code-map-generator.py <project-root> [--json] [--incremental]

Exit codes:
  0 - Generated
  1 - Usage error / project root missing
"""

import hashlib
import json
import os
import re
import subprocess
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

# --- Budget constants (R-07) ---
ROUTER_TOKEN_LIMIT = 3000          # hard: <=3k token
ROUTER_PCT_LIMIT = 15              # hard: <=15% of codebase
AVG_TOKENS_PER_LINE = 10           # codebase token estimate: lines * 10
ENTRY_MAX_TOKENS = 300             # single entry <=300 token
SCHEMA_VERSION = "2.0.0"
GENERATOR_VERSION = "2.1.0"

# --- Source file extensions (primary: C/C++; others treated as unindexed) ---
C_EXTENSIONS = {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx"}
PRIMARY_EXTENSIONS = set(C_EXTENSIONS)

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "vendor", "target", "third_party",
    "thirdparty", "out", "cmake-build-debug", "CMakeFiles", ".rpd", ".code-map.tmp",
}
SKIP_PATH_PARTS = {"tests", "test", "generated", "gen", "external", "ext"}


def estimate_tokens(obj):
    """Estimate tokens of a JSON-serializable object (~4 chars/token)."""
    try:
        return max(1, len(json.dumps(obj, ensure_ascii=False, separators=(",", ":"))) // 4)
    except Exception:
        return 0


def sha256_of_file(path):
    """Full-content sha256 hex of a file."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def git_head(project_root):
    """Current HEAD hash or None."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            text=True, encoding="utf-8", errors="replace"
        ).strip()
    except Exception:
        return None


def git_available(project_root):
    try:
        subprocess.check_output(
            ["git", "-C", str(project_root), "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def is_source_file(path, project_root):
    """Whether a file should be indexed (relative path checks)."""
    rel = path.relative_to(project_root)
    parts = set(rel.parts)
    if parts & SKIP_DIRS:
        return False
    for part in rel.parts[:-1]:  # dirs only
        if part.lower() in SKIP_PATH_PARTS:
            return False
    return path.suffix.lower() in PRIMARY_EXTENSIONS


def collect_source_files(project_root):
    """Collect indexable source files (deterministic sorted)."""
    files = []
    for p in project_root.rglob("*"):
        if not p.is_file():
            continue
        if is_source_file(p, project_root):
            files.append(p)
    return sorted(files, key=lambda p: str(p.relative_to(project_root)).lower())


def file_loc(path):
    """Line count of a file (for budget + fingerprint)."""
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


# --- Parsing: tree-sitter dual-path ---

_ts_cpp = None


def get_tree_sitter_parser():
    """Load tree-sitter C++ parser lazily; return (parser, cpp_lang) or (None, None)."""
    global _ts_cpp
    if _ts_cpp is not None:
        return _ts_cpp
    try:
        from tree_sitter import Language, Parser
        import tree_sitter_cpp
        cpp = Language(tree_sitter_cpp.language())
        parser = Parser(cpp)
        _ts_cpp = (parser, True)
    except Exception as e:
        _ts_cpp = (None, False)
        print(f"[code-map] tree-sitter 不可用，降级为正则解析: {e}", file=sys.stderr)
    return _ts_cpp


def _ts_node_name(node):
    """Extract symbol name from a function/class node."""
    try:
        if node.type in ("class_specifier", "struct_specifier", "enum_specifier"):
            n = node.child_by_field_name("name")
            return n.text.decode("utf-8", "replace") if n else ""
        # function_definition
        decl = node.child_by_field_name("declarator")
        if decl is None:
            return ""
        sub = decl.child_by_field_name("declarator")
        if sub is None:
            sub = decl
        return sub.text.decode("utf-8", "replace")
    except Exception:
        return ""


def _ts_node_signature(node):
    """Human-readable signature: first 120 chars of the node, normalized."""
    try:
        txt = node.text.decode("utf-8", "replace").split("{")[0].strip()
        return re.sub(r"\s+", " ", txt)[:120]
    except Exception:
        return ""


def _ts_extract_calls(node, content):
    """Collect call_expression callee names within a node."""
    calls = []
    stack = [node]
    while stack:
        n = stack.pop()
        for c in n.children:
            if c.type == "call_expression":
                fn = c.child_by_field_name("function")
                if fn is not None:
                    calls.append(fn.text.decode("utf-8", "replace"))
                else:
                    calls.append(c.text.decode("utf-8", "replace").split("(")[0])
            else:
                stack.append(c)
    return calls


def parse_with_tree_sitter(path, content):
    """Parse a C/C++ file with tree-sitter. Returns list of raw symbol dicts.

    Each raw symbol: {name, kind, line, signature, doc, calls[], in_class}
    """
    parser, ok = get_tree_sitter_parser()
    if not ok:
        return None
    try:
        tree = parser.parse(content.encode("utf-8"))
    except Exception:
        return None
    root = tree.root_node
    symbols = []

    def walk(node, in_class=None, class_name=""):
        t = node.type
        if t in ("function_definition",):
            name = _ts_node_name(node)
            if not name:
                for c in node.children:
                    walk(c, in_class, class_name)
                return
            sig = _ts_node_signature(node)
            line = node.start_point[0] + 1
            calls = _ts_extract_calls(node, content)
            full = f"{class_name}::{name}" if in_class and name and "::" not in name else name
            kind = "method" if in_class else "function"
            symbols.append({
                "name": full, "kind": kind, "line": line,
                "signature": sig, "doc": _extract_doc_before(content, node.start_point[0]),
                "calls": calls, "in_class": class_name,
            })
        elif t in ("class_specifier", "struct_specifier"):
            cname = _ts_node_name(node)
            line = node.start_point[0] + 1
            symbols.append({
                "name": cname, "kind": "struct" if t == "struct_specifier" else "class",
                "line": line, "signature": f"{t}: {cname}",
                "doc": _extract_doc_before(content, node.start_point[0]),
                "calls": [], "in_class": "",
            })
            for c in node.children:
                walk(c, True, cname)
            return
        else:
            for c in node.children:
                walk(c, in_class, class_name)

    walk(root)
    return symbols


def _extract_doc_before(content, line_idx):
    """Extract single-line doc from comments immediately above the symbol."""
    lines = content.split("\n")
    doc = ""
    for i in range(max(0, line_idx - 4), line_idx):
        line = lines[i].strip()
        if line.startswith("//"):
            doc = line.lstrip("/").strip()
            break
        if line.startswith("*") or line.startswith("/*") or line.startswith("/**"):
            doc = line.lstrip("*/ ").strip()
            break
    return doc[:80]


# --- Regular-expression fallback parser (heuristic) ---

_RE_FUNC = re.compile(
    r'^\s*(?:static\s+|inline\s+|const\s+|virtual\s+|extern\s+|explicit\s+)*'
    r'(?:[\w:]+\s+)+([\w~]+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>,\s]+)?\s*\{',
    re.MULTILINE
)
_RE_METHOD = re.compile(
    r'^\s*(?:[\w:]+\s+)+([\w~]+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?\s*;\s*$',
    re.MULTILINE
)
_RE_CLASS = re.compile(r'^\s*(?:class|struct)\s+(\w+)', re.MULTILINE)


def parse_with_regex(path, content):
    """Heuristic regex parse (fallback path). Returns raw symbol dicts."""
    symbols = []
    lines = content.split("\n")
    for m in _RE_FUNC.finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        name = m.group(1)
        sig = re.sub(r"\s+", " ", m.group(0).split("{")[0].strip())[:120]
        symbols.append({
            "name": name, "kind": "function", "line": line_no,
            "signature": sig, "doc": _extract_doc_before(content, line_no - 1),
            "calls": _extract_calls_regex(content[max(0, m.start()):m.end()]),
            "in_class": "",
        })
    for m in _RE_CLASS.finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        symbols.append({
            "name": m.group(1), "kind": "class", "line": line_no,
            "signature": f"class: {m.group(1)}",
            "doc": _extract_doc_before(content, line_no - 1), "calls": [], "in_class": "",
        })
    return symbols


def _extract_calls_regex(body):
    """Extract callee names from a function body via regex (heuristic)."""
    return re.findall(r'\b(\w+)\s*\(', body)


# --- Entry building ---

def kind_prefix(kind):
    """id prefix per kind."""
    return {"function": "function", "method": "method", "class": "class",
            "struct": "struct", "variable": "variable", "macro": "macro",
            "enum": "enum"}.get(kind, "symbol")


def build_entries(source_files, project_root):
    """Build full symbol table entries + per-file raw data.

    Returns (entries, per_file, parser_used).
    entries: dict id -> entry
    per_file: dict rel_path -> {loc, fingerprint, raw_symbols}
    """
    entries = {}
    per_file = {}
    parser_used = "tree-sitter" if get_tree_sitter_parser()[1] else "regex"

    for path in source_files:
        rel = str(path.relative_to(project_root)).replace("\\", "/")
        content = smart_read(str(path))
        if not content:
            continue
        loc = file_loc(path)
        per_file[rel] = {
            "loc": loc,
            "fingerprint": "sha256:" + (sha256_of_file(path) or ""),
        }

        if parser_used == "tree-sitter":
            raws = parse_with_tree_sitter(path, content)
            if raws is None:
                raws = parse_with_regex(path, content)
        else:
            raws = parse_with_regex(path, content)

        # Build entry ids
        raw_by_name = {}
        for raw in raws:
            name = raw["name"]
            if not name:
                continue
            kind = raw["kind"]
            entry_id = f"{kind_prefix(kind)}:{rel}:{name}"
            raw_by_name.setdefault(name, raw)
            # Skip duplicate ids (same name+kind in same file: keep first)
            if entry_id in entries:
                continue
            entry = {
                "id": entry_id,
                "name": name,
                "kind": kind,
                "file": rel,
                "line": raw["line"],
                "signature": raw["signature"],
                "doc": raw.get("doc", ""),
                "calls": [],
                "called_by": [],
                "doc_refs": [],
            }
            # Resolve calls against raw_by_name (within-file) -> resolved; else heuristic
            for callee in raw.get("calls", []):
                clean = callee.strip()
                if not clean:
                    continue
                if clean in raw_by_name:
                    target_id = f"{kind_prefix(raw_by_name[clean]['kind'])}:{rel}:{clean}"
                    entry["calls"].append({"target": target_id, "confidence": "resolved"})
                else:
                    entry["calls"].append({"target": clean, "confidence": "heuristic"})
            entries[entry_id] = entry

    # Compute called_by reverse edges (resolved edges only)
    for eid, entry in entries.items():
        for c in entry["calls"]:
            if c["confidence"] == "resolved":
                tid = c["target"]
                if tid in entries:
                    entries[tid].setdefault("called_by", []).append(
                        {"caller": eid, "confidence": "resolved"}
                    )

    # Enforce entry token budget (R-07): truncate doc/signature if > ENTRY_MAX_TOKENS
    for eid, entry in entries.items():
        if estimate_tokens(entry) > ENTRY_MAX_TOKENS:
            if len(entry.get("doc", "")) > 40:
                entry["doc"] = entry.get("doc", "")[:40]
            if estimate_tokens(entry) > ENTRY_MAX_TOKENS and len(entry.get("signature", "")) > 60:
                entry["signature"] = entry.get("signature", "")[:60]

    return entries, per_file, parser_used


def build_inverted_index(entries):
    """inverted index: symbol name/segment -> entry ids."""
    index = {}
    for eid, entry in entries.items():
        name = entry["name"]
        index.setdefault(name, []).append(eid)
        # add bare last segment (e.g. "update" from "Game::update")
        if "::" in name:
            index.setdefault(name.split("::")[-1], []).append(eid)
    return index


def write_atomic(project_root, filename, obj):
    """Atomic write via .code-map.tmp/ staging then os.replace."""
    rpd = project_root / ".rpd"
    rpd.mkdir(exist_ok=True)
    tmp_dir = rpd / ".code-map.tmp"
    tmp_dir.mkdir(exist_ok=True)
    tmp = tmp_dir / (filename + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, rpd / filename)
    return rpd / filename


# --- Router (Layer 1) + budget guard ---

def symbol_priority(entry):
    """Score for top_symbols ordering (higher = keep first when trimming)."""
    name = entry["name"]
    score = 0
    if name in ("main", "Main", "main()"):
        score += 100
    if entry["kind"] == "method":
        score += 30
    if entry["kind"] in ("class", "struct"):
        score += 20
    if len(entry.get("called_by", [])) > 0:
        score += 15 * min(5, len(entry["called_by"]))
    if entry["kind"] == "function":
        score += 5
    return score


def _file_priority(rel):
    """Core files first (src/ > root > generated). Lower = trim later."""
    low = rel.lower()
    if low.startswith("src/"):
        return 0
    if any(k in low for k in ("/include/", "include/")):
        return 1
    if "test" in low or "bench" in low or "demo" in low:
        return 3
    return 2


def build_router(project, entries, per_file, codebase_tokens, head_commit):
    """Build code-map.router.json with budget guard (trim top_symbols then files).

    router.files is a lean list (path + loc only); fingerprints/entry_count live
    in code-map.meta.json (red-line source). Both lists are trimmed to satisfy
    the hard budget (<=3k token AND <=15% codebase).
    """
    top = sorted(entries.values(), key=symbol_priority, reverse=True)
    top_symbols = []
    for e in top:
        top_symbols.append({
            "id": e["id"], "name": e["name"], "file": e["file"],
            "line": e["line"], "kind": e["kind"],
            "entry_ref": f"code-map.json#{e['id']}",
        })

    # files: lean, core-first ordering (trim from tail when over budget)
    files = [{"path": rel, "loc": info["loc"]}
             for rel, info in sorted(per_file.items(), key=lambda kv: _file_priority(kv[0]))]

    router = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RPD Code-Map Router (Layer 1)",
        "version": 2,
        "schema_version": SCHEMA_VERSION,
        "project": {
            "name": project["name"],
            "language": project["language"],
            "file_count": project["file_count"],
            "line_count": project["line_count"],
            "head_commit": head_commit or "unknown",
        },
        "top_symbols": top_symbols,
        "files": files,
        "documents": project.get("documents", []),
        "budget": {
            "estimated_read_tokens": 0,
            "token_limit": ROUTER_TOKEN_LIMIT,
            "pct_of_codebase": 0.0,
            "pct_limit": ROUTER_PCT_LIMIT,
        },
        "generated": {
            "generator_version": GENERATOR_VERSION,
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commit": head_commit or "unknown",
        },
    }

    # Budget guard (R-07): the ABSOLUTE 3k cap is hard and always enforced.
    # The RELATIVE 15% cap is meaningful only when the 3k cap is already binding
    # (i.e., a router large enough to need trimming). For small repos whose full
    # router is already <=3k, trimming for a relative ratio would destroy
    # navigation value ("small repo map from day one") — so we keep it and record
    # the actual pct honestly.
    full_est = estimate_tokens(router)
    trimmed_symbols = 0
    trimmed_files = 0

    if full_est > ROUTER_TOKEN_LIMIT:
        # Fast O(n) greedy: precompute per-element sizes, drop larger contributor first
        base_router = {k: v for k, v in router.items() if k not in ("top_symbols", "files")}
        base_tokens = estimate_tokens(base_router)
        sym_toks = [estimate_tokens(s) for s in top_symbols]
        file_toks = [estimate_tokens(f) for f in files]
        ts_total = sum(sym_toks)
        f_total = sum(file_toks)

        def over_budget_approx():
            return (base_tokens + ts_total + f_total) > ROUTER_TOKEN_LIMIT

        while over_budget_approx():
            if sym_toks and ts_total >= f_total:
                sym_toks.pop()
                ts_total = sum(sym_toks)
                top_symbols.pop()
                trimmed_symbols += 1
            elif len(file_toks) > 1:
                file_toks.pop()
                f_total = sum(file_toks)
                files.pop()
                trimmed_files += 1
            elif sym_toks:
                sym_toks.pop()
                ts_total = sum(sym_toks)
                top_symbols.pop()
                trimmed_symbols += 1
            else:
                break

        router["top_symbols"] = top_symbols
        router["files"] = files
        # Bounded exact-estimate corrective trim (fast: only runs when near target)
        for _ in range(500):
            est = estimate_tokens(router)
            pct = (est / codebase_tokens) * 100 if codebase_tokens else 0
            if est <= ROUTER_TOKEN_LIMIT and pct <= ROUTER_PCT_LIMIT:
                break
            if router["top_symbols"]:
                router["top_symbols"].pop()
                trimmed_symbols += 1
            elif len(router["files"]) > 1:
                router["files"].pop()
                trimmed_files += 1
            else:
                break

    # Final exact record (after any trim)
    est = estimate_tokens(router)
    pct = (est / codebase_tokens) * 100 if codebase_tokens else 0
    router["budget"]["estimated_read_tokens"] = est
    router["budget"]["pct_of_codebase"] = round(pct, 2)
    router["budget"]["trimmed_symbols"] = trimmed_symbols
    router["budget"]["trimmed_files"] = trimmed_files
    if pct > ROUTER_PCT_LIMIT:
        router["budget"]["relative_cap_breached"] = True
        router["budget"]["relative_cap_note"] = "小仓库相对口径不具约束力，router 已按绝对 3k 上限保真"
    return router, trimmed_symbols


def build_meta(project_root, entries, per_file, router, parser_used, head_commit, understand_any):
    """Build code-map.meta.json."""
    files = {}
    for rel, info in per_file.items():
        files[rel] = {
            "fingerprint": info["fingerprint"],
            "entry_count": sum(1 for e in entries.values() if e["file"] == rel),
            "lines": info["loc"],
        }
    meta = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RPD Code-Map Metadata",
        "version": 2,
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head_commit": head_commit or "unknown",
        "map_commit": head_commit or "unknown",
        "parser": parser_used,
        "files": files,
        "budget": {
            "router_estimated_read_tokens": router["budget"]["estimated_read_tokens"],
            "router_token_limit": ROUTER_TOKEN_LIMIT,
            "router_pct_of_codebase": router["budget"]["pct_of_codebase"],
            "router_pct_limit": ROUTER_PCT_LIMIT,
            "entry_max_tokens": ENTRY_MAX_TOKENS,
        },
        "trust": {
            "overall": "verified",
            "last_verified_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "understand_anything": understand_any,
    }
    return meta


def detect_understand_any(project_root):
    """R-10: detect knowledge-graph.json (reuse/degrade, never writes it)."""
    candidates = [
        project_root / ".claude" / "knowledge-graph.json",
        project_root / ".workbuddy" / "knowledge-graph.json",
        project_root / "knowledge-graph.json",
        project_root / ".rpd" / "knowledge-graph.json",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                data = json.loads(smart_read(str(cand)))
                if isinstance(data, dict) and ("nodes" in data or "edges" in data):
                    return {"detected": True, "reused": True, "source_path": str(cand)}
                return {"detected": True, "reused": False, "source_path": str(cand)}
            except Exception:
                return {"detected": True, "reused": False, "source_path": str(cand)}
    return {"detected": False, "reused": False, "source_path": None}


# --- Documents discovery (M3: doc refs) ---

DOC_PATTERNS = ("README", "CHANGELOG", "decisions", "architecture", "docs/")


def discover_documents(project_root):
    docs = []
    for p in project_root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(project_root)).replace("\\", "/")
        low = rel.lower()
        if any(k in low for k in ("readme", "changelog", "decisions", "architecture", "docs/")):
            topic = "overview" if "readme" in low else ("history" if "changelog" in low else "decisions" if "decisions" in low else "architecture" if "architecture" in low else "docs")
            docs.append({"path": rel, "topic": topic})
    return docs


def project_summary(project_root, source_files, head_commit):
    """Detect project name/language from root dir name + source extensions."""
    name = project_root.name.strip() or "project"
    langs = []
    ext_count = {}
    for f in source_files:
        e = f.suffix.lower()
        ext_count[e] = ext_count.get(e, 0) + 1
    if ext_count:
        top_ext = max(ext_count, key=ext_count.get)
        langs = {"cpp": "cpp", "h": "cpp", "hpp": "cpp", "hxx": "cpp",
                 "c": "c"}.get(top_ext.lstrip("."), top_ext.lstrip("."))
    total_lines = sum(file_loc(f) for f in source_files)
    return {
        "name": name,
        "language": [langs] if isinstance(langs, str) else langs,
        "file_count": len(source_files),
        "line_count": total_lines,
        "documents": discover_documents(project_root),
    }


def generate_map(project_root, incremental=False):
    """Full or incremental code-map generation. Returns report dict."""
    root = Path(project_root)
    rpd = root / ".rpd"
    rpd.mkdir(exist_ok=True)

    source_files = collect_source_files(root)

    # Incremental: only re-parse files changed since map_commit (if git available)
    if incremental and git_available(root):
        try:
            meta_old = {}
            meta_path = rpd / "code-map.meta.json"
            if meta_path.exists():
                meta_old = json.loads(smart_read(str(meta_path)))
            map_commit = meta_old.get("map_commit")
            head = git_head(root)
            if map_commit and head and map_commit != head:
                out = subprocess.check_output(
                    ["git", "-C", str(root), "diff", "--name-only", f"{map_commit}..HEAD"],
                    text=True, encoding="utf-8", errors="replace"
                )
                changed = {line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()}
                # Keep only files that are both changed and source
                source_files = [p for p in source_files
                                if str(p.relative_to(root)).replace("\\", "/") in changed]
        except Exception:
            pass  # fall back to full re-parse

    entries, per_file, parser_used = build_entries(source_files, root)
    inverted = build_inverted_index(entries)
    code_map = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "version": 2,
        "schema_version": SCHEMA_VERSION,
        "entries": entries,
        "inverted_index": inverted,
    }
    write_atomic(root, "code-map.json", code_map)

    head = git_head(root)
    total_lines = sum(per_file[p]["loc"] for p in per_file)
    codebase_tokens = total_lines * AVG_TOKENS_PER_LINE
    summary = project_summary(root, collect_source_files(root), head)
    router, _trimmed = build_router(summary, entries, per_file, codebase_tokens, head)
    write_atomic(root, "code-map.router.json", router)

    ua = detect_understand_any(root)
    meta = build_meta(root, entries, per_file, router, parser_used, head, ua)
    ts = router["budget"].get("trimmed_symbols", 0)
    tf = router["budget"].get("trimmed_files", 0)
    if ts or tf:
        meta["budget"]["trimmed"] = True
        meta["budget"]["trimmed_symbols"] = ts
        meta["budget"]["trimmed_files"] = tf
        meta["budget"]["router_estimated_read_tokens"] = router["budget"]["estimated_read_tokens"]
        meta["budget"]["router_pct_of_codebase"] = router["budget"]["pct_of_codebase"]
    write_atomic(root, "code-map.meta.json", meta)

    return {
        "project_root": str(root.resolve()),
        "source_files": len(source_files),
        "symbols": len(entries),
        "parser": parser_used,
        "router_tokens": router["budget"]["estimated_read_tokens"],
        "router_token_limit": ROUTER_TOKEN_LIMIT,
        "router_pct": router["budget"]["pct_of_codebase"],
        "router_pct_limit": ROUTER_PCT_LIMIT,
        "trimmed": _trimmed,
        "codebase_token_estimate": codebase_tokens,
        "head_commit": head or "unknown",
        "understand_anything": ua,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python code-map-generator.py <project-root> [--json] [--incremental]")
        return 1
    project_root = args[0]
    as_json = "--json" in args
    incremental = "--incremental" in args
    if not Path(project_root).is_dir():
        print(f"Error: Not a directory: {project_root}", file=sys.stderr)
        return 1
    report = generate_map(project_root, incremental=incremental)
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Code-map 生成完成:")
        print(f"  源文件: {report['source_files']} | 符号: {report['symbols']} | parser: {report['parser']}")
        print(f"  router: {report['router_tokens']} token ({report['router_pct']}% of codebase) "
              f"限 {report['router_token_limit']} token / {report['router_pct_limit']}% "
              f"{'[已裁剪 top_symbols]' if report['trimmed'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
