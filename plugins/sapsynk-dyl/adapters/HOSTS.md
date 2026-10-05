# Hosts for sapsynk-dyl

Portable skills: `skills/dyl-review`, `skills/principle-the-algorithm`. Originals (parent bundles source):

- [../upstream/dyl/skills/dyl-review/SKILL.md](../upstream/dyl/skills/dyl-review/SKILL.md)
- [../upstream/dyl/skills/principle-the-algorithm/SKILL.md](../upstream/dyl/skills/principle-the-algorithm/SKILL.md)

## Portable

- Quick review is one worker, at most 7 evidence-backed asks, and a 🟢/🟡/🔴 draft. Never post or merge.
- Model choice stays on pstack routing. Do not pin a cheap or fast model.
- Deep is unavailable until the host qualifies thermos, Bugbot, and the original four reviewers. Panel count stays four. Do not run a partial panel.
- The algorithm order is fixed. Approved consent, tenant, and acceptance requirements stay. Standing host authority and progress reporting stay.

## Native (host-dependent)

`gh` / `origin` PR commands, throwaway worktrees, thermos subagents, Bugbot, and pstack principle leaves are native. If they are absent, say so. Do not invent their output.

## Parity

No cloud/native parity claim. A host without Bugbot or thermos cannot complete deep review. Quick review is the portable path.

## Claude Code

Install `sapsynk-dyl@sapsynk-tools` from this repository's `.claude-plugin/marketplace.json`, then invoke `/sapsynk-dyl:dyl-review` or `/sapsynk-dyl:principle-the-algorithm`. The one quick-review worker is the role pstack resolves: a native subagent, or a Codex or Grok worker through the project's `scripts/pstack-run` in read mode. `gh` supplies PR context. Deep review stays unavailable: Bugbot and thermos are not Claude Code tools. The original `dyl-agent` under `upstream/` is not loaded.
