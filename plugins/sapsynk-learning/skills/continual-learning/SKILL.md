---
name: continual-learning
description: "Record a reviewed structured user preference as a candidate, then approve, promote, or roll it back with bundled scripts/memory.py. No automatic hooks and no transcript scanning."
disable-model-invocation: true
---

# Continual learning

Store only a preference the user has already stated in structured form and that a person has reviewed. Do not scan transcripts, session logs, or private caller data. Do not install hooks. Nothing is written or promoted automatically.

Use the bundled script next to this skill after the parent build: `scripts/memory.py`. Do not copy a second memory framework into the plugin.

## Lifecycle

Run these as separate explicit steps. Stop after each one and wait for the user.

1. **Candidate.** Add one reviewed preference record (stable id, statement, scope, source note). Reject free-form dumps, secrets, and anything not a user preference.
2. **Approval.** A person approves or rejects that candidate. Unapproved candidates do not affect later sessions.
3. **Promotion.** Promote only an approved candidate into the active preference set.
4. **Rollback.** Remove a promoted preference by id and restore the previous active set. Say what was removed.

Pass only the structured fields the script already accepts. Do not pipe chats, credentials, or raw tool logs into it.

## Limits

This skill does not claim the script sanitizes secrets. Do not put secrets in a preference. If a record might contain one, stop and ask the user to redact it before candidate creation.

Host memory UIs and auto-memory hooks are native features. They are not this skill, and this package does not claim cloud and native hosts persist the same way.

Originals for the other bundled skills stay at `../../upstream/` after the parent build. This skill is the portable lifecycle above. It does not vendor an upstream copy.
