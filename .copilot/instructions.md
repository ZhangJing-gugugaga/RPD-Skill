# RPD Skill — Copilot Instructions

This is a Claude Code Skill (RPD) for product requirement documentation.

## Key patterns
- All Python scripts use stdlib only (no pip dependencies)
- SKILL.md is bilingual (English + Chinese)
- State file uses YAML frontmatter + Markdown body
- Security scanner has 8 rules (SEC-001 to SEC-008)
- Eval suite has 11 scenarios (A/B/C/D/E/F/G/H/I/O/P)

## When writing code
- Follow existing code style in scripts/
- Add Windows encoding fix to new scripts
- Use safe_read_file() for file I/O
- Test with: python scripts/run-eval.py
