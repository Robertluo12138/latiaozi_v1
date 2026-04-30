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
  4. (FAIL) No overly generic second-level titles. A title fails if
     ANY of:
       a. Contains NO judgment / trend / action / state word from the
          curated `JUDGMENT_WORDS` list (any length). This blocks bare
          tool-name and platform-name titles regardless of how many
          Chinese characters they have — e.g. `ODPS 工具链：`,
          `FBI 看板：`, `Qoderwork 数据连接：`, `自助分析平台：`,
          `经营看板系统：`, `用户增长平台：`. The doc's "二级标题语义
          形态" rule (action + result + business meaning) requires
          every title to carry at least one verb / outcome / state
          token, so the validator enforces that contract directly; OR
       b. Ends in a placeholder / container suffix that turns the title
          back into a field-name or bare tool-name label
          regardless of length: `情况` / `数据` / `工作` / `现状` /
          `概况` / `平台` / `系统` / `工具链` / `看板` / `工作台` —
          e.g. `用户增长情况：`, `用户增长平台：`; OR
       c. Matches the `[Container][TailVerb]$` shape — i.e. ends with a
          single action verb (`迭代` / `上线` / `落地` / `打通` ...)
          that immediately follows a container noun (`看板` / `平台` /
          `系统` / `工具链` / `工作台` / `报告` / `工具` / `站点` /
          `链路`), with nothing else after the container besides the
          verb — e.g. `经营看板迭代：` (= `看板` + `迭代` at end).
          A legitimate title needs a specifying noun / outcome between
          the container and the verb (`...看板维度持续补齐：`).
  5. No forbidden "process narration" phrases in positive example output
     blocks. The skill must output the final 拉条子 only, never the
     internal extraction / bucketing / rewrite-explanation steps. The
     phrases checked: 现在我来 / 先做抽取 / 原文事实抽取 / 归桶 /
     以下是改写结果 / 改写如下.
  6. No more than 2 occurrences of "待补充：" per positive example
     output block. Normal monthly-report rewrites should rely on
     qualitative judgments instead of stacking placeholders; the upper
     limit only relaxes when the user explicitly asks for a
     data-completeness review.
  7. No 放大型 (amplification) wording in positive example output
     blocks. The skill must use measured business language; the
     following words leak absolute / over-claim tone and are forbidden
     unless the user's own input contained them: 零门槛 / 大幅 /
     明显提升 / 完全打通 / 全自动 / 闭环完成 / 显著 / 极大 / 巨大.
     `明显提升` was added alongside `大幅提升` because it implies a
     specific magnitude of improvement but is almost always written
     without supporting data — i.e. "looks measured but actually
     amplifies". See SKILL.md "业务措辞克制" + style_rules.md §6.2
     and §11.4 for the rule text.

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

# Judgment / trend / action vocabulary. A short title that contains any of
# these reads as a conclusion rather than a bare field-name label. The list
# spans trend (增长 / 下行 / 收敛 ...), state (稳定 / 偏高 / 不足 ...),
# action (上线 / 打通 / 建成 / 跑通 / 落地 / 治理 / 修复 / 推进 ...) and
# comparison (低于 / 高于 / 逼近) — broad enough to avoid false positives
# on legitimate "动作 + 结果" titles while still catching bare tool-name
# titles like "ODPS 工具链：" / "FBI 看板：".
JUDGMENT_WORDS = [
    # Trend
    "增长", "提升", "下滑", "下行", "上行", "改善", "改观",
    "收敛", "扩张", "抬升", "攀升", "放缓", "加速", "回落",
    "失血", "反弹",
    # State
    "稳定", "维稳", "偏弱", "偏高", "偏低", "偏重", "集中",
    "分散", "健康", "风险", "空白", "不足", "充足",
    # Action / outcome
    "上线", "打通", "建成", "跑通", "落地", "治理", "修复",
    "推进", "突破", "探索", "验证", "评估", "迭代", "消化",
    "扩展", "补齐", "接入", "收口", "沉淀", "启动", "立项",
    "跟进", "升级", "承接", "挤压", "重合", "补位", "钻取",
    "聚焦", "回归", "形成", "持续", "完成", "达成", "达标",
    "支撑", "拉动", "拖累", "驱动", "覆盖", "纳入",
    "先行", "细分", "成为",
    # Comparison
    "低于", "高于", "等于", "接近", "逼近",
    # Modifier / state qualifier (when used as judgment)
    "明显", "初步", "可见", "可用", "全程", "阻力",
]

# Placeholder / container suffixes turn any title back into a field-name or
# tool-name label even when the title is long enough or contains a judgment
# word elsewhere. Two groups:
#
#   - Generic placeholder suffixes (`情况` / `数据` / `工作` / `现状` /
#     `概况`) — explicitly listed as bad shapes in style_rules.md /
#     checklist.md (e.g. `用户增长情况：`, `本月数据：`, `经营情况：`).
#   - Container suffixes (`平台` / `系统` / `工具链` / `看板` / `工作台`)
#     — listed as bad shapes in style_rules.md 10.6 / SKILL.md
#     "二级标题语义形态" (e.g. `自助分析平台：`, `经营看板系统：`,
#     `用户增长平台：`, `Agent 工作台：`). These names need a verb /
#     outcome word to become a legitimate "动作 + 结果 + 业务意义" title.
PLACEHOLDER_SUFFIXES = [
    "情况", "数据", "工作", "现状", "概况",
    "平台", "系统", "工具链", "看板", "工作台",
]

# Tool / platform / container nouns that must NOT be the immediate
# left-context of a single tail verb. The pattern `[Container][TailVerb]$`
# (e.g. `看板迭代`, `平台上线`, `系统落地`, `工具链打通`) is a bare
# tool-name + verb shape — it states an action on a tool but does not
# specify the result / scope / business meaning that the doc's
# "动作 + 结果 + 业务意义" rule requires. A specifying noun between
# the container and the verb (e.g. `看板维度持续补齐`) lifts the title
# out of this trap.
TOOL_NAME_CONTAINERS = [
    "看板", "平台", "系统", "工具链", "工作台",
    "报告", "工具", "站点", "链路",
]
TOOL_NAME_TAIL_VERBS = [
    "迭代", "上线", "建成", "落地", "打通", "搭建",
    "修复", "治理", "推进", "升级", "验证", "探索",
    "启动", "跑通", "收敛", "推出", "接入", "改造",
    "重构", "搭通",
]

# Process-narration phrases that must never leak into a final output. The
# skill is required to emit only the rewritten 拉条子, never the internal
# extraction / bucketing / rewrite-explanation steps.
FORBIDDEN_PROCESS_PHRASES = [
    "现在我来",
    "先做抽取",
    "原文事实抽取",
    "归桶",
    "以下是改写结果",
    "改写如下",
]

# In normal monthly-report rewrites the skill should rely on qualitative
# judgments rather than stacking placeholders. Cap at 2 occurrences per
# example output block.
MAX_PLACEHOLDER_PER_BLOCK = 2
PLACEHOLDER_TOKEN = "待补充："

# 放大型 wording — absolute / over-claim words that leak exaggerated tone.
# Forbidden in positive example output blocks unless the user's input
# explicitly used them. Listed in SKILL.md > 业务措辞克制 and recommended
# replacements live in references/style_rules.md.
#
# `明显提升` is grouped here alongside `大幅提升` (already covered by the
# `大幅` substring): both imply a specific magnitude of improvement but are
# almost always written without supporting data — "looks measured, actually
# amplifies". `明显` alone is NOT forbidden because it is a legitimate
# directional modifier ("明显抬升" / "明显下行" with an accompanying number
# is fine); only the `明显提升` phrase is banned.
FORBIDDEN_AMP_WORDS = [
    "零门槛",
    "大幅",
    "明显提升",
    "完全打通",
    "全自动",
    "闭环完成",
    "显著",
    "极大",
    "巨大",
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


def count_chinese_chars(s: str) -> int:
    """Count CJK Unified Ideographs in s (excludes ASCII / digits / punct)."""
    return sum(1 for c in s if "一" <= c <= "鿿")


def _matches_tool_verb_tail(sj: str) -> tuple[str, str] | None:
    """If `sj` ends with `[Container][TailVerb]`, return (container, verb).

    The container must be the immediate left-neighbor of the verb — i.e.
    the prefix before the verb must end exactly with the container, with
    no specifying noun in between. Returns None on no match."""
    for verb in TOOL_NAME_TAIL_VERBS:
        if not sj.endswith(verb):
            continue
        prefix = sj[: -len(verb)]
        for cont in TOOL_NAME_CONTAINERS:
            if prefix.endswith(cont):
                return cont, verb
    return None


def check_generic_titles(blocks: list[str]) -> list[tuple[int, str, str]]:
    """Flag short judgments that read as bare field-name / tool-name labels:

      a. Contains no judgment / trend / action / state word (any length).
         Catches `ODPS 工具链：` (3 中文字) AND `自助分析平台：` (6 中文字).
      b. Ends in a placeholder / container suffix (情况 / 数据 / 工作 /
         现状 / 概况 / 平台 / 系统 / 工具链 / 看板 / 工作台). Catches
         titles like `用户增长平台：` that have a judgment word elsewhere
         but still resolve to a bare X+container shape.
      c. Matches `[Container][TailVerb]$` — a single verb directly after
         a container noun at the end of the title (`经营看板迭代：` =
         看板 + 迭代). The doc requires a specifying noun / scope /
         result between the container and the verb.

    Returns (example_index, short_judgment, reason)."""
    flagged: list[tuple[int, str, str]] = []
    for i, block in enumerate(blocks, 1):
        for m in SHORT_JUDGMENT_RE.finditer(block):
            sj = m.group(1).rstrip()
            if not any(w in sj for w in JUDGMENT_WORDS):
                cn = count_chinese_chars(sj)
                flagged.append((i, sj, f"{cn} 中文字, 缺判断/动作词"))
                continue
            suffix_hit = next((s for s in PLACEHOLDER_SUFFIXES if sj.endswith(s)), None)
            if suffix_hit:
                flagged.append((i, sj, f"placeholder 后缀 {suffix_hit!r}"))
                continue
            tv = _matches_tool_verb_tail(sj)
            if tv is not None:
                cont, verb = tv
                flagged.append(
                    (i, sj, f"[{cont}][{verb}] 容器 + 尾动词形态"),
                )
    return flagged


def check_process_phrases(blocks: list[str]) -> list[tuple[int, str]]:
    """Flag any positive example block that leaks process-narration phrases.

    Returns (example_index, phrase)."""
    violations: list[tuple[int, str]] = []
    for i, block in enumerate(blocks, 1):
        for phrase in FORBIDDEN_PROCESS_PHRASES:
            if phrase in block:
                violations.append((i, phrase))
    return violations


def check_placeholder_count(blocks: list[str]) -> list[tuple[int, int]]:
    """Flag positive example blocks that exceed the placeholder cap.

    Returns (example_index, count)."""
    violations: list[tuple[int, int]] = []
    for i, block in enumerate(blocks, 1):
        n = block.count(PLACEHOLDER_TOKEN)
        if n > MAX_PLACEHOLDER_PER_BLOCK:
            violations.append((i, n))
    return violations


def check_amplification_words(blocks: list[str]) -> list[tuple[int, str]]:
    """Flag any positive example block that contains 放大型 wording.

    Returns (example_index, word)."""
    violations: list[tuple[int, str]] = []
    for i, block in enumerate(blocks, 1):
        for w in FORBIDDEN_AMP_WORDS:
            if w in block:
                violations.append((i, w))
    return violations


def main() -> int:
    print(f"Validating skill at: {SKILL_DIR}")
    print()

    failed = False

    # ---- Check 1: required files ----
    print("[1/7] Required files exist")
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
    print("\n[2/7] No bare field-name labels in positive examples")
    bare = check_bare_labels(blocks)
    if bare:
        print(f"  FAIL: {len(bare)} bare label(s):")
        for ex_idx, fn in bare:
            print(f"    example {ex_idx}: **{fn}：**")
        failed = True
    else:
        print("  OK: zero bare field-name labels")

    # ---- Check 3: forbidden punctuation in second-level titles ----
    print("\n[3/7] No forbidden punctuation in 二级标题 (before 冒号)")
    bad_punct = check_forbidden_punct(blocks)
    total_titles = sum(len(SHORT_JUDGMENT_RE.findall(b)) for b in blocks)
    if bad_punct:
        print(f"  FAIL: {len(bad_punct)} short judgment(s) with forbidden punct:")
        for ex_idx, sj, bad in bad_punct:
            print(f"    example {ex_idx}: {sj!r}  forbidden={bad}")
        failed = True
    else:
        print(f"  OK: {total_titles} short judgments scanned, all clean")

    # ---- Check 4: overly generic short judgments (FAIL) ----
    print("\n[4/7] No overly generic 二级标题 "
          "(工具名/平台名独立成标 或 情况/数据 等占位后缀)")
    generic = check_generic_titles(blocks)
    if generic:
        print(f"  FAIL: {len(generic)} generic title(s) "
              f"(tool / platform names without action / judgment word):")
        for ex_idx, sj, reason in generic:
            print(f"    example {ex_idx}: {sj!r}  ({reason})")
        failed = True
    else:
        print("  OK: no overly generic short judgments detected")

    # ---- Check 5: forbidden process-narration phrases ----
    print("\n[5/7] No process-narration phrases in positive examples")
    proc_violations = check_process_phrases(blocks)
    if proc_violations:
        print(f"  FAIL: {len(proc_violations)} process phrase leak(s):")
        for ex_idx, phrase in proc_violations:
            print(f"    example {ex_idx}: {phrase!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_PROCESS_PHRASES)} forbidden phrases scanned, zero hits")

    # ---- Check 6: placeholder count cap ----
    print(f"\n[6/7] No more than {MAX_PLACEHOLDER_PER_BLOCK} occurrences of "
          f"{PLACEHOLDER_TOKEN!r} per example output block")
    pl_violations = check_placeholder_count(blocks)
    if pl_violations:
        print(f"  FAIL: {len(pl_violations)} block(s) over the cap:")
        for ex_idx, n in pl_violations:
            print(f"    example {ex_idx}: {n} occurrences (max {MAX_PLACEHOLDER_PER_BLOCK})")
        failed = True
    else:
        per_block = [b.count(PLACEHOLDER_TOKEN) for b in blocks]
        print(f"  OK: per-block counts {per_block}, all within cap")

    # ---- Check 7: 放大型 wording ----
    print("\n[7/7] No 放大型 wording in positive examples "
          "(零门槛 / 大幅 / 明显提升 / 完全打通 / 全自动 / 闭环完成 / 显著 / 极大 / 巨大)")
    amp_violations = check_amplification_words(blocks)
    if amp_violations:
        print(f"  FAIL: {len(amp_violations)} amp word leak(s):")
        for ex_idx, w in amp_violations:
            print(f"    example {ex_idx}: {w!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_AMP_WORDS)} forbidden amp words scanned, zero hits")

    print()
    if failed:
        print("VALIDATION FAILED")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
