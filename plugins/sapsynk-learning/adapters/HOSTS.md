# Hosts — sapsynk-learning

Portable skill: `skills/continual-learning`. Persistence goes through the bundled `skills/continual-learning/scripts/memory.py` after the parent build. This plugin does not copy another memory framework. Other originals in this repo stay linked under [../../upstream/](../../upstream/).

## Portable

Explicit steps only: candidate, approval, promotion, rollback. Input is a reviewed structured user preference. No automatic hooks. No transcript or session scanning. Unapproved candidates stay inactive.

Do not claim `memory.py` sanitizes secrets. Keep secrets out of preference records.

## Native (host-dependent)

Host auto-memory, hook installers, and transcript indexers are native features. This skill does not turn them on and does not wrap them.

## Parity

No cloud/native parity claim. Where a preference file lives, and whether a host injects it into the next session, depends on that host. Promotion here only updates state through `memory.py`.
