#!/usr/bin/env python3
"""State file guard: physical backup + atomic write + post-write validation.

Usage:
  python state-guard.py <state-file> --action backup    # Create backup
  python state-guard.py <state-file> --action restore   # Restore from latest backup
  python state-guard.py <state-file> --action list      # List available backups
  python state-guard.py <state-file> --action update <content-file>  # Atomic update with validation

Exit codes:
  0 - Success
  1 - Usage error
  2 - Validation failed (rolled back)
  3 - File not found
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_backup_dir(state_file_path: Path) -> Path:
    """Get or create backup directory next to the state file."""
    backup_dir = state_file_path.parent / ".state-backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def create_backup(state_file_path: Path) -> Path:
    """Create a timestamped backup of the state file."""
    if not state_file_path.exists():
        print(f"Error: State file not found: {state_file_path}", file=sys.stderr)
        sys.exit(3)

    backup_dir = get_backup_dir(state_file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"state-{timestamp}.md"
    shutil.copy2(state_file_path, backup_path)

    # Keep only the latest 10 backups (prevent bloat)
    cleanup_old_backups(backup_dir)

    print(f"Backup created: {backup_path}")
    return backup_path


def cleanup_old_backups(backup_dir: Path, max_backups: int = 10) -> None:
    """Remove old backups, keeping only the most recent ones."""
    backups = sorted(backup_dir.glob("state-*.md"))
    for old in backups[:-max_backups]:
        old.unlink()
        print(f"Removed old backup: {old.name}")


def list_backups(state_file_path: Path) -> None:
    """List available backups for the state file."""
    backup_dir = get_backup_dir(state_file_path)
    backups = sorted(backup_dir.glob("state-*.md"))

    if not backups:
        print("No backups found.")
        return

    print(f"Available backups for {state_file_path.name}:")
    for i, backup in enumerate(reversed(backups), 1):
        print(f"  {i}. {backup.name}")


def restore_backup(state_file_path: Path) -> None:
    """Restore the state file from the latest backup."""
    backup_dir = get_backup_dir(state_file_path)
    backups = sorted(backup_dir.glob("state-*.md"))

    if not backups:
        print("Error: No backups available to restore.", file=sys.stderr)
        sys.exit(3)

    latest_backup = backups[-1]
    shutil.copy2(latest_backup, state_file_path)
    print(f"Restored from: {latest_backup.name}")


def run_validator(state_file_path: Path) -> int:
    """Run state-validator.py on the state file. Returns exit code."""
    script_dir = Path(__file__).parent
    validator_path = script_dir / "state-validator.py"

    if not validator_path.exists():
        print(f"Warning: Validator not found at {validator_path}", file=sys.stderr)
        return 0  # Skip validation if validator not found

    import subprocess
    result = subprocess.run(
        [sys.executable, str(validator_path), str(state_file_path)],
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def atomic_update(state_file_path: Path, content_file: Path) -> None:
    """Atomically update state file with backup and validation."""
    if not content_file.exists():
        print(f"Error: Content file not found: {content_file}", file=sys.stderr)
        sys.exit(3)

    # Step 1: Physical backup (before update)
    create_backup(state_file_path)

    # Step 2: Read new content
    new_content = content_file.read_text(encoding="utf-8")

    # Step 3: Atomic write (write to temp file, then rename)
    tmp_path = state_file_path.with_suffix(".md.tmp")
    try:
        tmp_path.write_text(new_content, encoding="utf-8")
        os.replace(tmp_path, state_file_path)
        print(f"Atomic write completed: {state_file_path}")
    except Exception as e:
        # Clean up temp file if write failed
        if tmp_path.exists():
            tmp_path.unlink()
        raise e

    # Step 4: Post-write validation
    result = run_validator(state_file_path)
    if result != 0:
        # Rollback to latest backup
        backup_dir = get_backup_dir(state_file_path)
        backups = sorted(backup_dir.glob("state-*.md"))
        if backups:
            latest_backup = backups[-1]
            shutil.copy2(latest_backup, state_file_path)
            print(f"Validation failed. Rolled back to: {latest_backup.name}", file=sys.stderr)
        else:
            print("Validation failed and no backup available for rollback!", file=sys.stderr)
        sys.exit(2)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    state_file = Path(sys.argv[1]).resolve()
    action = sys.argv[2]

    if action == "--action":
        if len(sys.argv) < 4:
            print("Error: --action requires a value (backup|restore|list|update)", file=sys.stderr)
            sys.exit(1)
        action = sys.argv[3]

    if action == "backup":
        create_backup(state_file)
    elif action == "restore":
        restore_backup(state_file)
    elif action == "list":
        list_backups(state_file)
    elif action == "update":
        if len(sys.argv) < 5:
            print("Error: update requires a content file path", file=sys.stderr)
            sys.exit(1)
        content_file = Path(sys.argv[4]).resolve()
        atomic_update(state_file, content_file)
    else:
        print(f"Error: Unknown action '{action}'", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
