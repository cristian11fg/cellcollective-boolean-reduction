"""Download a version-pinned, provenance-filtered Cell Collective pilot from BBM."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REPO = 'sybila/biodivine-boolean-models'

def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'cc-reduction-research'}), timeout=60) as r:
        return r.read()

def main():
    destination = ROOT / 'data/raw'
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for model in manifest['models']:
            for item in model['files']:
                target = destination / model['id'] / item['name']
                data = fetch(item['url'])
                if hashlib.sha256(data).hexdigest() != item['sha256']:
                    raise ValueError('Checksum mismatch')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        print('Replayed pinned manifest')
        return
    tree = json.loads(fetch(f'https://api.github.com/repos/{REPO}/git/trees/main?recursive=1'))
    if tree.get('truncated'):
        raise ValueError('Incomplete repository tree')
    commit = tree['sha']
    paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob']
    directories = sorted({p.rsplit('/', 1)[0] for p in paths if p.startswith('models/') and re.search(r'var-\d+]', p)}, key=lambda p: (int(re.search(r'var-(\d+)]', p)[1]), p))
    selected = []
    for directory in directories:
        n = int(re.search(r'var-(\d+)]', directory)[1])
        if n > 20:
            break
        files = [p for p in paths if p.rsplit('/', 1)[0] == directory]
        metadata = [p for p in files if p.endswith('.json')]
        if not metadata:
            continue
        meta = fetch(f'https://raw.githubusercontent.com/{REPO}/{commit}/{quote(metadata[0])}')
        if b'cellcollective' not in meta.lower():
            continue
        ident = re.search(r'id-(\d+)', directory)[1]
        model = {'id': ident, 'repository_directory': directory, 'files': []}
        for path in files:
            if not path.endswith(('.json', '.md', '.bnet', '.sbml', '.xml')):
                continue
            url = f'https://raw.githubusercontent.com/{REPO}/{commit}/{quote(path)}'
            data = fetch(url)
            target = destination / ident / Path(path).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            model['files'].append({'name': target.name, 'url': url, 'sha256': hashlib.sha256(data).hexdigest()})
        selected.append(model)
        print(directory, flush=True)
        if len(selected) == 5:
            break
    manifest_path.write_text(json.dumps({'repository': REPO, 'commit': commit, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'selection': 'Five smallest BBM models whose JSON metadata mentions cellcollective; ties by directory; maximum 20 nodes. Convenience pilot, not representative.', 'models': selected}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
