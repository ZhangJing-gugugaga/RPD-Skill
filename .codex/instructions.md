# RPD Skill — Codex Instructions

## Project Overview
RPD (Rapid Product Document) is a Claude Code Skill covering the full project lifecycle: new project → PRD generation → half-finished takeover → continue development.

## Architecture
- SKILL.md: Main control file with Hard Constraints
- 8 Python scripts: Deterministic, stdlib-only, zero dependencies
- State file (.project-state.md): Cross-session memory anchor

## Scripts
| Script | Purpose |
|--------|---------|
| intent-router.py | Deterministic intent classification |
| security-scanner.py | 8 SEC rules + path traversal |
| project-scanner.py | Tech stack detection |
| gap-analyzer.py | Gap + decision drift analysis |
| state-validator.py | State file validation |
| state-guard.py | Backup + atomic write + Git check |
| prd-validator.py | PRD completeness check |
| run-eval.py | 11 evaluation scenarios |

## Code Conventions
- Windows encoding fix: sys.stdout.reconfigure(encoding="utf-8")
- Path output: .replace("\\", "/")
- File read: safe_read_file() not read_text()
- Comments: #, //, * lines skipped in security scan
