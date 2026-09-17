"""Pin BBM and retain every instance with explicit Cell Collective provenance."""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'sybila/biodivine-boolean-models'


def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'cc-reduction-research'}), timeout=60) as response:
        return response.read()


def main():
    destination = ROOT / 'data/cellcollective'
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'manifest.json'
    if manifest_path.exists():
        commit = json.loads(manifest_path.read_text())['commit']
    else:
        commit = json.loads(fetch(f'https://api.github.com/repos/{REPO}/commits/main'))['sha']
    archive_url = f'https://codeload.github.com/{REPO}/zip/{commit}'
    archive_bytes = fetch(archive_url)
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    selected, inventory = [], []
    for path in sorted(archive.namelist()):
        if '/models/' not in path or not path.endswith('/metadata.json'):
            continue
        metadata_bytes = archive.read(path)
        metadata = json.loads(metadata_bytes)
        urls = metadata.get('url-model', [])
        if isinstance(urls, str):
            urls = [urls]
        cc_urls = [u for u in urls if 'cellcollective.org' in u.lower()]
        included = bool(cc_urls)
        inventory.append({'id': metadata['id'], 'name': metadata['name'], 'included': included,
                          'cellcollective_urls': cc_urls})
        if not included:
            continue
        ident = str(metadata['id']).zfill(3)
        folder = destination / ident
        folder.mkdir(exist_ok=True)
        prefix = path.rsplit('/', 1)[0]
        files = []
        for name in ('metadata.json', 'model.bnet'):
            data = archive.read(prefix + '/' + name)
            (folder / name).write_bytes(data)
            files.append({'name': name, 'sha256': hashlib.sha256(data).hexdigest()})
        selected.append({'id': ident, 'name': metadata['name'],
                         'repository_directory': prefix.split('/', 1)[1],
                         'cellcollective_urls': cc_urls, 'files': files})
    manifest = {'repository': REPO, 'commit': commit, 'archive_url': archive_url,
                'archive_sha256': hashlib.sha256(archive_bytes).hexdigest(),
                'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'selection': 'All BBM metadata records with a Cell Collective url-model; no size filter. BBM instances, not a claim of complete live Cell Collective coverage.',
                'models': selected, 'inventory': inventory}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    # Preserve upstream licensing information alongside the downloaded models.
    for path in archive.namelist():
        if path.count('/') == 1 and Path(path).name.lower().startswith('license'):
            (destination / ('UPSTREAM_' + Path(path).name)).write_bytes(archive.read(path))
    print(f'{len(selected)} Cell Collective instances / {len(inventory)} BBM records; commit {commit}')


if __name__ == '__main__':
    main()
