# RPD Skill — Copilot Instructions

This is a Copilot Skill (RPD) for product requirement documentation.

## Key Documentation
- `SKILL.md`: Main control instructions (bilingual EN/ZH)
- `CLAUDE.md`: Project-level instructions
- `AGENT.md`: Agent interaction guide
- `行为守则.md`: AI behavior guidelines

## Key Patterns
- All Python scripts use stdlib only (no pip dependencies)
- SKILL.md is bilingual (English + Chinese)
- State file uses YAML frontmatter + Markdown body
- Security scanner has 8 rules (SEC-001 to SEC-008)
- Eval suite has 11 scenarios (A/B/C/D/E/F/G/H/I/O/P)

## When Writing Code
- Follow existing code style in scripts/
- Add Windows encoding fix to new scripts
- Use `safe_read_file()` for file I/O
- Test with: `python scripts/run-eval.py`
- **Wait for user approval before committing to GitHub**

## Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Usage error |
| 2 | Security block (hard stop) |
| 3 | Validation failed |
| 4 | Git conflict |
