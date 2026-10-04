---
name: principle-the-algorithm
description: "Apply before a non-trivial change: make the requirement less dumb, delete, optimize, accelerate, automate, then rerun. Name the requirement you questioned and what you deleted. Do not remove approved consent, tenant, or acceptance requirements."
disable-model-invocation: true
---

# The Algorithm

Five steps, in this order, for any change bigger than an edit you can see at a glance. Each step is cheap only after the previous one. Original: [principle-the-algorithm](../../upstream/dyl/skills/principle-the-algorithm/SKILL.md).

1. **Make the requirement less dumb.** It comes from a person, not a department. A ticket, linter, reviewer, or "the old code" is a source, not a reason. If you disagree with the reasoning, do not accept it. No is a valid outcome.
2. **Delete** the part, flag, layer, retry, or step before optimizing it. If you never add anything back, you did not delete enough.
3. **Optimize** what survived. One part should do many jobs. Look hardest at boundaries where a wrapper wraps a wrapper.
4. **Accelerate.** Walk one change through edit, build, check, and review and tighten the wait.
5. **Automate** last. Volume alone does not justify it. Precision and reviewability do.

**Run it again** on the result before you ship.

## Standing limits

Do not delete or waive an approved consent, tenant isolation, or acceptance requirement. Those stay even when they look slow or redundant. Standing host authority and progress reporting also stay. Question them with the owner, and leave them in place until that owner changes the approval.

pstack leaves in the original (`principle-subtract-before-you-add`, laziness, reader load, verifiable units, build-the-lever) are native routing hints. Use them only when this host actually provides those leaves. Do not invent a second framework copy.

## Tell

Name the requirement you made less dumb, who owned it, and what you deleted. A citation with neither means you skipped the algorithm. Say when a consent, tenant, acceptance, authority, or progress rule was challenged and kept.
