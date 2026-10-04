import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import memory as m


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.agents = self.root / 'AGENTS.md'
        self.original = b'# Policy\nNever override tenant boundaries.\n'
        self.agents.write_bytes(self.original)

    def record(self, identifier, text, supersedes=None):
        record = {'id': identifier, 'speaker': 'user', 'project': 'test',
                  'source': 'reviewed synthetic fixture', 'text': text}
        if supersedes:
            record['supersedes'] = supersedes
        return record

    def candidate(self, records, name='candidate'):
        source = self.root / (name + '-records.json')
        source.write_text(json.dumps(records))
        output = self.root / (name + '.json')
        digest = m.build_candidate('test', self.agents, source, output)
        return output, digest

    def test_promotion_write_failures_restore_state_and_allow_same_retry(self):
        for target in ('ledger.json', 'receipt-'):
            with self.subTest(target=target):
                candidate, digest = self.candidate([self.record('a', 'Use spaces.')], target)
                state = m.state_dir_for(self.agents)
                original_write = m._atomic_write

                def fail_once(path, data, mode):
                    if target in Path(path).name:
                        raise OSError('injected storage failure')
                    return original_write(path, data, mode)

                with patch.object(m, '_atomic_write', fail_once):
                    with self.assertRaises(OSError):
                        m.promote(candidate, digest)
                self.assertEqual(self.agents.read_bytes(), self.original)
                self.assertFalse((state / 'ledger.json').exists())
                result = m.promote(candidate, digest)
                m.rollback(result['receipt_path'], result['receipt_sha256'])
                self.assertEqual(self.agents.read_bytes(), self.original)

    def test_rollback_failure_keeps_promoted_state_and_is_retriable(self):
        candidate, digest = self.candidate([self.record('a', 'Use spaces.')])
        result = m.promote(candidate, digest)
        current = self.agents.read_bytes()
        ledger = m.state_dir_for(self.agents) / 'ledger.json'
        current_ledger = ledger.read_bytes()
        original_unlink = Path.unlink

        def fail_ledger(path, *args, **kwargs):
            if path == ledger:
                raise OSError('injected unlink failure')
            return original_unlink(path, *args, **kwargs)

        with patch.object(Path, 'unlink', fail_ledger):
            with self.assertRaises(OSError):
                m.rollback(result['receipt_path'], result['receipt_sha256'])
        self.assertEqual(self.agents.read_bytes(), current)
        self.assertEqual(ledger.read_bytes(), current_ledger)
        m.rollback(result['receipt_path'], result['receipt_sha256'])
        self.assertEqual(self.agents.read_bytes(), self.original)

    def test_process_interruption_recovers_and_releases_lock(self):
        candidate, digest = self.candidate([self.record('a', 'Use spaces.')])
        script = ('import os,sys\nfrom tools import memory as m\n'
                  'm._restore_ledger=lambda *args: os._exit(17)\n'
                  'm.promote(sys.argv[1],sys.argv[2])\n')
        child = subprocess.run([sys.executable, '-c', script, str(candidate), digest],
                               cwd=Path(__file__).resolve().parents[1], capture_output=True)
        self.assertEqual(child.returncode, 17, child.stderr)
        self.assertNotEqual(self.agents.read_bytes(), self.original)
        self.assertTrue((m.state_dir_for(self.agents) / 'pending.json').exists())
        result = m.promote(candidate, digest)
        self.assertFalse((m.state_dir_for(self.agents) / 'pending.json').exists())
        m.rollback(result['receipt_path'], result['receipt_sha256'])
        self.assertEqual(self.agents.read_bytes(), self.original)

    def test_correction_cycle_is_rejected_without_changes(self):
        candidate, digest = self.candidate([self.record('a', 'Use tabs.', 'b'),
                                             self.record('b', 'Use spaces.', 'a')])
        with self.assertRaises(m.MemoryError):
            m.promote(candidate, digest)
        self.assertEqual(self.agents.read_bytes(), self.original)
        self.assertFalse((m.state_dir_for(self.agents) / 'ledger.json').exists())

    def test_final_directory_sync_failure_restores_and_allows_retry(self):
        candidate, digest = self.candidate([self.record('a', 'Use spaces.')])
        state = m.state_dir_for(self.agents)
        original_sync = m._sync_dir
        count = 0

        def fail_final_once(path):
            nonlocal count
            if Path(path) == state:
                count += 1
                if count == 5:
                    raise OSError('injected final fsync failure')
            return original_sync(path)

        with patch.object(m, '_sync_dir', fail_final_once):
            with self.assertRaises(OSError):
                m.promote(candidate, digest)
        self.assertEqual(self.agents.read_bytes(), self.original)
        self.assertFalse((state / 'ledger.json').exists())
        result = m.promote(candidate, digest)
        m.rollback(result['receipt_path'], result['receipt_sha256'])
        self.assertEqual(self.agents.read_bytes(), self.original)

    def test_replaying_a_retired_id_cannot_resurrect_it(self):
        old = self.record('a', 'Use tabs.')
        first, digest = self.candidate([old], 'first')
        m.promote(first, digest)
        second, digest = self.candidate([self.record('b', 'Use spaces.', 'a')], 'second')
        m.promote(second, digest)
        current = self.agents.read_bytes()
        replay, digest = self.candidate([old], 'replay')
        m.promote(replay, digest)
        self.assertEqual(self.agents.read_bytes(), current)
        ledger = json.loads((m.state_dir_for(self.agents) / 'ledger.json').read_text())
        self.assertEqual(ledger['ids'], ['b'])
        self.assertEqual({rec['id'] for rec in ledger['history']}, {'a', 'b'})


if __name__ == '__main__':
    unittest.main()
