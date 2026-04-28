# latiaozi_v1

A portable Claude **Skill** that rewrites rough Chinese work summaries — monthly reports, weekly updates, project recaps, BI dashboard rollouts, SQL/build progress, business diagnostics — into Alibaba-style "拉条子" (latiaozi): the structured, conclusion-first writing format preferred by managers in their pre-meeting scan.

This repo distributes the skill as a self-contained zip importable into desktop agents that support skill import.

---

## What this skill does

Given a piece of rough Chinese work-summary text, the skill produces output that strictly follows three layers:

1. **Top-level claim** (1, bold) — one sentence of overall judgment.
2. **First-level claims** (3–5, bold) — each a conclusion-style sentence.
3. **Second-level sub-claims** (2–4 each) — each formatted as:

   ```
   **[short judgment, no punctuation]：** fact + data + explanation + judgment
   ```

Hard rules enforced by the skill:

- The short judgment before the colon must not contain `,` `.` `;` `，` `。` `；` `、`.
- Bare field-name labels (`**GMV：**`, `**订单：**`, `**SQL：**`, `**看板：**`, `**数据集：**`) are forbidden.
- Numbers may not be invented; missing data is replaced by `待补充：XX数据`.
- Execution language ("built a wide table") is rewritten as business-value language ("wide table online to support multi-dimensional analysis").
- No exclamation marks, no client-meeting filler, no口语 ("我们觉得 / 大概 / 差不多").

---

## When to use it

Trigger phrases (Chinese):

- "改成拉条子"
- "用阿里风格改写"
- "结论先行" / "结构化重写"
- "管理者风格" / "老板要看的"

Suitable inputs: monthly reports, weekly/bi-weekly updates, project recaps, data analysis conclusions, SQL & dataset/build progress, BI dashboard rollouts, business diagnostics, KPI explanations.

Six worked scenarios are in `skill/references/examples.md`.

---

## Folder structure

```
latiaozi_v1/
├── README.md                  # this file
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── skill/                     # the actual skill — this is what gets packaged
│   ├── SKILL.md               # entry, YAML frontmatter, rules summary
│   ├── references/
│   │   ├── style_rules.md     # 9-section rule book
│   │   ├── examples.md        # 6 worked scenarios + label conversion table
│   │   └── checklist.md       # 12-item pre-output self-check
│   └── evals/
│       └── test_cases.md      # 8 evaluation cases
├── scripts/
│   ├── validate_skill.py      # lints skill/ for compliance (stdlib only)
│   └── package_skill.py       # builds dist/latiaozi_v1.zip (stdlib only)
└── dist/
    └── latiaozi_v1.zip        # generated artifact (run package script)
```

---

## How to validate

The validator checks:

1. All required files exist under `skill/`.
2. Positive example outputs (the "拉条子改写" sections in `examples.md`) contain no bare `**FIELD：**` labels.
3. No second-level title before the colon contains forbidden punctuation.
4. **Warning (non-blocking):** No second-level title is overly generic — flagged if it is ≤ 5 Chinese characters with no judgment/trend/action word (`增长`, `提升`, `下滑`, `承压`, …) **or** ends in a placeholder suffix (`情况`, `数据`, `工作`, `现状`, `概况`).

```bash
python3 scripts/validate_skill.py
```

Exits 0 on success, 1 on failure. Warnings do not affect the exit code. Standard library only — no dependencies.

---

## How to package

The packager runs the validator first, then zips the **contents** of `skill/` into `dist/latiaozi_v1.zip`:

```bash
python3 scripts/package_skill.py
```

After unzipping `dist/latiaozi_v1.zip`, the root contains:

```
SKILL.md
references/
evals/
```

It does NOT contain a wrapping `skill/` or `.claude/` directory — the wrapper is intentionally stripped so the zip imports cleanly.

---

## How to import the zip into a desktop agent

Most desktop agents that support Claude Skills accept either a folder or a zip whose root contains `SKILL.md`. Generic flow:

1. Open your desktop agent's **Skills** / **Plugins** / **Extensions** panel.
2. Choose **Import skill** (or "Add skill" / "Load skill from zip").
3. After running the package script, select `dist/latiaozi_v1.zip`.
4. Confirm. The agent reads `SKILL.md`'s YAML frontmatter and registers the skill under name `ali-latiao-writing`.

If your agent imports from a folder rather than a zip, point it at the `skill/` directory directly.

---

## How to test the skill with example prompts

After import, paste any of the following prompts to confirm activation and observe the output format.

**Test 1 — full-data monthly report**

> 把下面这段月报改成拉条子风格：
> 三月 GMV 1.2 亿，环比 +10%。订单 80 万，环比 +4%。客单价提升了。新客投入做了不少，留存还需要观察。库存周转有点慢了。下个月重点搞留存和库存。

Expected: 3–5 first-level claims, each second-level title 8–18 chars without forbidden punctuation, placeholders only where the original lacks numbers.

**Test 2 — sparse input (placeholder behavior)**

> 用阿里风格改写：这个月感觉还行，GMV 涨了一些，订单也涨了。下月继续。

Expected: every missing number replaced by `待补充：XX数据`; no fabricated figures.

**Test 3 — execution-heavy SQL/build progress**

> 重写为管理者风格：本周建了订单宽表，跑了一些 SQL，修了 GMV 重复计算的 bug。

Expected: short judgments rewritten as business-value statements (e.g. `订单宽表上线支撑多维分析`), not field-name labels.

**Test 4 — single-line business diagnosis**

> 拉条子格式，老板要看的：转化率最近两周掉了，详情页跳出率上来了。

Expected: total claim mentions root cause hypothesis + priority action; no `**转化率：**` field-name label.

More cases in `skill/evals/test_cases.md`.

---

## Releases

If a release is published, download the prebuilt zip from the GitHub **Releases** tab. Otherwise, clone the repo and run `python3 scripts/package_skill.py` — the result is identical.

---

## Appendix: optional Claude Code local installation

If you use the Claude Code CLI, you can also load this skill locally without the zip:

```bash
mkdir -p ~/.claude/skills/ali-latiao-writing
cp -R skill/* ~/.claude/skills/ali-latiao-writing/
```

Restart Claude Code; the skill becomes available globally. (Project-scoped install: `<project>/.claude/skills/ali-latiao-writing/`.)

This local path is provided for convenience only — the canonical distribution path is the zip in `dist/`.

---

## Privacy

This skill ships only writing rules and synthetic examples. It contains no real company data, no internal URLs, no credentials, no personal information. The "GMV" / "订单" figures in `skill/references/examples.md` are illustrative numbers used purely to teach format.

---

## License

MIT — see `LICENSE`.
