# Learning host mapping

The explicit workflow is provider-independent. The [Python script](../scripts/memory.py) is qualified on this POSIX Linux host using kernel file locks, atomic replacements and directory fsync. Windows execution has not been qualified. Keep candidate/review steps portable; qualify an appropriate file-lock implementation before enabling promotion on another host.

No hooks, transcript scanning or host auto-memory are enabled. Operators supply reviewed structured records. Promotion writes only the selected AGENTS memory section and private `<AGENTS.md>.sapsynk-memory/` state. Receipts, backups, candidates and record inputs are private; add the state pattern to project Git exclusions. Other AGENTS bytes remain intact.

A pending journal restores the recorded prior state before a retry. External changes that match neither recorded state cause a conflict rather than an overwrite. Kernel locks release when a process exits. Known-secret detection is incomplete, so exact candidate review remains required.

The complete [original Continual Learning source](../upstream/continual-learning/) is bundled unchanged. Automatic updater behavior is replaced by reviewed candidate promotion, an explicit behavioral deviation. No Codex/Grok/native hook or automatic persistence parity is claimed.
