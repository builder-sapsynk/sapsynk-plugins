# Qualification

The three packages preserve 55 original files from cursor/plugins at e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a. Source inventory and file hashes are verified before every build. Deterministic archive and contained-link tests pass.

13 behavioral and package tests pass on POSIX Linux. The memory suite exercises exact outside-section policy preservation, explicit digest approvals, project/speaker checks, stale hashes, locks, replay/corrections, interrupted subprocess recovery, injected ledger/receipt/rollback/directory-sync failures and retry. An independent Sol review reproduced the original failures and verified repairs, including rejection of external edits during recovery. The packaged memory script matches its reviewed source.

`python3 qualification/verify_learning.py` compares the original implementation at99c5d0f and the repaired source against identical synthetic fixtures. Baseline fails policy preservation after a ledger-write failure and resurrects an obsolete preference on replay; treatment passes both cases. This is a behavioral comparison, not a performance benchmark.

Grok4.7 wrote the workflow adapters and initial memory tool in separately verified jobs. A prior combined job was cancelled without edits and remains in private receipts. Parent integration fixed reviewed faults; it does not erase that failure or claim every delegated output was correct initially.

Original Cursor hook delivery, Windows promotion, deep Dyl panel dependencies, connected Codex app API parity and real VAO application behavior remain unqualified. No automatic hooks or customer-data access are enabled. Native installation and private cloud save are tracked separately in the workspace handoff.
