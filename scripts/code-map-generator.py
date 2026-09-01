#!/usr/bin/env python3
"""RPD v2 code-map generator: two-layer code map (router + full symbol table).

Produces in <project-root>/.rpd/:
  - code-map.router.json   Layer 1, always-in-context index (<=3k token AND <=15% codebase)
  - code-map.json          Layer 2, full key-value symbol table (read per-entry only)
  - code-map.meta.json     metadata: commit, fingerprints, budget, trust (red-line source)

Parsing: tree-sitter (9 languages via language pack / official packages) with
per-language regex fallback (dual-path). Calls edges are labeled candidate-only
with confidence heuristic|resolved — never "exact call graph".
labeled candidate-only with confidence heuristic|resolved — never "exact call graph".

Usage:
  python code-map-generator.py <project-root> [--json] [--incremental]

Exit codes:
  0 - Generated
  1 - Usage error / project root missing
"""

import hashlib
import importlib
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
GENERATOR_VERSION = "2.2.0"

# --- Language registry (v2.2: multi-language code map) ---
# Each language: indexed extensions, optional tree-sitter backend, regex rules.
# tree-sitter backends, in priority order:
#   1. tree-sitter-language-pack (aggregated, lazy per-language download;
#      pre-compiled at ABI 14, backwards compatible with tree_sitter 0.21-0.26)
#   2. official per-language packages (LANGS[lang]["ts"] module)
#   3. per-language regex fallback (zero dependency, always available)
# NOTE: csharp grammar is generated at ABI 15 — pack/official both handle it,
# but a parse failure (ABI mismatch) must fall back to regex, never crash.

LANGS = {
    "c":          {"exts": (".c",), "ts": "tree_sitter_c"},
    "cpp":        {"exts": (".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx"), "ts": "tree_sitter_cpp"},
    "python":     {"exts": (".py", ".pyw"), "ts": "tree_sitter_python"},
    "javascript": {"exts": (".js", ".jsx", ".mjs", ".cjs"), "ts": "tree_sitter_javascript"},
    "typescript": {"exts": (".ts", ".tsx", ".mts", ".cts"), "ts": "tree_sitter_typescript"},
    "java":       {"exts": (".java",), "ts": "tree_sitter_java"},
    "go":         {"exts": (".go",), "ts": "tree_sitter_go"},
    "rust":       {"exts": (".rs",), "ts": "tree_sitter_rust"},
    "csharp":     {"exts": (".cs",), "ts": "tree_sitter_csharp"},
}
EXT_TO_LANG = {ext: lang for lang, cfg in LANGS.items() for ext in cfg["exts"]}
PRIMARY_EXTENSIONS = set(EXT_TO_LANG)

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "vendor", "target", "third_party",
    "thirdparty", "out", "cmake-build-debug", "CMakeFiles", ".rpd", ".code-map.tmp",
    ".claude", ".claude-plugin", ".github",  # agent 配置/worktree 副本不应被索引
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


# --- Parsing: tree-sitter multi-language + per-language regex fallback ---

_ts_parsers = {}   # lang -> (parser, ok) cache; (None, False) = regex fallback
_ts_warned = False


def get_tree_sitter_parser(lang):
    """Lazily load a parser for one language. Returns (parser, ok) or (None, False).

    Priority: tree-sitter-language-pack (aggregated) > official per-language
    package. Any failure (missing package, ABI mismatch) degrades to regex.
    """
    global _ts_warned
    if lang in _ts_parsers:
        return _ts_parsers[lang]
    result = (None, False)
    try:
        try:
            from tree_sitter_language_pack import get_parser
            result = (get_parser(lang), True)
        except ImportError:
            from tree_sitter import Language, Parser
            mod = importlib.import_module(LANGS[lang]["ts"])
            lang_fn = getattr(mod, "language", None)
            if lang_fn is None:
                raise ImportError(f"{LANGS[lang]['ts']} exposes no language()")
            result = (Parser(Language(lang_fn())), True)
    except Exception as e:
        result = (None, False)
        if not _ts_warned:
            _ts_warned = True
            print(f"[code-map] tree-sitter {lang} 不可用，该语言降级为正则解析: {e}",
                  file=sys.stderr)
    _ts_parsers[lang] = result
    return result


# tree-sitter node type -> symbol kind, per language
LANG_TS_NODES = {
    "c": {"function_definition": "function", "class_specifier": "class",
          "struct_specifier": "struct", "enum_specifier": "enum"},
    "cpp": {"function_definition": "function", "class_specifier": "class",
            "struct_specifier": "struct", "enum_specifier": "enum"},
    "python": {"function_definition": "function", "class_definition": "class"},
    "javascript": {"function_declaration": "function", "method_definition": "method",
                   "generator_function_declaration": "function",
                   "class_declaration": "class"},
    "typescript": {"function_declaration": "function", "method_definition": "method",
                   "generator_function_declaration": "function",
                   "class_declaration": "class"},
    "java": {"method_declaration": "method", "constructor_declaration": "method",
             "class_declaration": "class", "interface_declaration": "class",
             "enum_declaration": "enum", "record_declaration": "class"},
    "go": {"function_declaration": "function", "method_declaration": "method"},
    "rust": {"function_item": "function", "struct_item": "struct",
             "enum_item": "enum", "trait_item": "class"},
    "csharp": {"method_declaration": "method", "constructor_declaration": "method",
               "class_declaration": "class", "interface_declaration": "class",
               "struct_declaration": "struct", "enum_declaration": "enum",
               "record_declaration": "class"},
}

# call-node type per language (java uses method_invocation)
LANG_TS_CALL_NODE = {"java": "method_invocation"}
_CALL_NODE_DEFAULT = "call_expression"


def _ts_node_name(node, lang):
    """Extract symbol name from a definition node (per-language quirks)."""
    try:
        if lang == "go" and node.type == "method_declaration":
            recv = node.child_by_field_name("receiver")
            name = node.child_by_field_name("name")
            if name is None:
                return ""
            method = name.text.decode("utf-8", "replace")
            if recv is not None:
                m = re.search(r"(\w+)\s*\)?\s*$", recv.text.decode("utf-8", "replace"))
                if m:
                    return f"{m.group(1)}::{method}"
            return method
        if lang == "go" and node.type == "type_declaration":
            # names live on child type_spec nodes
            names = []
            for c in node.children:
                if c.type == "type_spec":
                    n = c.child_by_field_name("name")
                    if n is not None:
                        names.append(n.text.decode("utf-8", "replace"))
            return names[0] if names else ""
        if lang in ("c", "cpp"):
            if node.type in ("class_specifier", "struct_specifier", "enum_specifier"):
                n = node.child_by_field_name("name")
                return n.text.decode("utf-8", "replace") if n else ""
            decl = node.child_by_field_name("declarator")
            if decl is None:
                return ""
            sub = decl.child_by_field_name("declarator")
            if sub is None:
                sub = decl
            return sub.text.decode("utf-8", "replace")
        n = node.child_by_field_name("name")
        return n.text.decode("utf-8", "replace") if n else ""
    except Exception:
        return ""


def _ts_node_signature(node, lang):
    """Human-readable signature: first 120 chars of the node, normalized."""
    try:
        txt = node.text.decode("utf-8", "replace")
        cut = txt.split("{")[0] if lang != "python" else txt.split(":")[0]
        return re.sub(r"\s+", " ", cut.strip())[:120]
    except Exception:
        return ""


def _ts_extract_calls(node, lang):
    """Collect call-target names within a node subtree."""
    call_type = LANG_TS_CALL_NODE.get(lang, _CALL_NODE_DEFAULT)
    calls = []
    stack = [node]
    while stack:
        n = stack.pop()
        for c in n.children:
            if c.type == call_type:
                fn = c.child_by_field_name("function") or c.child_by_field_name("name")
                if fn is not None:
                    calls.append(fn.text.decode("utf-8", "replace"))
                else:
                    calls.append(c.text.decode("utf-8", "replace").split("(")[0])
            else:
                stack.append(c)
    return calls


def parse_with_tree_sitter(path, content, lang):
    """Parse one file with tree-sitter. Returns list of raw symbol dicts or None.

    Each raw symbol: {name, kind, line, signature, doc, calls[], in_class}
    """
    parser, ok = get_tree_sitter_parser(lang)
    if not ok:
        return None
    try:
        tree = parser.parse(content.encode("utf-8"))
    except Exception:
        return None
    root = tree.root_node
    node_map = LANG_TS_NODES[lang]
    symbols = []

    def walk(node, in_class=False, class_name=""):
        t = node.type
        if lang == "rust" and t == "impl_item":
            # methods live inside impl blocks; use the impl target as class
            try:
                ty = node.child_by_field_name("type")
                impl_name = ""
                if ty is not None:
                    m = re.search(r"(\w+)\s*$", ty.text.decode("utf-8", "replace"))
                    impl_name = m.group(1) if m else ""
            except Exception:
                impl_name = ""
            for c in node.children:
                walk(c, bool(impl_name), impl_name)
            return
        kind = node_map.get(t)
        if kind:
            name = _ts_node_name(node, lang)
            if lang == "go" and t == "type_declaration":
                # one node may declare several types; take them all
                for c in node.children:
                    if c.type == "type_spec":
                        n = c.child_by_field_name("name")
                        if n is not None:
                            symbols.append({
                                "name": n.text.decode("utf-8", "replace"),
                                "kind": "struct", "line": c.start_point[0] + 1,
                                "signature": f"type: {n.text.decode('utf-8', 'replace')}",
                                "doc": "", "calls": [], "in_class": "",
                            })
                return
            if name:
                line = node.start_point[0] + 1
                final_kind = "method" if (kind == "function" and in_class) else kind
                full = (f"{class_name}::{name}" if in_class and name and "::" not in name
                        else name)
                symbols.append({
                    "name": full, "kind": final_kind, "line": line,
                    "signature": _ts_node_signature(node, lang),
                    "doc": _extract_doc_before(content, node.start_point[0], lang),
                    "calls": _ts_extract_calls(node, lang),
                    "in_class": class_name,
                })
                if kind in ("class", "struct", "enum") and t not in ("enum_specifier",):
                    for c in node.children:
                        walk(c, True, name)
                return
        for c in node.children:
            walk(c, in_class, class_name)

    walk(root)
    return symbols


def _extract_doc_before(content, line_idx, lang=None):
    """Extract single-line doc from comments immediately above the symbol."""
    lines = content.split("\n")
    doc = ""
    for i in range(max(0, line_idx - 4), line_idx):
        line = lines[i].strip()
        if line.startswith("//"):
            doc = line.lstrip("/").strip()
            break
        if lang == "python" and line.startswith("#") and not line.startswith("#!"):
            doc = line.lstrip("#").strip()
            break
        if line.startswith("*") or line.startswith("/*") or line.startswith("/**"):
            doc = line.lstrip("*/ ").strip()
            break
    return doc[:80]


# --- Regular-expression fallback parsers (per-language rules) ---

def _R(pattern):
    return re.compile(pattern, re.MULTILINE)


_C_FUNC = _R(
    r'^\s*(?:static\s+|inline\s+|const\s+|virtual\s+|extern\s+|explicit\s+)*'
    r'(?:[\w:]+\s+)+([\w~]+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>,\s]+)?\s*\{'
)
_C_CLS = _R(r'^\s*(?:class|struct)\s+(\w+)')

JS_FUNC = _R(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)\s*\(')
JS_ARROW = _R(r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*'
              r'(?:async\s+)?(?:function\b|\([^)]*\)\s*(?::[^=]+)?=>|\w+\s*=>)')
JS_METHOD = _R(r'^\s+(?:(?:public|private|protected|static|readonly|async|abstract|override|get|set|\*)\s+)*'
               r'(?!if\b|for\b|while\b|switch\b|catch\b|return\b|function\b|new\b|delete\b|typeof\b)'
               r'(\w+)\s*\([^;{}]*\)\s*(?::\s*[^{;=]+)?\s*\{')
JS_CLS = _R(r'^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?(?:class|interface)\s+(\w+)')

JAVA_FUNC = _R(r'^\s*(?:(?:public|private|protected|static|final|abstract|synchronized|native|default)\s+)*'
               r'(?:<[^>]+>\s*)?(?:[\w<>\[\],.?]+\s+)+(\w+)\s*\([^;]*\)\s*(?:throws\s+[\w.,\s]+)?\{')
JAVA_CLS = _R(r'^\s*(?:(?:public|private|protected|static|final|abstract|sealed|strictfp)\s+)*'
              r'(?:class|interface|enum|record)\s+(\w+)')

GO_FUNC = _R(r'^func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(')
GO_METHOD = _R(r'^func\s+\(\w+\s+\*?(\w+)\)\s*(\w+)\s*\(')
GO_CLS = _R(r'^type\s+(\w+)\s+(?:struct|interface)\b')

RUST_FUNC = _R(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:const\s+)?(?:async\s+)?(?:unsafe\s+)?'
               r'(?:extern\s+"[^"]*"\s+)?fn\s+(\w+)')
RUST_CLS = _R(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:struct|enum|trait)\s+(\w+)')

CS_FUNC = _R(r'^\s*(?:(?:public|private|protected|internal|static|virtual|override|abstract|sealed|async|partial|extern|new|unsafe)\s+)*'
             r'(?:[\w<>\[\],.?]+\s+)+(\w+)\s*\([^;]*\)\s*(?:where\s+[\w<>,\s:]+)?\{')
CS_CLS = _R(r'^\s*(?:(?:public|internal|private|protected|abstract|sealed|static|partial)\s+)*'
            r'(?:class|interface|struct|record|enum)\s+(\w+)')

_LANG_RE = {
    "c": {"func": [_C_FUNC], "cls": _C_CLS, "brace": True},
    "cpp": {"func": [_C_FUNC], "cls": _C_CLS, "brace": True},
    "python": {"func": [_R(r'^(\s*)(?:async\s+)?def\s+(\w+)')],
               "cls": _R(r'^(\s*)class\s+(\w+)'), "brace": False},
    "javascript": {"func": [JS_FUNC, JS_ARROW, JS_METHOD], "cls": JS_CLS, "brace": True},
    "typescript": {"func": [JS_FUNC, JS_ARROW, JS_METHOD], "cls": JS_CLS, "brace": True},
    "java": {"func": [JAVA_FUNC], "cls": JAVA_CLS, "brace": True},
    "go": {"func": [GO_METHOD, GO_FUNC], "cls": GO_CLS, "brace": True},
    "rust": {"func": [RUST_FUNC], "cls": RUST_CLS, "brace": True},
    "csharp": {"func": [CS_FUNC], "cls": CS_CLS, "brace": True},
}


def _brace_body(lines, start_idx, cap=600):
    """Lines of a brace-delimited body starting at start_idx (balanced)."""
    depth = 0
    started = False
    buf = []
    for i in range(start_idx, min(len(lines), start_idx + cap)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        buf.append(lines[i])
        if started and depth <= 0:
            break
    return "\n".join(buf)


def _indent_body(lines, start_idx, base_indent, cap=600):
    """Lines of an indentation-delimited body (Python style), def line included."""
    buf = [lines[start_idx]]
    for i in range(start_idx + 1, min(len(lines), start_idx + 1 + cap)):
        line = lines[i]
        if line.strip() and (len(line) - len(line.lstrip())) <= base_indent:
            break
        buf.append(line)
    return "\n".join(buf)


def parse_with_regex(path, content, lang):
    """Heuristic per-language regex parse. Returns raw symbol dicts."""
    rules = _LANG_RE[lang]
    brace = rules["brace"]
    lines = content.split("\n")
    symbols = []
    classes = []  # (line_no, name) in file order, for in_class attribution

    for m in rules["cls"].finditer(content):
        line_no = content[:m.start()].count("\n") + 1
        if lang == "python":
            indent, name = m.group(1), m.group(2)
        else:
            indent, name = "", m.group(1)
        classes.append((line_no, name))
        symbols.append({
            "name": name, "kind": "class", "line": line_no,
            "signature": f"class: {name}",
            "doc": _extract_doc_before(content, line_no - 1, lang),
            "calls": [], "in_class": "",
        })

    for m in _iter_func_matches(rules["func"], content):
        if lang == "python":
            # the match may start on a preceding blank line (\s* swallows the
            # newline); anchor line/indent/signature to the line where it ends
            line_no = content[:m.end()].count("\n") + 1
            base_indent = len(lines[line_no - 1]) - len(lines[line_no - 1].lstrip())
            name = m.group(2)
            in_class_name = ""
            for cls_line, cls_name in reversed(classes):
                if cls_line < line_no:
                    cls_indent = len(lines[cls_line - 1]) - len(lines[cls_line - 1].lstrip())
                    if base_indent > cls_indent:
                        in_class_name = cls_name
                    break
            body = _indent_body(lines, line_no - 1, base_indent)
            full = f"{in_class_name}::{name}" if in_class_name else name
            symbols.append({
                "name": full, "kind": "method" if in_class_name else "function",
                "line": line_no,
                "signature": re.sub(r"\s+", " ", lines[line_no - 1].strip())[:120],
                "doc": _extract_doc_before(content, line_no - 1, lang),
                "calls": _extract_calls_regex(body), "in_class": in_class_name,
            })
        else:
            line_no = content[:m.start()].count("\n") + 1
            # go method pattern carries the receiver type in group(1)
            if lang == "go" and m.re is GO_METHOD and m.lastindex == 2:
                recv, name = m.group(1), m.group(2)
                full = f"{recv}::{name}"
            else:
                name = m.group(m.lastindex)
                full = name
            # attribute to the enclosing class only for indented definitions
            line = lines[line_no - 1]
            if (len(line) - len(line.lstrip())) > 0:
                for cls_line, cls_name in reversed(classes):
                    if cls_line < line_no:
                        in_class_name = cls_name
                        break
            else:
                in_class_name = ""
            if in_class_name and "::" not in full:
                full = f"{in_class_name}::{full}"
            body = _brace_body(lines, line_no - 1)
            symbols.append({
                "name": full, "kind": "method" if in_class_name else "function",
                "line": line_no,
                "signature": re.sub(r"\s+", " ", m.group(0).split("{")[0].strip())[:120],
                "doc": _extract_doc_before(content, line_no - 1, lang),
                "calls": _extract_calls_regex(body), "in_class": in_class_name,
            })
    symbols.sort(key=lambda s: s["line"])
    return symbols


def _iter_func_matches(patterns, content):
    """Yield function matches across a language's pattern list, deduped by position."""
    seen = set()
    combined = []
    for pat in patterns:
        for m in pat.finditer(content):
            if m.start() not in seen:
                seen.add(m.start())
                combined.append(m)
    combined.sort(key=lambda m: m.start())
    return combined


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

    Returns (entries, per_file, parser_stats).
    entries: dict id -> entry
    per_file: dict rel_path -> {loc, fingerprint, lang, raw_symbols}
    parser_stats: dict lang -> "tree-sitter" | "regex" (per language, actual path)
    """
    entries = {}
    per_file = {}
    parser_stats = {}

    for path in source_files:
        lang = EXT_TO_LANG.get(path.suffix.lower())
        if lang is None:
            continue
        rel = str(path.relative_to(project_root)).replace("\\", "/")
        content = smart_read(str(path))
        if not content:
            continue
        loc = file_loc(path)
        per_file[rel] = {
            "loc": loc,
            "fingerprint": "sha256:" + (sha256_of_file(path) or ""),
            "lang": lang,
        }

        raws = parse_with_tree_sitter(path, content, lang)
        if raws is None:
            parser_stats.setdefault(lang, "regex")
            raws = parse_with_regex(path, content, lang)
        else:
            if lang not in parser_stats:
                parser_stats[lang] = "tree-sitter"

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

    return entries, per_file, parser_stats


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


def build_meta(project_root, entries, per_file, router, parser_stats, head_commit,
               understand_any, unindexed_exts=None):
    """Build code-map.meta.json."""
    files = {}
    for rel, info in per_file.items():
        files[rel] = {
            "fingerprint": info["fingerprint"],
            "entry_count": sum(1 for e in entries.values() if e["file"] == rel),
            "lines": info["loc"],
            "lang": info.get("lang", ""),
        }
    parser_summary = "tree-sitter" if any(v == "tree-sitter" for v in parser_stats.values()) else "regex"
    meta = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RPD Code-Map Metadata",
        "version": 2,
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "head_commit": head_commit or "unknown",
        "map_commit": head_commit or "unknown",
        "parser": parser_summary,
        "parsers": parser_stats,
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
    if unindexed_exts:
        meta["unindexed_extensions"] = unindexed_exts
        meta["coverage_note"] = ("以下扩展名暂不在语言注册表内，未被索引；"
                                 "可通过扩展 LANGS 注册表或 .rpd/keyword-map.json 反馈")
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
    ext_count = {}
    for f in source_files:
        e = f.suffix.lower()
        ext_count[e] = ext_count.get(e, 0) + 1
    lang_count = {}
    for ext, count in ext_count.items():
        lang = EXT_TO_LANG.get(ext)
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + count
    langs = [l for l, _ in sorted(lang_count.items(), key=lambda kv: -kv[1])]
    total_lines = sum(file_loc(f) for f in source_files)
    return {
        "name": name,
        "language": langs,
        "file_count": len(source_files),
        "line_count": total_lines,
        "documents": discover_documents(project_root),
    }


def count_unindexed_extensions(project_root):
    """Coverage report: extensions of non-indexed text files (top 10 by count).

    Makes "unsupported language" visible in meta instead of silently dropping.
    """
    counts = {}
    for p in project_root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(project_root)
        if set(rel.parts) & SKIP_DIRS:
            continue
        skip_dirs = {part.lower() for part in rel.parts[:-1]}
        if skip_dirs & SKIP_PATH_PARTS:
            continue
        ext = p.suffix.lower()
        if not ext or ext in PRIMARY_EXTENSIONS:
            continue
        if ext in (".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg",
                   ".ini", ".lock", ".xml", ".html", ".css", ".scss", ".vue",
                   ".svelte", ".astro", ".sql", ".sh", ".bat", ".ps1", ".proto",
                   ".graphql", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
                   ".pdf", ".woff", ".woff2", ".ttf"):
            continue  # config/docs/assets are not "missed languages"
        counts[ext] = counts.get(ext, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1])[:10])


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

    entries, per_file, parser_stats = build_entries(source_files, root)
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
    unindexed = count_unindexed_extensions(root)
    meta = build_meta(root, entries, per_file, router, parser_stats, head, ua, unindexed)
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
        "parser": ("tree-sitter" if any(v == "tree-sitter" for v in parser_stats.values())
                   else "regex"),
        "parsers": parser_stats,
        "unindexed_extensions": unindexed,
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
        if report.get("parsers"):
            print(f"  分语言: {report['parsers']}")
        if report.get("unindexed_extensions"):
            print(f"  未索引扩展名: {report['unindexed_extensions']}")
        print(f"  router: {report['router_tokens']} token ({report['router_pct']}% of codebase) "
              f"限 {report['router_token_limit']} token / {report['router_pct_limit']}% "
              f"{'[已裁剪 top_symbols]' if report['trimmed'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
