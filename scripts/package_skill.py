#!/usr/bin/env python3
"""Package the skill/ directory into dist/latiaozi_v1.zip.

The zip is built from the *contents* of skill/, so unzipping yields:

    SKILL.md
    references/
    evals/

NOT skill/SKILL.md.

The validator runs first; packaging is aborted on any validation failure.

Stdlib only. Usage:

    python3 scripts/package_skill.py
"""

from __future__ import annotations

import sys
import zipfile
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skill"
DIST_DIR = ROOT / "dist"
ZIP_PATH = DIST_DIR / "latiaozi_v1.zip"
VALIDATOR = ROOT / "scripts" / "validate_skill.py"

# Top-level entries that must NOT appear inside the zip
FORBIDDEN_TOP_LEVELS = {"skill", ".claude", "skills", "ali-latiao-writing", "latiaozi_v1"}
EXPECTED_TOP_LEVELS = {"SKILL.md", "references", "evals"}


def run_validator() -> None:
    print("Running validator first...", flush=True)
    print("-" * 60, flush=True)
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=str(ROOT))
    print("-" * 60, flush=True)
    if result.returncode != 0:
        print("Validator failed; refusing to package.", flush=True)
        sys.exit(1)


def should_skip(path: pathlib.Path) -> bool:
    """Skip OS / editor / Python cache cruft when zipping."""
    parts = path.relative_to(SKILL_DIR).parts
    if any(p.startswith(".") for p in parts):
        return True
    if "__pycache__" in parts:
        return True
    if path.name in {".DS_Store", "Thumbs.db"}:
        return True
    return False


def build_zip() -> int:
    if not SKILL_DIR.is_dir():
        print(f"FAIL: {SKILL_DIR} does not exist")
        sys.exit(1)

    DIST_DIR.mkdir(exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    file_count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SKILL_DIR.rglob("*")):
            if not path.is_file():
                continue
            if should_skip(path):
                continue
            arcname = path.relative_to(SKILL_DIR)
            zf.write(path, arcname=str(arcname))
            file_count += 1
            print(f"  + {arcname}")
    return file_count


def verify_zip() -> None:
    """Confirm the zip's top-level layout matches what desktop agents expect."""
    print("\nVerifying zip top-level layout...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        names = zf.namelist()

    top_levels = sorted({n.split("/")[0] for n in names if n})
    print(f"  Top-level entries: {top_levels}")

    forbidden_present = FORBIDDEN_TOP_LEVELS & set(top_levels)
    if forbidden_present:
        print(f"  FAIL: zip contains forbidden top-level wrapper(s): {sorted(forbidden_present)}")
        sys.exit(1)

    missing = EXPECTED_TOP_LEVELS - set(top_levels)
    if missing:
        print(f"  FAIL: zip missing expected top-level entries: {sorted(missing)}")
        sys.exit(1)

    print(f"  OK: zip extracts to root with {sorted(EXPECTED_TOP_LEVELS)}")


def main() -> None:
    run_validator()
    print()
    print(f"Building {ZIP_PATH.relative_to(ROOT)}")
    print("=" * 60)
    file_count = build_zip()
    size = ZIP_PATH.stat().st_size
    print(f"\nWrote {ZIP_PATH.relative_to(ROOT)}  ({file_count} files, {size} bytes)")
    verify_zip()
    print("\nPACKAGING SUCCEEDED")


if __name__ == "__main__":
    main()
