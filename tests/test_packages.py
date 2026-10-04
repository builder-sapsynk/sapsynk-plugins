import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('plugin_build', ROOT / 'tools/build.py')
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class PackageTests(unittest.TestCase):
    def test_exact_sources_and_deterministic_archives(self):
        build.verify_sources()
        first = build.build()
        hashes = [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in first]
        second = build.build()
        self.assertEqual(hashes, [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in second])
        self.assertEqual(len(first), 3)
        for path in first:
            with zipfile.ZipFile(path) as archive:
                members = archive.namelist()
                name = members[0].split('/')[0]
                identity = json.loads(archive.read(name + '/plugin.json'))
                self.assertEqual(identity['name'], name)
                self.assertTrue(any('/skills/' in member and member.endswith('/SKILL.md') for member in members))
                self.assertIn(name + '/LICENSE', members)
                self.assertFalse(any(member.startswith(name + '/hooks/') for member in members))
                self.assertFalse(any(member.endswith('/auth.json') for member in members))
                self.assertFalse(any('/.git/' in member or '/.pstack/runs/' in member for member in members))

    def test_changed_upstream_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copyfile(ROOT / 'sources.lock.json', root / 'sources.lock.json')
            shutil.copytree(ROOT / 'upstream', root / 'upstream')
            (root / 'upstream/teamkit/LICENSE').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'upstream content changed'):
                build.verify_sources(root)

    def test_uncontained_skill_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'package'
            shutil.copytree(ROOT / 'plugins/sapsynk-teamkit', root)
            skill = root / 'skills/verify-this/SKILL.md'
            with skill.open('a') as output:
                output.write('\n[invalid](../../../../outside.md)\n')
            with self.assertRaisesRegex(ValueError, 'uncontained adapter link'):
                build.validate_package(root)


if __name__ == '__main__':
    unittest.main()
