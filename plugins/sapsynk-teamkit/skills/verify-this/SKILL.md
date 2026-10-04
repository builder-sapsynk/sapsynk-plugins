---
name: verify-this
description: "Verify a claim with fresh local evidence: restate it falsifiably, capture baseline and treatment, compare artifacts, and return VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Prefer the project's verify-vao when it exists."
---

# Verify This

Verification proves or disproves one claim. It is not a recap. Original: [verify-this](../../upstream/teamkit/skills/verify-this/SKILL.md) (parent build bundles source).

Use the project's pinned Sapsynk pstack contract, Poteto Mode and role configuration. Read this plugin's [host mapping](../../adapters/HOSTS.md). Installation does not activate hooks or grant tools.

## When

Use for "verify this", "prove it works", "did this fix it", or "show me the evidence", including a before/after bug repro or a UI, CLI, API, performance, or memory measurement. If the claim is not measurable ("cleaner"), ask for a metric first.

## Workflow

Leave these six steps in order:

1. Restate the claim in falsifiable form: condition, metric, and threshold.
2. Pick the smallest local surface that can disprove it. Prefer the project's `verify-vao` when that surface exists. Otherwise use a focused test, minimal repro, local request/response, timing, or heap snapshot.
3. Capture a baseline from the old state (merge base, parent, failing branch, or current broken repro).
4. Capture treatment from the changed state with the same command, data, warmup, and environment.
5. Compare raw artifacts (numbers, transcripts, responses, profiles, snapshots, or test output).
6. Return exactly one verdict: `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`.

`VERIFIED`: baseline and treatment differ in the predicted direction by the claimed threshold, with no obvious confound. `NOT VERIFIED`: unchanged, wrong direction, or missed threshold. `INCONCLUSIVE`: no valid baseline, noise, failed measurement, or an environment mismatch. Do not soften a negative result.

## Output

```text
VERIFIED | NOT VERIFIED | INCONCLUSIVE
Claim: <falsifiable claim>
Evidence: <metric>: baseline=<...>, treatment=<...>, delta=<...>, threshold=<...>
Reasoning: <one paragraph naming evidence and confounds>
```

Keep evidence inline. Do not write prompts, secrets, screenshots, HTTP bodies, or heap dumps to disk unless the user agrees. Host browser or UI capture is native and optional. This skill does not claim cloud and native hosts produce the same artifacts.
