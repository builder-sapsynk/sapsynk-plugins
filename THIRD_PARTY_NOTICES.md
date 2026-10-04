# Third-party notices

## Upstream skills

Revision: `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`

License: MIT

The parent build bundles upstream source. Plugin skills link to it with contained `../../upstream/...` paths and do not replace those files with rewritten copies.

All 55 pinned original files are preserved, including assets, source scripts and MIT licenses. The adapted skills refer to these originals:

- `upstream/teamkit/skills/verify-this/SKILL.md` (teamkit)
- `upstream/dyl/skills/dyl-review/SKILL.md` (dyl)
- `upstream/dyl/skills/principle-the-algorithm/SKILL.md` (dyl; five-step process adapted from Elon Musk's engineering process, as stated in that skill)

MIT attribution: copyright remains with the upstream authors. This distribution keeps the license and this notice. No additional copyright claim is made over the original wording.

## Deviations in the portable skills

- `verify-this`: same six steps and verdicts. Prefers the project's `verify-vao` surface. Drops host-specific `control-ui` / `control-cli` as required steps. No cloud/native parity claim.
- `dyl-review`: quick path is one worker, at most seven evidence asks, never posts or merges, and leaves the model to pstack routing. Deep review is visibly unavailable until thermos, Bugbot, and the original four reviewers are qualified. The panel count stays four. Forge CLIs, worktrees, thermos, and Bugbot are native host capabilities, not portable steps.
- `principle-the-algorithm`: order unchanged. The portable skill refuses to delete approved consent, tenant, or acceptance requirements, and it keeps standing host authority and progress reporting. pstack leaves are optional native hints.
- `continual-learning`: portable lifecycle only (candidate, approval, promotion, rollback) through bundled `scripts/memory.py`. No automatic hooks and no transcript scanning. Only reviewed structured user-preference input. This notice does not assert that the script sanitizes secrets.

Provider-independent text is the skill behavior above. Native host capabilities are listed in each plugin `adapters/HOSTS.md`. Those capabilities are not promised on every cloud or local host.
