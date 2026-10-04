import json
from pathlib import Path
import subprocess
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '99c5d0f'


def load(source, name):
    module = types.ModuleType(name)
    exec(compile(source, name, 'exec'), module.__dict__)
    return module


def record(identifier, text, supersedes=None):
    result = {'id': identifier, 'speaker': 'user', 'project': 'fixture',
              'source': 'reviewed synthetic qualification', 'text': text}
    if supersedes:
        result['supersedes'] = supersedes
    return result


def exercise(module):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        agents = root / 'AGENTS.md'
        original = b'# Policy\nPreserve tenant boundaries.\n'
        agents.write_bytes(original)

        def candidate(records, name):
            source, output = root / (name + '-records.json'), root / (name + '.json')
            source.write_text(json.dumps(records))
            digest = module.build_candidate('fixture', agents, source, output)
            return output, digest

        first, digest = candidate([record('a', 'Use tabs.')], 'first')
        original_write = module._atomic_write

        def fail_ledger(path, data, mode):
            if Path(path).name == 'ledger.json':
                raise OSError('synthetic ledger failure')
            return original_write(path, data, mode)

        with patch.object(module, '_atomic_write', fail_ledger):
            try:
                module.promote(first, digest)
            except OSError:
                pass
        failed_write_preserves_policy = agents.read_bytes() == original
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        agents = root / 'AGENTS.md'
        agents.write_bytes(original)
        first, digest = candidate([record('a', 'Use tabs.')], 'first')
        module.promote(first, digest)
        correction, digest = candidate([record('b', 'Use spaces.', 'a')], 'correction')
        module.promote(correction, digest)
        expected = agents.read_bytes()
        replay, digest = candidate([record('a', 'Use tabs.')], 'replay')
        module.promote(replay, digest)
        replay_preserves_correction = agents.read_bytes() == expected
    return {'failed_write_preserves_policy': failed_write_preserves_policy,
            'replay_preserves_correction': replay_preserves_correction}


def main():
    baseline_source = subprocess.check_output(['git', 'show', BASELINE + ':tools/memory.py'],
                                              cwd=ROOT, text=True)
    baseline = exercise(load(baseline_source, 'baseline_memory'))
    treatment = exercise(load((ROOT / 'tools/memory.py').read_text(), 'treatment_memory'))
    assert baseline == {'failed_write_preserves_policy': False, 'replay_preserves_correction': False}
    assert treatment == {'failed_write_preserves_policy': True, 'replay_preserves_correction': True}
    print(json.dumps({'verdict': 'VERIFIED', 'baseline_revision': BASELINE,
                      'baseline': baseline, 'treatment': treatment}, indent=2))


if __name__ == '__main__':
    main()
