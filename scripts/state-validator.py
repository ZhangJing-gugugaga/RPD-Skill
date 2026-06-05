#!/usr/bin/env python3
"""Validate .project-state.md YAML frontmatter against JSON Schema.

Usage: python state-validator.py <path-to-project-state.md>

Exit codes:
  0 - Valid
  1 - File not found or unreadable
  2 - YAML frontmatter missing or malformed
  3 - Schema validation failed
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# --- Schema validation (stdlib-only, no jsonschema dependency) ---

def validate_type(value, schema_type):
    """Check if value matches the expected JSON Schema type."""
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "null":
        return value is None
    return True


def validate_enum(value, enum_values):
    """Check if value is one of the allowed enum values."""
    return value in enum_values


def validate_pattern(value, pattern):
    """Check if string value matches the regex pattern."""
    return bool(re.match(pattern, value))


def validate_format_date(value):
    """Check if string is a valid date (YYYY-MM-DD)."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_format_datetime(value):
    """Check if string is a valid ISO 8601 datetime."""
    try:
        # Try with T separator
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        try:
            # Try without T (space separator)
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False


def validate_schema(data, schema):
    """Validate data against a JSON Schema. Returns list of errors."""
    errors = []

    if not isinstance(data, dict):
        return ["Root value must be an object"]

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # Check each property
    properties = schema.get("properties", {})
    for key, value in data.items():
        if key not in properties:
            if not schema.get("additionalProperties", True):
                errors.append(f"Unknown field: '{key}'")
            continue

        prop_schema = properties[key]

        # Type check
        expected_type = prop_schema.get("type")
        if expected_type and not validate_type(value, expected_type):
            errors.append(f"Field '{key}': expected {expected_type}, got {type(value).__name__}")
            continue

        # Enum check
        if "enum" in prop_schema and not validate_enum(value, prop_schema["enum"]):
            errors.append(f"Field '{key}': value '{value}' not in {prop_schema['enum']}")

        # Pattern check
        if "pattern" in prop_schema and isinstance(value, str):
            if not validate_pattern(value, prop_schema["pattern"]):
                errors.append(f"Field '{key}': value '{value}' doesn't match pattern '{prop_schema['pattern']}'")

        # String length
        if isinstance(value, str):
            if "minLength" in prop_schema and len(value) < prop_schema["minLength"]:
                errors.append(f"Field '{key}': too short (min {prop_schema['minLength']})")
            if "maxLength" in prop_schema and len(value) > prop_schema["maxLength"]:
                errors.append(f"Field '{key}': too long (max {prop_schema['maxLength']})")

        # Format checks
        fmt = prop_schema.get("format")
        if fmt == "date" and isinstance(value, str):
            if not validate_format_date(value):
                errors.append(f"Field '{key}': invalid date format, expected YYYY-MM-DD")
        elif fmt == "date-time" and isinstance(value, str):
            if not validate_format_datetime(value):
                errors.append(f"Field '{key}': invalid datetime format, expected ISO 8601")

    return errors


# --- YAML frontmatter extraction ---

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content. Returns dict or None."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    # Simple YAML parser (handles flat key-value pairs only)
    frontmatter = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove inline comments
            if " #" in value:
                value = value[:value.index(" #")].strip()
            # Remove quotes
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            frontmatter[key] = value

    return frontmatter


# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python state-validator.py <path-to-project-state.md>", file=sys.stderr)
        return 1

    file_path = Path(sys.argv[1])

    # Check file exists
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    # Read file
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error: Cannot read file: {e}", file=sys.stderr)
        return 1

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)
    if frontmatter is None:
        print("Error: No valid YAML frontmatter found (must be delimited by ---)", file=sys.stderr)
        return 2

    # Load schema
    schema_path = Path(__file__).parent.parent / "references" / "state-schema.json"
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error: Cannot parse schema: {e}", file=sys.stderr)
        return 1

    # Validate
    errors = validate_schema(frontmatter, schema)

    if errors:
        print("Validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 3

    print("Validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
