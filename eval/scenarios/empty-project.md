# Scenario A: Empty Project → Continue Development

## Input
- Empty temporary directory (no files)
- User says: "继续开发"

## Expected Behavior
1. Skill checks for .project-state.md → not found
2. Output error: "没有找到项目状态文件，请先「分析项目」或「新建项目」"
3. Exit gracefully without crashing

## Assertions
- [ ] state-validator.py returns exit code 1 (file not found)
- [ ] Error message mentions missing state file
- [ ] Suggests running "analyze project" or "new project"
