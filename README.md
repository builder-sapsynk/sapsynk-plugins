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

Run `python3 tools/build.py` and `python3 -m unittest discover -s tests -q`. The build verifies all pinned source hashes and creates three deterministic private plugin archives in `dist/`. The Codex catalog is `.agents/plugins/marketplace.json` and the Claude Code catalog is `.claude-plugin/marketplace.json`; each package has a portable manifest plus Codex and Claude Code manifests. The build writes the Claude Code files from the portable identity.

Use pstack's selected roles for workers. Grok is an external official CLI worker, with actual private receipts retained separately from source. These packages do not copy pstack or introduce a second broker. Cloud publication and native installation are separate operations from storing this repository in GitHub.

The memory script is qualified on POSIX Linux only. Add `*.sapsynk-memory/` to each target project's Git exclusions before using it. Keep reviewed inputs, candidates and execution evidence private. No credentials or private transcripts belong in this repository.

## Persistent Codex source

Canonical public source is [builder-sapsynk/sapsynk-plugins](https://github.com/builder-sapsynk/sapsynk-plugins). Each plugin remains independently selectable. The reviewed 0.1.0 packages are pinned to source commit `8d662ae823ca8bba497c3dc56975eb04bf03eeaf`. Version 0.1.1 adds the Claude Code manifests and host notes; the skills and the memory script are unchanged. Consuming projects pin its exact commit in `.pstack/plugins.lock.json`.

```sh
codex plugin marketplace add https://github.com/builder-sapsynk/sapsynk-plugins.git --ref 8d662ae823ca8bba497c3dc56975eb04bf03eeaf
codex plugin add sapsynk-teamkit@sapsynk-tools
codex plugin add sapsynk-dyl@sapsynk-tools
codex plugin add sapsynk-learning@sapsynk-tools
```

If this marketplace was previously added from a local directory, remove only `sapsynk-tools` before adding its Git source. Project policy and exact package pins govern applicable workflows. Account cloud plugin publication is separate from Git installation; public source does not automatically make private account releases public.

## Claude Code

```sh
claude plugin marketplace add /path/to/pinned/sapsynk-plugins
claude plugin install sapsynk-teamkit@sapsynk-tools
claude plugin install sapsynk-dyl@sapsynk-tools
claude plugin install sapsynk-learning@sapsynk-tools
```

Use a clean checkout of the pinned commit: Claude Code loads a directory marketplace in place. A project bound to pstack 0.2.0 or later restores these from its `.pstack/plugins.lock.json` with `scripts/bootstrap-pstack --host claude-code` and verifies the locked file digests. Each plugin loads its selected skills only. Every skill is explicit (`/sapsynk-dyl:dyl-review` and so on) and none runs on its own. The original hooks, agents and rules under `upstream/` are not at a plugin root, so Claude Code does not load them. See each plugin's `adapters/HOSTS.md` for what the host does and does not provide.
