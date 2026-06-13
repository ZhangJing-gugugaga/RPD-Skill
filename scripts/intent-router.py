#!/usr/bin/env python3
"""Deterministic intent router using keyword matching.

Receives user input text, classifies intent and maturity level via
regex keyword matching (no LLM calls), and outputs a JSON routing decision.

Usage: python intent-router.py "<user-input-text>"

Exit codes:
  0 - Success (JSON output to stdout)
  1 - Usage error (no arguments or empty input)
"""

import json
import re
import sys

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

# Fix Windows encoding for JSON output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- Intent trigger patterns (priority order: new_project > takeover > continue) ---

WARM_START_TRIGGERS = [
    r"帮我做个", r"我想做个", r"有个想法", r"帮我弄个",
    r"那个.*就是", r"能不能帮我", r"我想搞个",
    r"help me", r"i want to", r"i have an idea", r"i'd like to build",
]

TAKEOVER_TRIGGERS = [
    r"接手", r"分析.*项目", r"做到一半", r"半成品",
    r"帮我理一下", r"看看.*进度",
    r"take over", r"analyze.*project", r"half.?finish",
]

CONTINUE_TRIGGERS = [
    r"继续", r"接着", r"下一步", r"接着做", r"继续开发",
    r"continue", r"what.?s next", r"keep going",
]

# --- Maturity signal patterns ---

VAGUE_SIGNALS = [
    r"可能", r"也许", r"不确定", r"不知道",
    r"就是.*那个", r"随便", r"都行",
    r"maybe", r"not sure", r"i don.?t know",
]

CLEAR_SIGNALS = [
    r"给.*用", r"自己用", r"公司.*用", r"客户.*用",
    r"记账", r"购物", r"社交", r"教育",
    r"for.*users", r"for myself", r"for my company",
]


def _compile_patterns(patterns):
    """Compile a list of regex strings into compiled pattern objects."""
    return [re.compile(p, re.IGNORECASE) for p in patterns]


# Pre-compile all patterns at module load time
_COMPILED_INTENTS = [
    ("new_project", _compile_patterns(WARM_START_TRIGGERS)),
    ("takeover", _compile_patterns(TAKEOVER_TRIGGERS)),
    ("continue", _compile_patterns(CONTINUE_TRIGGERS)),
]
_COMPILED_VAGUE = _compile_patterns(VAGUE_SIGNALS)
_COMPILED_CLEAR = _compile_patterns(CLEAR_SIGNALS)


def classify_intent(text):
    """Classify user intent from input text using first-match-wins priority.

    Priority order: new_project > takeover > continue > unknown.

    Args:
        text: User input string.

    Returns:
        Tuple of (intent_string, list_of_matched_trigger_strings).
    """
    for intent_name, patterns in _COMPILED_INTENTS:
        matched = []
        for pat in patterns:
            m = pat.search(text)
            if m:
                matched.append(m.group(0))
        if matched:
            return intent_name, matched
    return "unknown", []


def classify_maturity(text):
    """Classify user maturity level from input text.

    Rules:
      - vague_count >= 2 -> "vague"
      - clear_count >= 2 -> "clear"
      - otherwise -> "medium"

    Args:
        text: User input string.

    Returns:
        Tuple of (maturity_string, vague_count, clear_count).
    """
    vague_count = sum(1 for pat in _COMPILED_VAGUE if pat.search(text))
    clear_count = sum(1 for pat in _COMPILED_CLEAR if pat.search(text))

    if vague_count >= 2:
        return "vague", vague_count, clear_count
    if clear_count >= 2:
        return "clear", vague_count, clear_count
    return "medium", vague_count, clear_count


def determine_flow(intent, maturity):
    """Determine recommended flow from intent and maturity.

    Flow mapping:
      new_project + vague   -> scene_exploration
      new_project + medium  -> warm_start
      new_project + clear   -> standard_diagnosis
      takeover   + *        -> flow_b
      continue   + *        -> flow_c
      unknown    + *        -> ask_user

    Args:
        intent: Intent string from classify_intent().
        maturity: Maturity string from classify_maturity().

    Returns:
        Recommended flow string.
    """
    if intent == "new_project":
        if maturity == "vague":
            return "scene_exploration"
        if maturity == "clear":
            return "standard_diagnosis"
        return "warm_start"
    if intent == "takeover":
        return "flow_b"
    if intent == "continue":
        return "flow_c"
    return "ask_user"


def determine_confidence(intent, maturity, vague_count, clear_count):
    """Determine confidence level of the classification.

    Rules:
      - Intent matched a trigger AND maturity is decisive (>=2 signals)
        -> "high"
      - Intent matched OR maturity has some signals (>=1)
        -> "medium"
      - Neither intent nor maturity signals found
        -> "low"

    Args:
        intent: Intent string.
        maturity: Maturity string.
        vague_count: Number of vague signals matched.
        clear_count: Number of clear signals matched.

    Returns:
        Confidence string.
    """
    intent_known = intent != "unknown"
    maturity_decisive = vague_count >= 2 or clear_count >= 2
    maturity_partial = vague_count >= 1 or clear_count >= 1

    if intent_known and maturity_decisive:
        return "high"
    if intent_known or maturity_partial:
        return "medium"
    return "low"


def route(text):
    """Route user input to intent, maturity, and recommended flow.

    Args:
        text: User input string.

    Returns:
        Dict with keys: intent, maturity, recommended_flow, confidence,
        matched_triggers.
    """
    intent, matched_triggers = classify_intent(text)
    maturity, vague_count, clear_count = classify_maturity(text)
    flow = determine_flow(intent, maturity)
    confidence = determine_confidence(intent, maturity, vague_count, clear_count)

    return {
        "intent": intent,
        "maturity": maturity,
        "recommended_flow": flow,
        "confidence": confidence,
        "matched_triggers": matched_triggers,
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python intent-router.py \"<user-input-text>\"", file=sys.stderr)
        return 1

    text = sys.argv[1].strip()
    if not text:
        print("Error: Empty input text", file=sys.stderr)
        return 1

    result = route(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
