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

Manifests, build, and tests belong to the parent. This tree does not add credentials or private transcripts.
