# sapsynk plugins

Portable, provider-independent skills for teamkit, dyl, and learning. Host-only tools stay in `plugins/*/adapters/HOSTS.md`. Skills do not assume a cloud worker and a native IDE can do the same work. There is no cloud/native parity claim.

Source revision `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Original skill text is MIT-licensed upstream. Parent build bundles it. Plugins keep contained links `../../upstream/...` and do not vendor a second framework copy. See `THIRD_PARTY_NOTICES.md`.

## Plugins

| Plugin | Skill | What stays portable |
| --- | --- | --- |
| `sapsynk-teamkit` | `verify-this` | Six baseline/treatment/verdict steps. Prefer project `verify-vao`. |
| `sapsynk-dyl` | `dyl-review` | Quick: one worker, ≤7 evidence asks, no post or merge. pstack routes the model. Deep unavailable until thermos, Bugbot, and the four-reviewer panel are qualified. Panel count stays four. |
| `sapsynk-dyl` | `principle-the-algorithm` | Five steps, then rerun. Cannot drop approved consent, tenant, or acceptance requirements. Host authority and progress stay. |
| `sapsynk-learning` | `continual-learning` | Candidate, approval, promotion, rollback via bundled `scripts/memory.py`. No hooks. No transcript scanning. Reviewed structured user preferences only. No secret-sanitization guarantee. |

## Build and use

Run `python3 tools/build.py` and `python3 -m unittest discover -s tests -q`. The build verifies all pinned source hashes and creates three deterministic private plugin archives in `dist/`. The native catalog is `.agents/plugins/marketplace.json`; each package has a portable manifest and a Codex compatibility manifest.

Use pstack's selected roles for workers. Grok is an external official CLI worker, with actual private receipts retained separately from source. These packages do not copy pstack or introduce a second broker. Cloud publication and native installation are separate operations from storing this repository in GitHub.

The memory script is qualified on POSIX Linux only. Add `*.sapsynk-memory/` to each target project's Git exclusions before using it. Keep reviewed inputs, candidates and execution evidence private. No credentials or private transcripts belong in this repository.

## Persistent Codex source

Canonical public source is [builder-sapsynk/sapsynk-plugins](https://github.com/builder-sapsynk/sapsynk-plugins). Each plugin remains independently selectable. The reviewed 0.1.0 packages are pinned to source commit `8d662ae823ca8bba497c3dc56975eb04bf03eeaf`.

```sh
codex plugin marketplace add https://github.com/builder-sapsynk/sapsynk-plugins.git --ref 8d662ae823ca8bba497c3dc56975eb04bf03eeaf
codex plugin add sapsynk-teamkit@sapsynk-tools
codex plugin add sapsynk-dyl@sapsynk-tools
codex plugin add sapsynk-learning@sapsynk-tools
```

If this marketplace was previously added from a local directory, remove only `sapsynk-tools` before adding its Git source. Project policy and exact package pins govern applicable workflows. Account cloud plugin publication is separate from Git installation; public source does not automatically make private account releases public.
