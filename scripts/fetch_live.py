"""Download all versions of all public Boolean model cards and normalize EXPR."""
from concurrent.futures import ThreadPoolExecutor
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://research.cellcollective.org/web'


def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'cc-reduction-research'}), timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def normalize(expressions, external):
    rules = {}
    for line in expressions.splitlines():
        if not line.strip():
            continue
        name, expr = line.split(' = ', 1)
        if name in rules:
            raise ValueError(f'Duplicate rule {name}')
        rules[name] = expr.strip()
    inputs = [line.strip() for line in external.splitlines() if line.strip()]
    names = set(rules) | set(inputs)
    mapping = {n: 'v_' + re.sub(r'[^A-Za-z0-9_]', '_', n) for n in names}
    if len(set(mapping.values())) != len(mapping):
        # Stable collision-free fallback; original names are always retained.
        mapping = {n: f'v_{i:04d}' for i, n in enumerate(sorted(names))}
    ordered = sorted(names, key=lambda n: (-len(n), n))

    def translate(expr):
        tokens, position = [], 0
        while position < len(expr):
            if expr[position].isspace():
                position += 1
                continue
            match = next((n for n in ordered if expr.startswith(n, position) and
                          (position + len(n) == len(expr) or expr[position + len(n)].isspace() or expr[position + len(n)] in '()')), None)
            if match is not None:
                tokens.append(mapping[match])
                position += len(match)
                continue
            operator = re.match(r'(AND|OR|NOT|XOR)\b', expr[position:])
            if operator:
                tokens.append({'AND': '&', 'OR': '|', 'NOT': '!', 'XOR': '^'}[operator[0]])
                position += len(operator[0])
            elif expr[position] in '()01':
                tokens.append(expr[position])
                position += 1
            else:
                raise ValueError(f'Unknown expression token at {expr[position:position+60]!r}')
        return ' '.join(tokens)

    bnet = 'targets,factors\n' + '\n'.join(f'{mapping[n]}, {translate(e)}' for n, e in rules.items()) + '\n'
    return bnet, mapping, [mapping[n] for n in inputs], [mapping[n] for n in rules]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', help='Rebuild manifest from already cached source files')
    args = parser.parse_args()
    output = ROOT / 'data/live'
    output.mkdir(parents=True, exist_ok=True)
    catalogue = ROOT / 'data/cellcollective/live-research.cellcollective.org-web.json'
    cards = json.loads(catalogue.read_text())
    jobs = [(card, version) for card in cards for version in card['model']['modelVersionMap']]

    def download(job):
        card, version = job
        model = card['model']
        ident = f'{model["id"]}_{version}'
        folder = output / ident
        folder.mkdir(exist_ok=True)
        url = f'{BASE}/_api/model/export/{model["id"]}?version={version}&type=EXPR'
        record = {'id': ident, 'cellcollective_id': model['id'], 'version': version, 'name': model['name'],
                  'cellcollective_urls': [f'https://research.cellcollective.org/#module/{model["id"]}:{version}'],
                  'export_url': url}
        try:
            raw_path = folder / 'export.zip'
            if not raw_path.exists():
                if args.offline:
                    raise ValueError('Source export not yet downloaded')
                raw_path.write_bytes(fetch(url))
            archive = zipfile.ZipFile(io.BytesIO(raw_path.read_bytes()))
            expr = archive.read('expr/expressions.ALL.txt').decode('utf-8-sig')
            external = archive.read('expr/external_components.ALL.txt').decode('utf-8-sig')
            fixed = {}
            sbml_count = None
            try:
                bnet, mapping, inputs, variables = normalize(expr, external)
                if len(mapping) != model['components']:
                    raise ValueError('Missing components in expression export')
            except ValueError:
                # EXPR omits some clamped components. Recover only explicitly fixed
                # SBML species with a declared Boolean initialLevel, never infer inputs.
                sbml_path = folder / 'source.sbml'
                if not sbml_path.exists():
                    if args.offline:
                        raise ValueError('SBML required but not yet downloaded')
                    sbml_path.write_bytes(fetch(f'{BASE}/_api/model/export/{model["id"]}?version={version}&type=SBML'))
                q = '{http://www.sbml.org/sbml/level3/version1/qual/version1}'
                species = list(ET.fromstring(sbml_path.read_bytes()).iter(q + 'qualitativeSpecies'))
                sbml_count = len(species)
                present = {line.split(' = ', 1)[0] for line in expr.splitlines() if line.strip()} | set(external.splitlines())
                for species_node in species:
                    a = species_node.attrib
                    name = a[q + 'name']
                    if name not in present:
                        if a.get(q + 'constant') != 'true' or a.get(q + 'initialLevel') not in ('0', '1') or a.get(q + 'maxLevel') != '1':
                            raise ValueError(f'Missing non-fixed Boolean species: {name}')
                        fixed[name] = int(a[q + 'initialLevel'])
                expr += '\n' + '\n'.join(f'{n} = {v}' for n, v in fixed.items())
                bnet, mapping, inputs, variables = normalize(expr, external)
            if len(mapping) != model['components'] and len(mapping) != sbml_count:
                raise ValueError(f'Export/card/SBML component mismatch: {len(mapping)}, {model["components"]}, {sbml_count}')
            (folder / 'model.bnet').write_text(bnet, encoding='utf-8')
            metadata = {'id': ident, 'name': model['name'], 'input-names': inputs,
                        'variable-names': variables, 'output-names': [], 'original_name_to_bnet': mapping,
                        'sbml_fixed_components': fixed,
                        'catalogue_component_count': model['components'], 'sbml_component_count': sbml_count,
                        'source_model': model, 'source_hash': card.get('hash'), 'version': version}
            (folder / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            file_names = ['export.zip', 'model.bnet', 'metadata.json']
            if (folder / 'source.sbml').exists():
                file_names.append('source.sbml')
            record.update(status='downloaded', files=[{'name': n, 'sha256': hashlib.sha256((folder / n).read_bytes()).hexdigest()}
                          for n in file_names])
            print(f'{ident}: {len(variables)} rules + {len(inputs)} inputs', flush=True)
        except Exception as error:
            record.update(status='error', error=repr(error))
            print(f'{ident}: ERROR {error}', flush=True)
        return record

    with ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(download, jobs))
    manifest = {'repository': 'Cell Collective live public API', 'commit': None,
                'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'catalogue_url': f'{BASE}/api/model/cards/research?modelTypes=boolean&orderBy=recent&category=published&cards=10000',
                'catalogue_sha256': hashlib.sha256(catalogue.read_bytes()).hexdigest(),
                'public_models': len(cards), 'versions': len(jobs),
                'selection': 'All versions listed on every returned public published Boolean model card',
                'models': [r for r in records if r['status'] == 'downloaded'],
                'failures': [r for r in records if r['status'] != 'downloaded']}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Downloaded {len(manifest["models"])} / {len(jobs)} versions', flush=True)


if __name__ == '__main__':
    main()
