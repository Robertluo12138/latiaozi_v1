# Changelog

All notable changes to `latiaozi_v1` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/), and the project uses semantic versioning.

## [0.1.0] — 2026-04-28

Initial release.

### Added
- `skill/SKILL.md` — entry with YAML frontmatter, three-layer output structure, business-value-language conversion rules, mini worked example.
- `skill/references/style_rules.md` — 9-section rule book covering layered structure, short-judgment constraints, four-element body, missing-data handling, tone, and length caps.
- `skill/references/examples.md` — six worked scenarios (data analysis / SQL build / BI dashboard / monthly report / project recap / business diagnosis) plus a label-conversion lookup table.
- `skill/references/checklist.md` — 12-item pre-output self-check.
- `skill/evals/test_cases.md` — eight evaluation cases including sparse-input and length-stress tests.
- `scripts/validate_skill.py` — stdlib-only validator (file-presence + bare-label scan + forbidden-punctuation scan over positive example blocks).
- `scripts/package_skill.py` — stdlib-only packager that builds `dist/latiaozi_v1.zip` from the **contents** of `skill/` (no wrapper directory).
- Top-level `README.md`, `LICENSE` (MIT), `.gitignore`.
