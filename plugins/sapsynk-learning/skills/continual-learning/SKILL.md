---
name: continual-learning
description: "Retain reviewed project preferences through explicit candidates, digest approval, promotion and receipt-bound rollback. No automatic transcript scanning or hooks."
disable-model-invocation: true
---

# Continual learning

Use the project's pinned Sapsynk pstack contract, Poteto Mode and role configuration. Read the [host mapping](../../adapters/HOSTS.md). The complete [original source](../../upstream/continual-learning/skills/continual-learning/SKILL.md) remains bundled separately.

Accept only operator-reviewed structured records with `id`, `speaker: user`, `project`, `source` and `text`. An explicit `supersedes` ID corrects a prior fact. Do not scan transcripts, read caller data or install automatic hooks. Known-secret patterns are rejected; this does not prove that arbitrary records contain no secrets. The operator reviews the exact candidate before promotion.

## Use

Use the bundled [memory script](../../scripts/memory.py) on a qualified host. Keep records, candidates and receipts in a private ignored project directory. Ignore `*.sapsynk-memory/` in the project's Git configuration before use. The state includes preference text and must stay out of Git.

1. Create a candidate with `python3 <plugin>/scripts/memory.py candidate --project <project-id> --agents <AGENTS.md> --records <records.json> --output <candidate.json>`. This prints its SHA256 and changes no AGENTS policy.
2. Review the candidate and approve its exact SHA256. Source speaker labels are supplied data, not independently authenticated user identities.
3. Promote with `python3 <plugin>/scripts/memory.py promote --candidate <candidate.json> --approve <candidate-sha256>`. The script rejects stale AGENTS hashes, conflicting IDs and correction cycles. A transaction journal supports retry after interrupted writes; success is acknowledged only after AGENTS, ledger and receipt are written.
4. Roll back the whole promotion with `python3 <plugin>/scripts/memory.py rollback --receipt <receipt.json> --approve <receipt-sha256>`. The receipt lives under `<AGENTS.md>.sapsynk-memory/receipt-<first-16-candidate-digest-characters>.json`. Rollback restores the exact prior bytes and preference history. It cannot remove one ID from a batch. A later AGENTS change requires a newly reviewed operation.

Approval can be supplied by the coordinator only when the owner already authorized the exact candidate or rollback. An approved source-data scope does not approve every candidate it produces. Preserve unrelated project policies. Report unavailable host capabilities and unresolved contradictions; do not silently alter requirements.
