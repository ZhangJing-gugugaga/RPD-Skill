#!/usr/bin/env python3
"""RPD v2 code-map semantic enrichment (hybrid parsing: structure + LLM semantics).

Workflow (deterministic script, zero LLM calls of its own):
  1. `generate` (default)  : read code-map.json + meta, emit .rpd/enrich-prompt.md
                             — the host Agent fills it in (module purpose, arch
                             layer, insights) and saves JSON, then calls --apply.
  2. `--apply <file.json>` : validate the Agent's answer and persist
                             .rpd/code-map.semantic.json with anti-staleness
                             bindings (per-module fingerprint hash, model, time).
  3. `--validate`          : re-check bindings against current code-map.meta.json
                             fingerprints; drop stale/dangling entries; report.

Anti-staleness rules (community consensus, understand-anything-aligned):
  - structure layer is the single source of truth; semantics is a pure cache
  - every entry binds to the sha256 of its module's file fingerprints
  - fingerprint mismatch or missing module => entry invalid, never served
  - semantics never enters the router budget; it is a lazy-read layer only

Usage:
  python code-map-enrich.py <project-root> [--apply <answers.json>] [--validate] [--json]

Exit codes:
  0 - success (validate: all entries valid, or empty)
  1 - usage error
  2 - apply/validate found stale or dangling entries (cleaned file rewritten)
"""

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SEMANTIC_FILE = "code-map.semantic.json"
SEMANTIC_SCHEMA_VERSION = "1.0.0"
SEMANTIC_TOKEN_BUDGET = 2000   # lazy-read layer budget (NOT part of router 3k)
ALLOWED_LAYERS = ["api", "service", "data", "ui", "core", "tooling", "unknown"]
MAX_INSIGHTS_PER_MODULE = 3
MAX_PURPOSE_LEN = 80


def estimate_tokens(obj):
    try:
        return max(1, len(json.dumps(obj, ensure_ascii=False, separators=(",", ":"))) // 4)
    except Exception:
        return 0


def smart_read(file_path):
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp1252", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_json(path):
    try:
        return json.loads(smart_read(str(path)))
    except Exception:
        return None


def module_of(rel_path):
    """Module key: first directory segment, or '<root>' for top-level files."""
    parts = rel_path.split("/")
    return parts[0] if len(parts) > 1 else "<root>"


def aggregate_fingerprint(meta):
    """Per-module sha256 over that module's per-file fingerprints (order-stable)."""
    per_module = {}
    for rel, info in sorted(meta.get("files", {}).items()):
        mod = module_of(rel)
        per_module.setdefault(mod, []).append(info.get("fingerprint", ""))
    return {mod: hashlib.sha256("\n".join(fps).encode("utf-8")).hexdigest()
            for mod, fps in per_module.items()}


def generate_prompt(project_root, code_map, meta):
    """Emit .rpd/enrich-prompt.md for the host Agent to fill in."""
    entries = code_map.get("entries", {})
    modules = {}
    for e in entries.values():
        mod = module_of(e.get("file", ""))
        info = modules.setdefault(mod, {"files": set(), "symbols": []})
        info["files"].add(e.get("file", ""))
        if len(info["symbols"]) < 8:
            info["symbols"].append(f'{e.get("kind")}:{e.get("name")}')
    if not modules:
        print("[enrich] code-map 为空，无可富化内容", file=sys.stderr)
        return None

    lines = [
        "# Code-Map 语义富化（由宿主 Agent 填写）",
        "",
        "以下模块清单来自确定性 code-map 结构层。请为每个模块填写：",
        "- `purpose`: 一句话职责（≤40 字）",
        "- `layer`: 架构分层，只能是 " + "/".join(ALLOWED_LAYERS),
        f"- `insights`: 最多 {MAX_INSIGHTS_PER_MODULE} 条代码读不出来的关键理解"
        "（设计意图/坑/约束，不要复抄代码可推导内容）",
        "",
        "填写完成后保存为 JSON 并执行：",
        "`python scripts/code-map-enrich.py <project-root> --apply <answers.json>`",
        "",
        "```json",
        "{",
        '  "model": "<你的模型名>",',
        '  "modules": [',
    ]
    for mod in sorted(modules):
        info = modules[mod]
        lines.append("    {")
        lines.append(f'      "module": "{mod}",')
        lines.append(f'      "files": {json.dumps(sorted(info["files"]))},')
        lines.append('      "purpose": "",')
        lines.append(f'      "layer": "unknown",  // one of {ALLOWED_LAYERS}')
        lines.append('      "insights": []')
        lines.append("    },")
    lines.append("  ]")
    lines.append("}")
    lines.append("```")

    out = Path(project_root) / ".rpd" / "enrich-prompt.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def apply_answers(project_root, answers, meta):
    """Validate Agent answers and persist semantic cache with bindings."""
    fp_map = aggregate_fingerprint(meta)
    known_modules = set(fp_map)
    errors, valid = [], []
    model = str(answers.get("model", "unknown"))[:60]
    for m in answers.get("modules", []):
        mod = str(m.get("module", ""))
        if mod not in known_modules:
            errors.append(f"未知模块: {mod}（不在当前 code-map）")
            continue
        purpose = str(m.get("purpose", "")).strip()[:MAX_PURPOSE_LEN]
        layer = str(m.get("layer", "unknown"))
        if layer not in ALLOWED_LAYERS:
            errors.append(f"{mod}: 非法 layer '{layer}'")
            continue
        insights = [str(i).strip()[:120] for i in m.get("insights", [])[:MAX_INSIGHTS_PER_MODULE]
                    if str(i).strip()]
        if not purpose:
            errors.append(f"{mod}: purpose 为空")
            continue
        valid.append({
            "module": mod,
            "purpose": purpose,
            "layer": layer,
            "insights": insights,
            "bound_fingerprint": fp_map[mod],
            "model": model,
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    semantic = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RPD Code-Map Semantic Layer (derived cache)",
        "schema_version": SEMANTIC_SCHEMA_VERSION,
        "note": "纯派生缓存：结构层是唯一事实源；bound_fingerprint 失配即失效",
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modules": valid,
    }
    out = Path(project_root) / ".rpd" / SEMANTIC_FILE
    out.parent.mkdir(exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(semantic, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, out)
    return valid, errors, out


def validate(project_root, meta):
    """Drop stale (fingerprint mismatch) and dangling (module gone) entries."""
    path = Path(project_root) / ".rpd" / SEMANTIC_FILE
    semantic = load_json(path)
    if semantic is None:
        return {"status": "missing", "kept": 0, "dropped": 0, "dropped_modules": []}
    fp_map = aggregate_fingerprint(meta)
    kept, dropped = [], []
    for m in semantic.get("modules", []):
        mod = m.get("module", "")
        if mod not in fp_map:
            dropped.append({"module": mod, "reason": "dangling"})
        elif m.get("bound_fingerprint") != fp_map[mod]:
            dropped.append({"module": mod, "reason": "stale"})
        else:
            kept.append(m)
    semantic["modules"] = kept
    semantic["validated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(semantic, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    return {
        "status": "clean" if not dropped else "cleaned",
        "kept": len(kept),
        "dropped": len(dropped),
        "dropped_modules": dropped,
        "tokens": estimate_tokens(semantic),
        "budget": SEMANTIC_TOKEN_BUDGET,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python code-map-enrich.py <project-root> [--apply <answers.json>] "
              "[--validate] [--json]")
        return 1
    project_root = Path(args[0])
    if not project_root.is_dir():
        print(f"Error: Not a directory: {project_root}", file=sys.stderr)
        return 1
    as_json = "--json" in args
    apply_idx = args.index("--apply") if "--apply" in args else -1
    answers_file = args[apply_idx + 1] if apply_idx >= 0 and apply_idx + 1 < len(args) else None

    rpd = project_root / ".rpd"
    code_map = load_json(rpd / "code-map.json")
    meta = load_json(rpd / "code-map.meta.json")
    if code_map is None or meta is None:
        print("Error: 先运行 code-map-generator.py 生成结构层", file=sys.stderr)
        return 1

    if apply_idx >= 0:
        if not answers_file:
            print("Error: --apply 需要答案 JSON 路径", file=sys.stderr)
            return 1
        answers = load_json(Path(answers_file))
        if answers is None:
            print(f"Error: 无法读取答案文件: {answers_file}", file=sys.stderr)
            return 1
        valid, errors, out = apply_answers(project_root, answers, meta)
        report = {"applied": len(valid), "errors": errors, "output": str(out),
                  "tokens": estimate_tokens({"modules": valid})}
        if as_json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(f"语义层已写入: {out} ({report['applied']} 模块, "
                  f"~{report['tokens']} token)")
            for e in errors:
                print(f"  [跳过] {e}", file=sys.stderr)
        return 0

    if "--validate" in args:
        result = validate(project_root, meta)
        if as_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"语义层校验: {result['status']} | 保留 {result['kept']} | "
                  f"失效剔除 {result['dropped']}")
            for d in result.get("dropped_modules", []):
                print(f"  [剔除] {d['module']} ({d['reason']})")
        return 0 if result["status"] in ("missing", "clean") else 2

    out = generate_prompt(project_root, code_map, meta)
    if out is None:
        return 1
    if as_json:
        print(json.dumps({"prompt_file": str(out)}, indent=2))
    else:
        print(f"富化提示词已生成: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
