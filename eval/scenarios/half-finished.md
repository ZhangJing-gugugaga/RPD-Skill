# Scenario D: Half-Finished Project Takeover

## Input
- React project with:
  - package.json (react, vite dependencies)
  - src/components/Login.jsx
  - src/pages/Home.jsx with TODO comment
  - src/pages/Dashboard.jsx
  - No .project-state.md

## Expected Behavior
1. project-scanner.py detects react framework, vite build tool
2. Identifies 3 components (Login, Home, Dashboard)
3. Finds 1 TODO comment
4. Reports correct stats

## Assertions
- [ ] project-scanner.py returns exit code 0
- [ ] tech_stack.framework is "react"
- [ ] tech_stack.build_tool is "vite"
- [ ] components list has 3 entries
- [ ] todos list has at least 1 entry
- [ ] Output is valid JSON
