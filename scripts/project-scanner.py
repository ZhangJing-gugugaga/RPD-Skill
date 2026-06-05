#!/usr/bin/env python3
"""Scan a project directory to detect tech stack, structure, and code status.

Usage: python project-scanner.py <project-directory>

Exit codes:
  0 - Scan complete
  1 - Directory not found or not readable

Output: JSON to stdout with project analysis.
"""

import json
import os
import re
import sys
from pathlib import Path

# --- Tech stack detection ---

FRAMEWORK_INDICATORS = {
    "react": ["package.json:react", "jsx", "tsx"],
    "vue": ["package.json:vue", ".vue"],
    "angular": ["package.json:@angular/core", "angular.json"],
    "svelte": ["package.json:svelte", ".svelte"],
    "next": ["package.json:next"],
    "nuxt": ["package.json:nuxt"],
    "express": ["package.json:express"],
    "fastapi": ["requirements.txt:fastapi", "pyproject.toml:fastapi"],
    "django": ["requirements.txt:django", "manage.py"],
    "flask": ["requirements.txt:flask"],
    "spring": ["pom.xml", "build.gradle:spring-boot"],
    "gin": ["go.mod:gin-gonic"],
}

BUILD_TOOL_INDICATORS = {
    "vite": ["vite.config.js", "vite.config.ts", "vite"],
    "webpack": ["webpack.config.js", "webpack.config.ts", "webpack"],
    "next": ["next.config.js", "next.config.mjs"],
    "create-react-app": ["react-scripts"],
    "parcel": [".parcelrc"],
}

LANGUAGE_EXTENSIONS = {
    ".js": "javascript", ".jsx": "javascript", ".ts": "typescript",
    ".tsx": "typescript", ".py": "python", ".go": "go",
    ".java": "java", ".rs": "rust", ".rb": "ruby",
    ".php": "php", ".cs": "csharp", ".swift": "swift",
    ".kt": "kotlin", ".dart": "dart", ".vue": "vue",
    ".svelte": "svelte",
}

SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
}


def detect_tech_stack(project_dir):
    """Detect the technology stack from project files."""
    p = Path(project_dir)
    tech = {"language": "unknown", "framework": "unknown", "build_tool": "unknown", "package_manager": "unknown"}

    # Detect language by file extensions
    lang_counts = {}
    for ext, lang in LANGUAGE_EXTENSIONS.items():
        count = 0
        for f in p.rglob(f"*{ext}"):
            if any(skip in f.parts for skip in SKIP_DIRS):
                continue
            count += 1
        if count > 0:
            lang_counts[lang] = count
    if lang_counts:
        tech["language"] = max(lang_counts, key=lang_counts.get)

    # Detect package manager
    if (p / "package-lock.json").exists():
        tech["package_manager"] = "npm"
    elif (p / "yarn.lock").exists():
        tech["package_manager"] = "yarn"
    elif (p / "pnpm-lock.yaml").exists():
        tech["package_manager"] = "pnpm"
    elif (p / "Pipfile.lock").exists():
        tech["package_manager"] = "pipenv"
    elif (p / "poetry.lock").exists():
        tech["package_manager"] = "poetry"
    elif (p / "requirements.txt").exists():
        tech["package_manager"] = "pip"
    elif (p / "go.sum").exists():
        tech["package_manager"] = "go"
    elif (p / "Cargo.lock").exists():
        tech["package_manager"] = "cargo"

    # Read package.json if exists
    pkg_json = p / "package.json"
    pkg_deps = ""
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
            all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            pkg_deps = " ".join(all_deps.keys())
        except Exception:
            pass

    # Detect framework
    for fw, indicators in FRAMEWORK_INDICATORS.items():
        for indicator in indicators:
            if ":" in indicator:
                file, key = indicator.split(":", 1)
                if (p / file).exists():
                    try:
                        content = (p / file).read_text(encoding="utf-8")
                        if key in content:
                            tech["framework"] = fw
                            break
                    except Exception:
                        pass
            elif indicator.startswith("."):
                found = False
                for f in p.rglob(f"*{indicator}"):
                    if not any(skip in f.parts for skip in SKIP_DIRS):
                        tech["framework"] = fw
                        found = True
                        break
                if found:
                    break
            else:
                if indicator in pkg_deps:
                    tech["framework"] = fw
                    break

    # Detect build tool
    for bt, indicators in BUILD_TOOL_INDICATORS.items():
        for indicator in indicators:
            if indicator.startswith("."):
                if (p / indicator).exists():
                    tech["build_tool"] = bt
                    break
            elif indicator in pkg_deps:
                tech["build_tool"] = bt
                break

    return tech


def detect_structure(project_dir):
    """Detect project directory structure."""
    p = Path(project_dir)
    structure = {"src_dirs": [], "config_files": [], "has_tests": False, "has_docker": False}

    # Common source directories
    for src_dir in ["src", "app", "lib", "pages", "components", "api", "server", "routes"]:
        if (p / src_dir).is_dir():
            structure["src_dirs"].append(src_dir)

    # Config files
    config_patterns = [
        "package.json", "tsconfig.json", "vite.config.*", "webpack.config.*",
        "next.config.*", "angular.json", ".eslintrc*", "eslint.config.*",
        ".prettierrc*", "tailwind.config.*", "postcss.config.*",
        "requirements.txt", "pyproject.toml", "setup.py", "Cargo.toml",
        "go.mod", "pom.xml", "build.gradle", "Makefile", "Dockerfile",
    ]
    for pattern in config_patterns:
        matches = list(p.glob(pattern))
        structure["config_files"].extend([str(m.relative_to(p)) for m in matches])

    # Test detection
    test_indicators = ["test", "tests", "__tests__", "spec", "specs", "pytest.ini", "jest.config.*"]
    for indicator in test_indicators:
        if list(p.glob(indicator)):
            structure["has_tests"] = True
            break

    # Docker detection
    structure["has_docker"] = (p / "Dockerfile").exists() or (p / "docker-compose.yml").exists()

    return structure


def detect_components(project_dir):
    """Detect UI components and pages."""
    p = Path(project_dir)
    components = []

    component_patterns = ["**/*.jsx", "**/*.tsx", "**/*.vue", "**/*.svelte"]
    for pattern in component_patterns:
        for f in p.glob(pattern):
            rel = f.relative_to(p)
            parts = rel.parts
            if any(skip in parts for skip in SKIP_DIRS):
                continue
            name = f.stem
            comp_type = "component"
            if any(kw in str(rel).lower() for kw in ["page", "pages", "view", "views", "route"]):
                comp_type = "page"
            components.append({"name": name, "path": str(rel), "type": comp_type})

    return components


def detect_api_routes(project_dir):
    """Detect API routes from code."""
    p = Path(project_dir)
    routes = []

    # Express-style routes
    route_pattern = re.compile(
        r'(?:app|router|server)\.(get|post|put|delete|patch|all)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    code_extensions = {".js", ".ts", ".py"}
    for ext in code_extensions:
        for f in p.rglob(f"*{ext}"):
            parts = f.relative_to(p).parts
            if any(skip in parts for skip in SKIP_DIRS):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for match in route_pattern.finditer(content):
                    routes.append({"method": match.group(1).upper(), "path": match.group(2)})
            except Exception:
                continue

    # Python Flask/FastAPI routes
    py_route_pattern = re.compile(
        r'@(?:app|router|api)\.(get|post|put|delete|patch|route)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    for f in p.rglob("*.py"):
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for match in py_route_pattern.finditer(content):
                routes.append({"method": match.group(1).upper(), "path": match.group(2)})
        except Exception:
            continue

    return routes


def detect_todos(project_dir):
    """Detect TODO/FIXME/HACK comments in code."""
    p = Path(project_dir)
    todos = []
    todo_pattern = re.compile(r'(TODO|FIXME|HACK|XXX)[:\s]+(.+)', re.IGNORECASE)

    code_extensions = {".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".java", ".rs", ".vue", ".svelte"}

    for f in p.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in code_extensions:
            continue
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue
        try:
            for line_num, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").split("\n"), 1):
                match = todo_pattern.search(line)
                if match:
                    todos.append({
                        "file": f"{f.relative_to(p)}:{line_num}",
                        "text": f"{match.group(1)}: {match.group(2).strip()}",
                    })
        except Exception:
            continue

    return todos


def compute_stats(project_dir):
    """Compute basic project statistics."""
    p = Path(project_dir)
    total_files = 0
    total_lines = 0

    code_extensions = {".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".java", ".rs",
                       ".vue", ".svelte", ".html", ".css", ".scss", ".json", ".md"}

    for f in p.rglob("*"):
        if not f.is_file():
            continue
        parts = f.relative_to(p).parts
        if any(skip in parts for skip in SKIP_DIRS):
            continue
        if f.suffix in code_extensions:
            total_files += 1
            try:
                total_lines += len(f.read_text(encoding="utf-8", errors="ignore").split("\n"))
            except Exception:
                pass

    return {"total_files": total_files, "total_lines": total_lines}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python project-scanner.py <project-directory>")
        return 1

    project_dir = sys.argv[1]
    if not Path(project_dir).is_dir():
        print(f"Error: Not a directory: {project_dir}", file=sys.stderr)
        return 1

    result = {
        "project_root": str(Path(project_dir).resolve()),
        "tech_stack": detect_tech_stack(project_dir),
        "structure": detect_structure(project_dir),
        "components": detect_components(project_dir),
        "api_routes": detect_api_routes(project_dir),
        "todos": detect_todos(project_dir),
        "stats": compute_stats(project_dir),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
