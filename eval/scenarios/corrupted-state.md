# Scenario B: Corrupted State File

## Input
- Project directory with a .project-state.md that has broken YAML:
  ```
  ---
  name: test project
  created: not-a-date
  status: INVALID
  ---
  ```

## Expected Behavior
1. state-validator.py detects invalid fields
2. Returns exit code 3 (validation failed)
3. Reports specific validation errors

## Assertions
- [ ] state-validator.py returns exit code 3
- [ ] Error mentions pattern mismatch for 'name'
- [ ] Error mentions invalid date format for 'created'
- [ ] Error mentions invalid enum value for 'status'
