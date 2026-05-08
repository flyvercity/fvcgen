# Documentation Review — 2026.05.08

## High Priority

[x] README.md: Fix linter reference (flake8 → ruff)
[x] README.md: Update config YAML example to include `name` on origins, `transmission_delay`, `include_origin`
[x] README.md + SPECIFICATION.md: Document actual output record structure (nested `time.unix`/`time.rx`, `uaid.int`, `pos.loc`)
[x] SPECIFICATION.md: Add `transmission_delay` feature (mean/std_dev delay, `rx` field in output, sorting by rx)

## Medium Priority

[x] README.md: Add Installation section (CodeArtifact + pip install)
[x] README.md: Document `--verbose` and `--version` CLI flags
[ ] README.md: Document hierarchical defaults merge (general → origin → object)
[ ] README.md: Document multiple IDs per object (`id` accepts string or list)
[ ] SPECIFICATION.md: Mark "Smooth Transitions" (§2) as not yet implemented
[ ] SPECIFICATION.md: Add `include_origin` option and `name` field on origins

## Low Priority

[ ] README.md: Add link to CHANGELOG
[ ] docs/IMPLEMENTATION_SUMMARY.md: Remove (stale, duplicates README, shows old output format)
[ ] SPECIFICATION.md: Note simplified error propagation vs. spec's tangent-frame approach
