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
  8. No "unnatural AI template" phrases in positive example output
     blocks. The skill must use natural business Chinese, not AI
     template-speak. Forbidden: 使用门槛下行 / 能力获得 /
     数据不可达瓶颈 / 多项能力初步成型 / 消除瓶颈 / 用户不再受
     操作系统差异困扰 / 多端能力获得 / 流程闭环已达成. These read
     as stilted machine-generated wording and are explicitly banned
     in SKILL.md "月报提交模式 > 自然语言度" + style_rules.md
     §12.7. Natural alternatives live in §12.8 (e.g. `降低使用门槛`
     / `形成能力雏形` / `缓解 X 阻力` / `跨端使用条件得到补齐` /
     `双端可装` / `链路初步跑通`).
  9. No unsupported-inference phrases in positive example output
     blocks. These add UI behavior / adoption status / dependency
     removal / automation level / future expansion / business effect
     / user-feeling / data-bottleneck / system-capability /
     operations-virtual-claim wording the user did not state. The
     list mirrors the 8-category "禁止过度推断" inference table in
     SKILL.md / style_rules.md §12.11 + the 6-category "运营月报
     子模式 > 不得虚构" table in §13.8. Curated phrases include:
       - UI:       自行拖拽查询 / 一键导出 / 点击即用
       - 采纳依赖: 不再依赖人工中转 / 已全员采纳 / 数据团队不再承接
       - 自动化:   完整自动化闭环 / 全流程自动化 / 自动化覆盖所有场景
       - 未来扩展: 后续可扩展至 (substring; catches `更多数据域` /
                   `货品维度` / `流量等维度` / `全公司`) /
                   下季度可推广
       - 业务效果: 业务效率提升 / 决策速度加快 / 提升老板满意度
       - 用户感受: 用户不再受系统差异困扰 / 用户体验明显改善
       - 数据瓶颈: 消除数据瓶颈
       - 系统能力: Windows 用户可在本地直接执行 ODPS 查询 /
                   Agent 可承接所有取数场景
       - 运营场景虚构: 商户满意度 / 反响热烈 (substring; catches
                       `商户反响热烈` / `商户对活动反响热烈` /
                       `活动反响热烈` / `本次活动反响热烈` /
                       `市场反响热烈`) / 高度认可 (substring;
                       catches `商户高度认可` / `商户对策略高度
                       认可` / `商户高度认可策略` / `老板高度
                       认可`) / 商户给予正面评价 / 商户主动配合 /
                       商户已全员报名 / 活动效果超预期 /
                       活动 ROI 创新高 / 参与率显著提升 /
                       转化率明显改善 / 推动品类整体增长 /
                       经营改善显著 / 团队协同效率明显改善 /
                       跨团队配合质量大幅提升 / 商户关系全面改善
     Notes: `消除数据瓶颈` is distinct from `消除瓶颈` (unnatural
     list); `用户不再受系统差异困扰` is distinct from the longer
     `用户不再受操作系统差异困扰` (unnatural list) — both must
     fail. The 运营场景虚构 phrases are explicitly listed in
     test_cases.md 用例 16 PASS (i)/(j) and 用例 17 PASS (f) grep
     patterns; the validator now enforces parity. The skill must
     use restrained traceable wording that maps back to specific
     input sentences.
 10. No technical-substrate phrases in operations-mode examples.
     The full 12-phrase list mirrors style_rules.md §13.6:
       - core 6: 数据底座 / 技术基建 / 系统能力 / 链路打通 /
                 模型能力 / 自动化闭环
       - doc additions: 数据连接 / 数据采集 / 接口对接 /
                        监控告警 / 调度任务 / 流程闭环
     Operations-mode examples are detected by section title —
     keywords like 商户拜访 / 活动运营 / 客诉 / 走访 / 运营月报
     trigger ops-mode classification. Technical examples (data /
     SQL / dashboard / Agent / Skill / model) are exempt. This
     catches the common failure mode where the skill applies data-
     infrastructure tone to merchant / activity / customer-complaint
     monthly reports. See SKILL.md "运营月报子模式 > 技术化措辞
     禁忌" + style_rules.md §13.6.
 11. No operations status-upgrade phrases in operations-mode
     examples. Three groups, all forbidden — they overstate the
     actual work status by turning "feedback collected" into
     "issue solved", "aligned with teams" into "rule optimized",
     and "follow-up needed" into "plan landed". Listed in
     SKILL.md "运营状态校准" + style_rules.md §13.10.

     Group A — 5 specific failure-mode phrases:
       - 活动规则优化      (alignment → optimization)
       - 规则简化方向明确  (alignment → decided direction)
       - 专项跟进流程      (follow-up → formal process)
       - 资源分配方案落地  (concern → plan landing)
       - 推进经营改善      (sediment → business improvement)

     Group B — 6 hard-forbidden status-upgrade words from the
     "状态升档禁忌（hard rule）" subsection:
       - 已优化 / 已改善 / 已解决 / 已落地   (completion claims)
       - 方向明确                              (decided direction)
       - 形成闭环                              (closure formed)

     Group C — 8 multi-word ❌ variants from the §13.10
     "输入意图 → 校准措辞映射" table + examples.md mini-对照.
     Group B substrings miss these because of inserted words
     (e.g. `方向已经明确` ≠ `方向明确`) or different prefixes
     (e.g. `规则完成优化` ≠ `已优化`):
       - 反馈已闭环 / 高频反馈已闭环          (闭环 family)
       - 规则完成优化                         (alignment → optimization)
       - 方案完成落地                         (concern → landing)
       - 方向已经明确                         (alignment → direction)
       - 曝光资源完成配置                     (concern → configuration)
       - 商户参与效果改善                     (partial signup → improvement)
       - 商户问题完成解决                     (feedback → resolution)

     Operations-mode examples are detected by the same
     OPERATIONS_TITLE_KEYWORDS list as Check 10. Technical
     examples are exempt — they may legitimately use words
     like `落地` (e.g., `缓存与预聚合优先落地`) or `闭环`
     (e.g., `修复闭环`) where the user input supports the
     status claim. See test_cases.md 用例 19 PASS (f)/(g) for
     the calibration eval and examples.md "运营状态校准
     mini 对照" for the side-by-side ❌ / ✅ comparison.

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
    # Action / outcome — added for monthly-report submission style
    # (see SKILL.md "二级子论点 > 短判断形态" + style_rules.md §12.14).
    # These let short human-style titles like `安装体验优化` /
    # `数据桥梁建设` / `使用路径前置` / `曝光效率拆分` /
    # `连带分析补充` / `报告主题设计` / `准确性待观察` /
    # `安装文档整理` / `多维度新增` pass check 4(a). They are normal
    # monthly-report verbs, not amp words.
    "优化", "建设", "前置", "拆分", "补充", "设计", "观察",
    "整理", "新增",
    # Action / outcome — operations submission style (§13). Common
    # verbs in merchant / activity / customer-complaint monthly
    # reports: 识别 (identify), 对齐 (align), 梳理 (sort/organize).
    # Let titles like `素材准备节奏对齐` / `报名意愿低商户已识别` /
    # `三类问题完成梳理` / `后续风险提前识别` pass check 4(a).
    "识别", "对齐", "梳理",
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

# Unnatural AI template phrases — stilted machine-generated wording that
# leaks "this was written by an LLM" tone. Forbidden in positive example
# output blocks. Listed in SKILL.md "月报提交模式 > 自然语言度" and
# style_rules.md §12.7. Natural replacements live in §12.8.
#
# Detection rationale (one line each):
#   - 使用门槛下行: should be `降低使用门槛 / 使用门槛降低` (the verb
#     `下行` is for trends like 留存下行, not for thresholds).
#   - 能力获得: should be `形成能力 / 沉淀能力 / 具备 X 能力`.
#   - 数据不可达瓶颈: should be `数据无法对齐 / 业务无法直接取数`
#     with the concrete scenario preserved.
#   - 多项能力初步成型: should be `多个方向均形成阶段性进展` /
#     `各方向按节奏推进`.
#   - 消除瓶颈: an absolute/AI-template claim. Should be `缓解 X 阻力` /
#     `减少 X 协同成本` / `降低 X 门槛`.
#   - 用户不再受操作系统差异困扰: AI-template phrasing that reads as
#     translated marketing copy. Should be `跨端使用条件得到补齐` /
#     `双端可用`.
#   - 多端能力获得: same `能力获得` template trap on the multi-platform
#     case. Should be `双端可用 / 双端可装`.
#   - 流程闭环已达成: stilted absolute claim. Should be
#     `链路初步跑通 / 基本跑通`.
FORBIDDEN_UNNATURAL_PHRASES = [
    "使用门槛下行",
    "能力获得",
    "数据不可达瓶颈",
    "多项能力初步成型",
    "消除瓶颈",
    "用户不再受操作系统差异困扰",
    "多端能力获得",
    "流程闭环已达成",
]

# Unsupported-inference phrases — wording that adds UI behavior /
# adoption status / dependency-removal / automation-level / future
# expansion / business effect / user-feeling / system-capability
# claims that the user did not say. These read plausible in monthly-
# report tone but are *not* in the source. The skill must instead
# use restrained traceable wording that maps back to specific input
# sentences (see SKILL.md "禁止过度推断" / style_rules.md §12.11).
#
# This list mirrors the 7 categories in SKILL.md's inference table
# (UI / 采纳依赖 / 自动化 / 未来扩展 / 业务效果 / 用户感受 / 系统
# 能力). It is curated — explicit AI-template phrases that real
# outputs leak — not an exhaustive enumeration of every possible
# inference.
FORBIDDEN_INFERENCE_PHRASES = [
    # UI / 操作行为
    "自行拖拽查询",      # overshoots "拖字段看简单数据"
    "一键导出",          # AI-template UI claim
    "点击即用",          # AI-template UI claim
    # 采纳 / 依赖状态
    "不再依赖人工中转",   # dependency-removal claim
    "已全员采纳",         # adoption claim
    "数据团队不再承接",   # substring catches "...此类需求" suffix
    # 自动化程度
    "完整自动化闭环",     # absolute automation
    "全流程自动化",       # absolute automation
    "自动化覆盖所有场景", # absolute scope
    # 未来扩展方向 — substrings to catch the doc's whole family of
    # variants: `后续可扩展至更多数据域` / `后续可扩展至货品维度` /
    # `后续可扩展至流量等维度` / `后续可扩展至全公司` etc.
    "后续可扩展至",       # substring; covers `更多数据域` / `货品` /
                          # `流量等维度` / `全公司` and any new variants
    "下季度可推广",       # substring catches "...至全公司" / "...至全部"
    # 业务效果
    "业务效率提升",       # AI-template effect claim (no data)
    "决策速度加快",       # AI-template effect claim
    "提升老板满意度",     # AI-template stakeholder claim
    # 数据 / 瓶颈类
    "消除数据瓶颈",       # `消除[X]瓶颈` family — distinct from
                          # `消除瓶颈` (unnatural list). Use
                          # `缓解 X 数据无法对齐的具体场景`.
    # 用户感受
    "用户不再受系统差异困扰",  # shorter form of the longer
                                # "...操作系统差异困扰" in the
                                # unnatural list — both must fail
    "用户体验明显改善",   # AI-template user-feeling claim
    # 系统能力 — completes the 7-category "禁止过度推断" table in
    # SKILL.md / style_rules.md §12.11. Both are listed verbatim in
    # the doc as ❌ forbidden examples; both claim a system-wide
    # capability the user did not state.
    "Windows 用户可在本地直接执行 ODPS 查询",
    "Agent 可承接所有取数场景",
    # Operations-mode virtual claims — phrases the docs explicitly ban
    # in SKILL.md "运营月报子模式 > 不得虚构" + style_rules.md §13.8 +
    # test_cases.md 用例 16 PASS (i)/(j) and 用例 17 PASS (f) grep
    # patterns. The user's iteration explicitly bans inventing
    # merchant feedback / activity results / business changes /
    # cross-team effects. These are documented as ❌ across multiple
    # files; the validator must catch them too.
    # 商户反馈情绪 / 商户采纳
    "商户满意度",
    # `反响热烈` substring covers all word orders for the documented
    # AI-template merchant-feedback claim:
    #   - 商户反响热烈 (short form)
    #   - 商户对活动反响热烈 (SKILL.md / style_rules.md §13.8 — has
    #     `对活动` infix that breaks substring matching on the short
    #     form)
    #   - 活动反响热烈 / 本月活动反响热烈 / 市场反响热烈 (bare-activity
    #     and other variants the docs imply by example)
    # One substring, full family coverage. See style_rules.md §13.8
    # 商户反馈情绪 row.
    "反响热烈",
    "商户给予正面评价",
    # `高度认可` substring covers all word orders the docs list:
    #   - 商户高度认可 (short form)
    #   - 商户高度认可策略 (style_rules.md §13.8 — suffix variant)
    #   - 商户对策略高度认可 (SKILL.md 商户采纳 row — different word
    #     order with `对策略` infix between `商户` and `高度认可`)
    #   - 商户对活动高度认可 / 老板高度认可 (other variants the
    #     docs imply)
    # One substring, full family coverage.
    "高度认可",
    "商户主动配合",
    "商户已全员报名",
    # 活动效果 / 转化结果
    "活动效果超预期",
    "活动 ROI 创新高",
    "参与率显著提升",
    "转化率明显改善",     # SKILL.md 活动结果 + style_rules.md §13.8
                          # GMV/转化 row — uses `明显改善` not
                          # `明显提升` so amp-word check (Check 7)
                          # doesn't catch it.
    # 业务影响 / 跨团队效果
    "推动品类整体增长",
    "经营改善显著",
    "团队协同效率明显改善",
    "跨团队配合质量大幅提升",
    "商户关系全面改善",
]

# Operations-mode example detection: if the example's `## 示例 N: …`
# title contains any of these keywords, treat it as an operations-mode
# example (运营子模式) and apply check 10 (tech-substrate leakage).
# Technical examples (data / SQL / dashboard / Agent / Skill / model)
# are exempt from this check — they may legitimately use technical
# substrate words.
OPERATIONS_TITLE_KEYWORDS = [
    "商户拜访",
    "商家沟通",
    "活动运营",
    "客诉",
    "门店",
    "招商",
    "走访",
    "拜访",
    "运营月报",
    "运营子模式",
]

# Technical-substrate phrases that should NOT appear in operations-mode
# positive examples. These belong to data / system / model context;
# applying them to merchant / activity / customer-complaint monthly
# reports forces a wrong tone (see SKILL.md "运营月报子模式 > 技术化
# 措辞禁忌" + style_rules.md §13.6). Technical examples are exempt —
# scoping is by the example section title.
#
# This mirrors the full 12-row tech-leakage table in style_rules.md
# §13.6, not just the 6-phrase section-G subset. The natural ops
# replacements are documented next to each ❌ phrase in the same table.
FORBIDDEN_TECH_LEAKAGE = [
    # Core 6 (user's section-G list)
    "数据底座",
    "技术基建",
    "系统能力",
    "链路打通",
    "模型能力",
    "自动化闭环",
    # Doc additions in SKILL.md "技术化措辞禁忌" + style_rules.md §13.6
    "数据连接",   # use `信息对齐` / `跨团队对接`
    "数据采集",   # use `一线反馈收集` / `走访沉淀`
    "接口对接",   # use `跨团队对齐` / `沟通对齐`
    "监控告警",   # use `风险识别` / `重点跟进`
    "调度任务",   # use `推进节奏` / `跟进节点`
    "流程闭环",   # use `处理到位` / `持续推进` / `阶段性完成`
]

# Operations status-upgrade phrases — phrases that overstate the actual
# status of operations work. Three groups, all forbidden in ops-mode
# examples:
#
# Group A — 5 specific failure-mode phrases (user's explicit ban list).
# Each turns a lower status into a higher one without user-input
# support:
#
#   - 活动规则优化       : "对齐" upgraded to "优化"
#   - 规则简化方向明确   : "对齐" upgraded to "decided direction"
#   - 专项跟进流程       : "持续跟进" upgraded to "formal process"
#   - 资源分配方案落地   : "诉求" upgraded to "plan landing"
#   - 推进经营改善       : "反馈沉淀" upgraded to "business improvement"
#
# Group B — 6 hard-forbidden status-upgrade words declared in SKILL.md
# "运营状态校准 > 状态升档禁忌（hard rule）" + style_rules.md §13.10.
# These read as completion claims (`已 ...`, `... 明确`, `形成闭环`)
# and are forbidden in ops-mode positive examples because gold-standard
# outputs should never make completion claims absent input support:
#
#   - 已优化 / 已改善 / 已解决 / 已落地  : status-completion claims
#   - 方向明确                            : decided-direction claim
#   - 形成闭环                            : closure-formed claim
#
# Group C — 8 multi-word ❌ variants documented in the §13.10 "输入意图
# → 校准措辞映射" table (SKILL.md / style_rules.md) and the examples.md
# "运营状态校准 mini 对照" failure-mode column. These do NOT match Group
# B substrings (e.g. `规则完成优化` lacks the `已` prefix; `方向已经明确`
# inserts `已经` between `方向` and `明确` so the substring `方向明确`
# does not hit). Each is enumerated verbatim from the mapping tables:
#
#   - 反馈已闭环          : `形成闭环` family with 已-prefix
#   - 规则完成优化        : alignment overstated as completed optimization
#   - 方案完成落地        : concern overstated as completed landing
#   - 方向已经明确        : alignment overstated as decided direction
#   - 曝光资源完成配置    : concern overstated as completed configuration
#   - 商户参与效果改善    : partial signup overstated as effect improvement
#   - 商户问题完成解决    : feedback overstated as completed resolution
#   - 高频反馈已闭环      : feedback overstated as already closed loop
#
# All three groups scoped to operations-mode examples only (via
# OPERATIONS_TITLE_KEYWORDS) because technical examples may legitimately
# use words like `落地` (e.g. `缓存与预聚合优先落地` in example 3) or
# `闭环` (e.g. `修复闭环` / `根因结论本周内闭环`) where the user input
# supports the status claim. See SKILL.md "运营状态校准" +
# style_rules.md §13.10 + examples.md "运营状态校准 mini 对照" +
# test_cases.md 用例 19 PASS (f)/(g).
FORBIDDEN_OPS_UPGRADE_PHRASES = [
    # Group A: 5 specific failure-mode phrases
    "活动规则优化",
    "规则简化方向明确",
    "专项跟进流程",
    "资源分配方案落地",
    "推进经营改善",
    # Group B: 6 hard-forbidden status-upgrade words
    "已优化",
    "已改善",
    "已解决",
    "已落地",
    "方向明确",
    "形成闭环",
    # Group C: 8 multi-word ❌ variants from the §13.10 mapping table
    # and the examples.md mini-对照 failure-mode column
    "反馈已闭环",
    "规则完成优化",
    "方案完成落地",
    "方向已经明确",
    "曝光资源完成配置",
    "商户参与效果改善",
    "商户问题完成解决",
    "高频反馈已闭环",
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


def extract_example_titles(examples_path: pathlib.Path) -> list[str]:
    """Return the section title (first line after `## 示例`) for each
    example block, in the same order as `extract_positive_blocks`.

    Used by check 10 to detect operations-mode examples by keyword
    matching on titles (see `OPERATIONS_TITLE_KEYWORDS`)."""
    text = examples_path.read_text(encoding="utf-8")
    titles: list[str] = []
    sections = text.split("## 示例")
    for sec in sections[1:]:
        # Only count sections that actually contain a 拉条子改写 block,
        # to keep alignment with extract_positive_blocks.
        if not re.search(r"### 拉条子改写\s*\n", sec):
            continue
        title_match = re.match(r"\s*([^\n]+)", sec)
        if title_match:
            titles.append(title_match.group(1).strip())
        else:
            titles.append("")
    return titles


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
    """If `sj` is **literally** `[Container][TailVerb]` (the entire short
    judgment, with no specifying prefix at all), return (container, verb).

    The original strict rule flagged any `prefix.endswith(cont)` form —
    that was too aggressive: it rejected legitimate human-style monthly
    report titles like `安装链路打通` (where `安装` specifies `链路`
    before the verb).

    The relaxed rule only flags the truly bare `[Container][Verb]`
    shape (e.g. `看板迭代` / `工具链打通` / `工作台落地`). Any
    specifier prefix before the container makes the title rich enough.

    Examples:
      - `看板迭代`         → flagged ([看板][迭代])
      - `工具链打通`       → flagged ([工具链][打通])
      - `经营看板迭代`     → NOT flagged (has 经营 specifier)
      - `安装链路打通`     → NOT flagged (has 安装 specifier)
      - `核心经营看板维度持续补齐` → NOT flagged (补齐 not in tail verbs)
    """
    for verb in TOOL_NAME_TAIL_VERBS:
        if not sj.endswith(verb):
            continue
        prefix = sj[: -len(verb)]
        for cont in TOOL_NAME_CONTAINERS:
            if prefix == cont:
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


def check_unnatural_phrases(blocks: list[str]) -> list[tuple[int, str]]:
    """Flag any positive example block that contains unnatural AI phrases.

    Returns (example_index, phrase)."""
    violations: list[tuple[int, str]] = []
    for i, block in enumerate(blocks, 1):
        for w in FORBIDDEN_UNNATURAL_PHRASES:
            if w in block:
                violations.append((i, w))
    return violations


def check_inference_phrases(blocks: list[str]) -> list[tuple[int, str]]:
    """Flag any positive example block that contains unsupported-inference
    phrases (UI behavior / adoption status / future expansion / automation
    level the user did not state).

    Returns (example_index, phrase)."""
    violations: list[tuple[int, str]] = []
    for i, block in enumerate(blocks, 1):
        for w in FORBIDDEN_INFERENCE_PHRASES:
            if w in block:
                violations.append((i, w))
    return violations


def _is_operations_example(title: str) -> bool:
    """Return True if the example section title indicates operations-mode."""
    return any(kw in title for kw in OPERATIONS_TITLE_KEYWORDS)


def check_ops_tech_leakage(
    blocks: list[str], titles: list[str]
) -> list[tuple[int, str, str]]:
    """For operations-mode examples (detected by title keyword), flag
    technical-substrate phrases that should not appear (the input is
    business / merchant / activity / customer-complaint, not data /
    system / model context).

    Returns (example_index, phrase, title)."""
    violations: list[tuple[int, str, str]] = []
    for i, (block, title) in enumerate(zip(blocks, titles), 1):
        if not _is_operations_example(title):
            continue
        for phrase in FORBIDDEN_TECH_LEAKAGE:
            if phrase in block:
                violations.append((i, phrase, title))
    return violations


def check_ops_upgrade_phrases(
    blocks: list[str], titles: list[str]
) -> list[tuple[int, str, str]]:
    """For operations-mode examples (detected by title keyword), flag
    status-upgrade phrases that overstate the actual work status — e.g.
    aligning written as optimizing, follow-up written as landing.
    Technical examples are exempt because they may legitimately use
    words like `落地` where the input supports the status claim.

    Returns (example_index, phrase, title)."""
    violations: list[tuple[int, str, str]] = []
    for i, (block, title) in enumerate(zip(blocks, titles), 1):
        if not _is_operations_example(title):
            continue
        for phrase in FORBIDDEN_OPS_UPGRADE_PHRASES:
            if phrase in block:
                violations.append((i, phrase, title))
    return violations


def main() -> int:
    print(f"Validating skill at: {SKILL_DIR}")
    print()

    failed = False

    # ---- Check 1: required files ----
    print("[1/11] Required files exist")
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
    print("\n[2/11] No bare field-name labels in positive examples")
    bare = check_bare_labels(blocks)
    if bare:
        print(f"  FAIL: {len(bare)} bare label(s):")
        for ex_idx, fn in bare:
            print(f"    example {ex_idx}: **{fn}：**")
        failed = True
    else:
        print("  OK: zero bare field-name labels")

    # ---- Check 3: forbidden punctuation in second-level titles ----
    print("\n[3/11] No forbidden punctuation in 二级标题 (before 冒号)")
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
    print("\n[4/11] No overly generic 二级标题 "
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
    print("\n[5/11] No process-narration phrases in positive examples")
    proc_violations = check_process_phrases(blocks)
    if proc_violations:
        print(f"  FAIL: {len(proc_violations)} process phrase leak(s):")
        for ex_idx, phrase in proc_violations:
            print(f"    example {ex_idx}: {phrase!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_PROCESS_PHRASES)} forbidden phrases scanned, zero hits")

    # ---- Check 6: placeholder count cap ----
    print(f"\n[6/11] No more than {MAX_PLACEHOLDER_PER_BLOCK} occurrences of "
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
    print("\n[7/11] No 放大型 wording in positive examples "
          "(零门槛 / 大幅 / 明显提升 / 完全打通 / 全自动 / 闭环完成 / 显著 / 极大 / 巨大)")
    amp_violations = check_amplification_words(blocks)
    if amp_violations:
        print(f"  FAIL: {len(amp_violations)} amp word leak(s):")
        for ex_idx, w in amp_violations:
            print(f"    example {ex_idx}: {w!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_AMP_WORDS)} forbidden amp words scanned, zero hits")

    # ---- Check 8: unnatural AI template phrases ----
    print("\n[8/11] No unnatural AI template phrases in positive examples "
          "(使用门槛下行 / 能力获得 / 数据不可达瓶颈 / 多项能力初步成型 / "
          "消除瓶颈 / 用户不再受操作系统差异困扰 / 多端能力获得 / 流程闭环已达成)")
    unnatural_violations = check_unnatural_phrases(blocks)
    if unnatural_violations:
        print(f"  FAIL: {len(unnatural_violations)} unnatural phrase leak(s):")
        for ex_idx, w in unnatural_violations:
            print(f"    example {ex_idx}: {w!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_UNNATURAL_PHRASES)} forbidden unnatural phrases scanned, zero hits")

    # ---- Check 9: unsupported-inference phrases ----
    print("\n[9/11] No unsupported-inference phrases in positive examples "
          "(9 categories: UI / 采纳依赖 / 自动化 / 未来扩展 / 业务效果 / "
          "用户感受 / 数据瓶颈 / 系统能力 / 运营场景虚构)")
    inf_violations = check_inference_phrases(blocks)
    if inf_violations:
        print(f"  FAIL: {len(inf_violations)} inference phrase leak(s):")
        for ex_idx, w in inf_violations:
            print(f"    example {ex_idx}: {w!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_INFERENCE_PHRASES)} forbidden inference phrases scanned, zero hits")

    # ---- Check 10: tech-substrate leakage in operations-mode examples ----
    titles = extract_example_titles(examples_path)
    ops_block_indices = [
        i for i, t in enumerate(titles, 1) if _is_operations_example(t)
    ]
    print(f"\n[10/11] No tech-substrate leakage in operations-mode examples "
          f"(数据底座 / 技术基建 / 系统能力 / 链路打通 / 模型能力 / 自动化闭环 / "
          f"数据连接 / 数据采集 / 接口对接 / 监控告警 / 调度任务 / 流程闭环)")
    print(f"        Operations-mode example indices detected: {ops_block_indices}")
    leak_violations = check_ops_tech_leakage(blocks, titles)
    if leak_violations:
        print(f"  FAIL: {len(leak_violations)} tech-leakage hit(s) in ops examples:")
        for ex_idx, phrase, title in leak_violations:
            print(f"    example {ex_idx} ({title[:40]}...): {phrase!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_TECH_LEAKAGE)} tech-substrate phrases scanned across "
              f"{len(ops_block_indices)} ops example(s), zero hits")

    # ---- Check 11: operations status-upgrade phrases ----
    print(f"\n[11/11] No operations status-upgrade phrases in operations-mode "
          f"examples")
    print(f"        Group A (5 failure-mode phrases): 活动规则优化 / "
          f"规则简化方向明确 / 专项跟进流程 / 资源分配方案落地 / 推进经营改善")
    print(f"        Group B (6 hard-forbidden status words): 已优化 / 已改善 / "
          f"已解决 / 已落地 / 方向明确 / 形成闭环")
    print(f"        Group C (8 multi-word variants): 反馈已闭环 / 规则完成优化 / "
          f"方案完成落地 / 方向已经明确 / 曝光资源完成配置 / 商户参与效果改善 / "
          f"商户问题完成解决 / 高频反馈已闭环")
    print(f"        Operations-mode example indices detected: {ops_block_indices}")
    upgrade_violations = check_ops_upgrade_phrases(blocks, titles)
    if upgrade_violations:
        print(f"  FAIL: {len(upgrade_violations)} status-upgrade hit(s) in ops examples:")
        for ex_idx, phrase, title in upgrade_violations:
            print(f"    example {ex_idx} ({title[:40]}...): {phrase!r}")
        failed = True
    else:
        print(f"  OK: {len(FORBIDDEN_OPS_UPGRADE_PHRASES)} status-upgrade phrases "
              f"scanned across {len(ops_block_indices)} ops example(s), zero hits")

    print()
    if failed:
        print("VALIDATION FAILED")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
