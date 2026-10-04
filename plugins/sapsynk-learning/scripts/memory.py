"""Guarded project engineering memory.

Operator-reviewed records only. This module never scans transcripts or infers
paths. Known secret patterns are rejected; that cannot guarantee that a
generic secret is absent. Promotion and rollback are explicit and hashed.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import hmac
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

MEMORY_START = "<!-- sapsynk-memory:start -->"
MEMORY_END = "<!-- sapsynk-memory:end -->"
_START_B = MEMORY_START.encode("ascii")
_END_B = MEMORY_END.encode("ascii")
_FIELDS = ("id", "speaker", "project", "source", "text")
_ALLOWED = set(_FIELDS) | {"supersedes"}
_SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|sk-(?:proj-|ant-)?[A-Za-z0-9_\-]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|\b(?:api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*\S+",
    re.IGNORECASE,
)
_UNSAFE = re.compile(
    r"ignore (?:all |any )?(?:previous|prior|above) (?:instructions|rules|prompts)"
    r"|disregard (?:the )?(?:agents|safety|policy|protected)"
    r"|override (?:the )?(?:protected|safety|system) (?:rules|policy|instructions)"
    r"|disable (?:all )?(?:safety|guardrails|protections)"
    r"|do not follow (?:the )?(?:agents|policy|rules)",
    re.IGNORECASE,
)


class MemoryError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def state_dir_for(agents_path):
    path = Path(agents_path).resolve()
    return path.parent / (path.name + ".sapsynk-memory")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _chmod(path, mode):
    os.chmod(path, mode)


def _read(path):
    return Path(path).read_bytes()


def _json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _atomic_write(path, data, mode):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-mem-")
    try:
        with os.fdopen(fd, 'wb', closefd=False) as output:
            output.write(data)
            output.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    _sync_dir(path.parent)


def _sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _approve(actual, given):
    given = (given or "").strip().lower()
    if len(given) != 64 or any(c not in "0123456789abcdef" for c in given):
        raise MemoryError("approve_mismatch", "approval is not a sha256")
    if not hmac.compare_digest(actual, given):
        raise MemoryError("approve_mismatch", "approval does not match bytes")


def _check_markers(data):
    starts = data.count(_START_B)
    ends = data.count(_END_B)
    if starts == 0 and ends == 0:
        return
    if starts != 1 or ends != 1 or data.find(_START_B) > data.find(_END_B):
        raise MemoryError("marker", "AGENTS memory markers are not a single section")


def _check_record(rec, project):
    if not isinstance(rec, dict) or set(rec) - _ALLOWED:
        raise MemoryError("bad_records", "record shape must be id,speaker,project,source,text")
    for key in _FIELDS:
        value = rec.get(key)
        if not isinstance(value, str) or not value.strip():
            raise MemoryError("bad_records", f"missing {key}")
    if rec["speaker"] != "user":
        raise MemoryError("bad_speaker", "speaker must be user")
    if rec["project"] != project:
        raise MemoryError("bad_project", "record project does not match")
    sup = rec.get("supersedes")
    if sup is not None and (not isinstance(sup, str) or not sup.strip()):
        raise MemoryError("bad_records", "invalid supersedes")
    if sup == rec["id"]:
        raise MemoryError("conflict", "record cannot supersede itself")
    blob = rec["text"] + "\n" + rec["source"]
    if MEMORY_START in blob or MEMORY_END in blob:
        raise MemoryError("unsafe", "record injects a memory marker")
    if _SECRET.search(blob):
        raise MemoryError("secret", "known secret pattern; operator review cannot be skipped")
    if _UNSAFE.search(blob):
        raise MemoryError("unsafe", "protected-rule override")


def _core(rec):
    return {key: rec[key] for key in _FIELDS}


def _store(rec):
    out = _core(rec)
    if rec.get("supersedes"):
        out["supersedes"] = rec["supersedes"]
    return out


def _normalize(project, records):
    if not isinstance(records, list) or not records:
        raise MemoryError("bad_records", "records must be a non-empty list")
    seen = {}
    for rec in records:
        _check_record(rec, project)
        prev = seen.get(rec["id"])
        if prev is not None and prev != rec:
            raise MemoryError("conflict", f"conflicting id {rec['id']}")
        seen[rec["id"]] = rec
    targets = {}
    for rec in seen.values():
        sup = rec.get("supersedes")
        if not sup:
            continue
        if sup in targets:
            raise MemoryError("conflict", f"multiple corrections for {sup}")
        targets[sup] = rec["id"]
    return [seen[key] for key in sorted(seen)]


def _merge(history, incoming):
    by_id = {rec['id']: _store(rec) for rec in history}
    for rec in incoming:
        previous = by_id.get(rec['id'])
        if previous is not None and previous != _store(rec):
            raise MemoryError('conflict', 'record id was already used differently')
        by_id[rec['id']] = _store(rec)
    retired = {}
    for rec in by_id.values():
        target = rec.get('supersedes')
        if target is None:
            continue
        if target not in by_id:
            raise MemoryError('missing_supersede', 'correction target is unknown')
        if target in retired and retired[target] != rec['id']:
            raise MemoryError('conflict', 'correct the current fact, not a retired id')
        retired[target] = rec['id']
    for identifier in by_id:
        visited = set()
        current = identifier
        while current is not None:
            if current in visited:
                raise MemoryError('conflict', 'correction cycle')
            visited.add(current)
            current = by_id[current].get('supersedes')
    history = [by_id[key] for key in sorted(by_id)]
    return [rec for rec in history if rec['id'] not in retired], history


def _restore_ledger(path, ledger):
    if ledger is None:
        path.unlink(missing_ok=True)
    else:
        _atomic_write(path, _json_bytes(ledger), 0o600)


def _recover(state, agents):
    journal_path = state / 'pending.json'
    if not journal_path.exists():
        return
    journal = json.loads(_read(journal_path))
    current = _sha(_read(agents))
    if current not in (journal['before_sha256'], journal['after_sha256']):
        raise MemoryError('stale', 'interrupted update conflicts with external AGENTS changes')
    ledger_path = state / 'ledger.json'
    ledger = _load_ledger(ledger_path)
    if ledger not in (journal['ledger_before'], journal['ledger_after']):
        raise MemoryError('stale', 'interrupted update conflicts with external ledger changes')
    _atomic_write(agents, base64.b64decode(journal['before_bytes']), journal['mode'])
    _restore_ledger(ledger_path, journal['ledger_before'])
    journal_path.unlink()
    _sync_dir(state)


def _commit(state, agents, before, after, ledger_before, ledger_after, receipt_path=None, receipt=None):
    mode = os.stat(agents).st_mode & 0o777
    journal_path = state / 'pending.json'
    journal = {
        'before_bytes': base64.b64encode(before).decode('ascii'),
        'before_sha256': _sha(before), 'after_sha256': _sha(after),
        'mode': mode, 'ledger_before': ledger_before, 'ledger_after': ledger_after,
    }
    _atomic_write(journal_path, _json_bytes(journal), 0o600)
    try:
        _atomic_write(agents, after, mode)
        _restore_ledger(state / 'ledger.json', ledger_after)
        if receipt_path is not None:
            _atomic_write(receipt_path, _json_bytes(receipt), 0o600)
        journal_path.unlink()
        _sync_dir(state)
    except BaseException:
        if not journal_path.exists():
            _atomic_write(journal_path, _json_bytes(journal), 0o600)
        _recover(state, agents)
        raise


def _splice(original, records):
    _check_markers(original)
    body = json.dumps({"records": records}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    start = original.find(_START_B)
    if start == -1:
        prefix = original
        if prefix and not prefix.endswith(b"\n"):
            prefix += b"\n"
        return prefix + _START_B + b"\n" + body + b"\n" + _END_B + b"\n"
    end = original.find(_END_B, start + len(_START_B))
    return original[: start + len(_START_B)] + b"\n" + body + b"\n" + original[end:]


def _load_ledger(path):
    if not path.exists():
        return None
    return json.loads(_read(path).decode("utf-8"))


@contextmanager
def _lock(state):
    preexisted = state.exists()
    state.mkdir(parents=True, exist_ok=True)
    if not preexisted:
        _chmod(state, 0o700)
    lock_path = state / "lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise MemoryError("locked", "exclusive lock held for agents and state") from None
        yield
    finally:
        os.close(fd)


def build_candidate(project, agents_path, records_path, output_path):
    """Bind reviewed records to the current full AGENTS sha256. No transcript scan."""
    if not isinstance(project, str) or not project.strip():
        raise MemoryError("bad_project", "project is required")
    records_path = Path(records_path)
    payload_records = json.loads(_read(records_path).decode("utf-8"))
    _chmod(records_path, 0o600)
    records = _normalize(project, payload_records)
    agents = Path(agents_path).resolve()
    current = _read(agents)
    _check_markers(current)
    candidate = {
        "agents_path": str(agents),
        "expected_sha256": _sha(current),
        "note": "Operator-reviewed. Known secrets are blocked; generic absence is not guaranteed.",
        "project": project,
        "records": records,
        "records_path": str(records_path.resolve()),
        "records_sha256": _sha(_read(records_path)),
        "version": 1,
    }
    _atomic_write(output_path, _json_bytes(candidate), 0o600)
    return _sha(_read(output_path))


def _ledger_records(ledger, project, agents_path):
    if ledger is None:
        return []
    if ledger.get("project") not in (None, project) or ledger.get("agents_path") not in (None, agents_path):
        raise MemoryError("bad_project", "ledger is for a different project or AGENTS file")
    return list(ledger.get("records") or [])


def promote(candidate_path, approve):
    candidate_path = Path(candidate_path)
    raw = _read(candidate_path)
    digest = _sha(raw)
    _approve(digest, approve)
    _chmod(candidate_path, 0o600)
    candidate = json.loads(raw.decode("utf-8"))
    if candidate.get("version") != 1:
        raise MemoryError("bad_records", "unsupported candidate")
    project = candidate["project"]
    agents = Path(candidate["agents_path"])
    records = _normalize(project, candidate["records"])
    state = state_dir_for(agents)
    ledger_path = state / "ledger.json"
    with _lock(state):
        _recover(state, agents)
        current = _read(agents)
        current_sha = _sha(current)
        if not hmac.compare_digest(current_sha, candidate["expected_sha256"]):
            raise MemoryError("stale", "AGENTS hash does not match the candidate")
        ledger = _load_ledger(ledger_path)
        existing = _ledger_records(ledger, project, str(agents))
        merged, history = _merge(ledger.get('history', existing) if ledger else existing, records)
        updated = _splice(current, merged)
        backup = state / f"backup-{current_sha}.bin"
        _atomic_write(backup, current, 0o600)
        after = _sha(updated)
        new_ledger = {
            "agents_path": str(agents),
            "cursor": after,
            "ids": [rec["id"] for rec in merged],
            "project": project,
            "records": merged,
            "history": history,
        }
        receipt = {
            "after_sha256": after,
            "agents_path": str(agents),
            "backup_path": str(backup),
            "backup_sha256": current_sha,
            "before_sha256": current_sha,
            "candidate_sha256": digest,
            "cursor": after,
            "ids": new_ledger["ids"],
            "ledger_before": ledger,
            "project": project,
            "version": 1,
        }
        receipt_path = state / f"receipt-{digest[:16]}.json"
        _commit(state, agents, current, updated, ledger, new_ledger, receipt_path, receipt)
        receipt_sha = _sha(_read(receipt_path))
    return {"cursor": after, "receipt_path": str(receipt_path), "receipt_sha256": receipt_sha}


def rollback(receipt_path, approve):
    receipt_path = Path(receipt_path)
    raw = _read(receipt_path)
    _approve(_sha(raw), approve)
    _chmod(receipt_path, 0o600)
    receipt = json.loads(raw.decode("utf-8"))
    agents = Path(receipt["agents_path"])
    state = state_dir_for(agents)
    ledger_path = state / "ledger.json"
    with _lock(state):
        _recover(state, agents)
        current = _read(agents)
        if not hmac.compare_digest(_sha(current), receipt["after_sha256"]):
            raise MemoryError("stale", "AGENTS hash does not match the receipt")
        backup = Path(receipt["backup_path"])
        previous = _read(backup)
        if not hmac.compare_digest(_sha(previous), receipt["before_sha256"]):
            raise MemoryError("stale", "backup does not match the receipt")
        if not hmac.compare_digest(_sha(previous), receipt["backup_sha256"]):
            raise MemoryError("stale", "backup hash mismatch")
        prior = receipt.get("ledger_before")
        _commit(state, agents, current, previous, _load_ledger(ledger_path), prior)
        restored = _sha(_read(agents))
    return {"agents_sha256": restored, "cursor": receipt["before_sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="memory")
    sub = parser.add_subparsers(dest="cmd", required=True)
    candidate = sub.add_parser("candidate")
    candidate.add_argument("--project", required=True)
    candidate.add_argument("--agents", required=True)
    candidate.add_argument("--records", required=True)
    candidate.add_argument("--output", required=True)
    promote_cmd = sub.add_parser("promote")
    promote_cmd.add_argument("--candidate", required=True)
    promote_cmd.add_argument("--approve", required=True)
    roll = sub.add_parser("rollback")
    roll.add_argument("--receipt", required=True)
    roll.add_argument("--approve", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "candidate":
            print(build_candidate(args.project, args.agents, args.records, args.output))
        elif args.cmd == "promote":
            print(promote(args.candidate, args.approve)["receipt_sha256"])
        else:
            print(rollback(args.receipt, args.approve)["agents_sha256"])
    except MemoryError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
