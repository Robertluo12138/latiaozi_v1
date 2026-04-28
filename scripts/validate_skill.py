#!/usr/bin/env python3
"""Validate the latiaozi_v1 skill in the skill/ directory.

Checks:
  1. All required skill files exist.
  2. Positive example output blocks (the "### 拉条子改写" sections in
     skill/references/examples.md) contain no bare field-name labels
     such as **GMV：**, **订单：**, **SQL：**, **看板：**, **数据集：**.
  3. No second-level title (the bold short-judgment before the 冒号 in a
     positive example) contains forbidden punctuation:
     ASCII , . ;  /  Chinese ， 。 ； 、

Exits 0 on success, 1 on failure. Python standard library only.

Usage:
    python3 scripts/validate_skill.py
"""

from __future__ import annotations

import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skill"

REQUIRED_FILES = [
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "references" / "style_rules.md",
    SKILL_DIR / "references" / "examples.md",
    SKILL_DIR / "references" / "checklist.md",
    SKILL_DIR / "evals" / "test_cases.md",
]

FORBIDDEN_PUNCT = [",", ".", ";", "，", "。", "；", "、"]

BARE_FIELD_NAMES = [
    # Required by spec
    "GMV", "订单", "SQL", "看板", "数据集",
    # Common extra cases also worth catching
    "客单价", "Bug", "BUG", "性能", "库存", "延迟",
    "转化率", "DAU", "MAU", "新客", "留存",
    "UV", "PV", "ROI",
]

# **<short_judgment>：**
SHORT_JUDGMENT_RE = re.compile(r"\*\*([^*\n]+?)：\*\*")


def check_files_exist() -> list[str]:
    return [
        str(p.relative_to(ROOT))
        for p in REQUIRED_FILES
        if not p.exists()
    ]


def extract_positive_blocks(examples_path: pathlib.Path) -> list[str]:
    """Return only the '### 拉条子改写' subsections from examples.md."""
    text = examples_path.read_text(encoding="utf-8")
    blocks: list[str] = []
    sections = text.split("## 示例")
    for sec in sections[1:]:
        m = re.search(
            r"### 拉条子改写\s*\n(.*?)(?=\n---\n|\Z)",
            sec,
            flags=re.S,
        )
        if m:
            blocks.append(m.group(1))
    return blocks


def check_bare_labels(blocks: list[str]) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    for i, block in enumerate(blocks, 1):
        for fn in BARE_FIELD_NAMES:
            pat = re.compile(r"\*\*" + re.escape(fn) + r"：\*\*")
            for _ in pat.finditer(block):
                violations.append((i, fn))
    return violations


def check_forbidden_punct(blocks: list[str]) -> list[tuple[int, str, list[str]]]:
    violations: list[tuple[int, str, list[str]]] = []
    for i, block in enumerate(blocks, 1):
        for m in SHORT_JUDGMENT_RE.finditer(block):
            sj = m.group(1)
            bad = [c for c in FORBIDDEN_PUNCT if c in sj]
            if bad:
                violations.append((i, sj, bad))
    return violations


def main() -> int:
    print(f"Validating skill at: {SKILL_DIR}")
    print()

    failed = False

    # ---- Check 1: required files ----
    print("[1/3] Required files exist")
    missing = check_files_exist()
    if missing:
        print(f"  FAIL: {len(missing)} missing file(s):")
        for m in missing:
            print(f"    - {m}")
        failed = True
    else:
        print(f"  OK: {len(REQUIRED_FILES)} files present")

    # If examples.md is missing, content checks cannot run.
    examples_path = SKILL_DIR / "references" / "examples.md"
    if not examples_path.exists():
        print("\nSkipping content checks: examples.md missing")
        return 1

    blocks = extract_positive_blocks(examples_path)
    print(f"\nExtracted {len(blocks)} positive example block(s) from examples.md")

    # ---- Check 2: bare field-name labels ----
    print("\n[2/3] No bare field-name labels in positive examples")
    bare = check_bare_labels(blocks)
    if bare:
        print(f"  FAIL: {len(bare)} bare label(s):")
        for ex_idx, fn in bare:
            print(f"    example {ex_idx}: **{fn}：**")
        failed = True
    else:
        print("  OK: zero bare field-name labels")

    # ---- Check 3: forbidden punctuation in second-level titles ----
    print("\n[3/3] No forbidden punctuation in 二级标题 (before 冒号)")
    bad_punct = check_forbidden_punct(blocks)
    total_titles = sum(len(SHORT_JUDGMENT_RE.findall(b)) for b in blocks)
    if bad_punct:
        print(f"  FAIL: {len(bad_punct)} short judgment(s) with forbidden punct:")
        for ex_idx, sj, bad in bad_punct:
            print(f"    example {ex_idx}: {sj!r}  forbidden={bad}")
        failed = True
    else:
        print(f"  OK: {total_titles} short judgments scanned, all clean")

    print()
    if failed:
        print("VALIDATION FAILED")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
