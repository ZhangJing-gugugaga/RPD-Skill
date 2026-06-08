# RPD Skill — Codex Instructions

## Project Overview
RPD (Rapid Product Document) is a Codex Skill covering the full project lifecycle: new project → PRD generation → half-finished takeover → continue development.

## Key Documentation
- `SKILL.md`: Main control instructions (bilingual EN/ZH, Hard Constraints)
- `CLAUDE.md`: Project-level instructions
- `AGENT.md`: Agent interaction guide
- `行为守则.md`: AI behavior guidelines

## Architecture
- 8 Python scripts: Deterministic, stdlib-only, zero dependencies
- State file (`.project-state.md`): Cross-session memory anchor
- Hard Constraints: 6 non-negotiable rules

## Scripts
| Script | Purpose | Exit Codes |
|--------|---------|------------|
| intent-router.py | Deterministic intent classification | 0/1 |
| security-scanner.py | 8 SEC rules + path traversal | 0/1/2 |
| project-scanner.py | Tech stack detection | 0/1 |
| gap-analyzer.py | Gap + decision drift analysis | 0/1/3 |
| state-validator.py | State file validation | 0/1/3 |
| state-guard.py | Backup + atomic write + Git check | 0/2/3/4 |
| prd-validator.py | PRD completeness check | 0/1/2 |
| run-eval.py | 11 evaluation scenarios | 0/1 |

## Code Conventions
- Windows encoding fix: `sys.stdout.reconfigure(encoding="utf-8")`
- Path output: `.replace("\\", "/")`
- File read: `safe_read_file()` not `read_text()`
- Comments: `#`, `//`, `*` lines skipped in security scan

## Development Rules
- Run eval after changes: `python scripts/run-eval.py`
- All 11 scenarios must pass
- SKILL.md and README.md must be bilingual
- **Wait for user approval before committing to GitHub**
