"""Build independently selectable packages from immutable sources and adapters."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {'sapsynk-teamkit': 'teamkit', 'sapsynk-dyl': 'dyl',
           'sapsynk-learning': 'continual-learning'}


def verify_sources(root=ROOT):
    lock = json.loads((root / 'sources.lock.json').read_text())
    for name, source in lock['sources'].items():
        base = root / 'upstream' / name
        files = {str(p.relative_to(base)): p for p in base.rglob('*') if p.is_file()}
        if set(files) != set(source['files']):
            raise ValueError(f'upstream inventory changed: {name}')
        for relative, digest in source['files'].items():
            if hashlib.sha256(files[relative].read_bytes()).hexdigest() != digest:
                raise ValueError(f'upstream content changed: {name}/{relative}')
    return lock


def validate_package(package):
    identity = json.loads((package / 'plugin.json').read_text())
    native = json.loads((package / '.codex-plugin/plugin.json').read_text())
    if any(identity[key] != native[key] for key in ('name', 'version', 'description')):
        raise ValueError('native and portable identities differ')
    interface = identity['extensions']['com.openai']['interface']
    if len(interface['shortDescription']) > 30:
        raise ValueError('listing subtitle exceeds 30 characters')
    if any(key in identity for key in ('skills', 'mcpServers', 'apps', 'interface')):
        raise ValueError('nonportable root manifest field')
    skills = sorted((package / 'skills').glob('*/SKILL.md'))
    if not skills:
        raise ValueError('no selected skills')
    for skill in skills:
        text = skill.read_text()
        match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        if not match or not re.search(r'^name:\s*' + re.escape(skill.parent.name) + r'\s*$', match[1], re.M):
            raise ValueError(f'skill name/frontmatter invalid: {skill}')
        if not re.search(r'^description:\s*\S', match[1], re.M):
            raise ValueError(f'skill description missing: {skill}')
    for document in package.rglob('*.md'):
        if 'upstream' in document.relative_to(package).parts:
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', document.read_text()):
            if re.match(r'[a-z]+://', target) or target.startswith('#'):
                continue
            resolved = (document.parent / target.split('#')[0]).resolve()
            if not resolved.is_relative_to(package.resolve()) or not resolved.exists():
                raise ValueError(f'broken or uncontained adapter link: {document}: {target}')
    for path in package.rglob('*'):
        if path.is_symlink():
            raise ValueError('package symlinks are not supported')
    return identity


def build(root=ROOT):
    lock = verify_sources(root)
    archives = []
    for name, source in SOURCES.items():
        package = root / 'plugins' / name
        upstream = package / 'upstream' / source
        if upstream.exists():
            shutil.rmtree(upstream)
        shutil.copytree(root / 'upstream' / source, upstream)
        (package / 'LICENSE').write_bytes((upstream / 'LICENSE').read_bytes())
        (package / 'sources.lock.json').write_text(json.dumps({
            'repository': lock['repository'], 'revision': lock['revision'],
            'source': lock['sources'][source]}, indent=2) + '\n')
        if name == 'sapsynk-learning':
            script = root / 'tools/memory.py'
            if not script.stat().st_size:
                raise ValueError('learning implementation is missing')
            (package / 'scripts').mkdir(exist_ok=True)
            shutil.copyfile(script, package / 'scripts/memory.py')
        identity = validate_package(package)
        directory = root / 'dist'
        directory.mkdir(exist_ok=True)
        archive = directory / f"{name}-{identity['version']}.zip"
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
            for path in sorted(package.rglob('*')):
                if not path.is_file() or '__pycache__' in path.parts:
                    continue
                entry = zipfile.ZipInfo(name + '/' + str(path.relative_to(package)), (1980, 1, 1, 0, 0, 0))
                entry.external_attr = 0o100644 << 16
                entry.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(entry, path.read_bytes())
        archives.append(str(archive))
    return archives


if __name__ == '__main__':
    print(json.dumps({'archives': build()}, indent=2))
