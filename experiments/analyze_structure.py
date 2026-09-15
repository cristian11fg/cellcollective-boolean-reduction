"""Reproduce draft-aligned pilot diagnostics without changing legacy results."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ccreduce.parser import read_bnet
from ccreduce.reduction import reduce_network
from ccreduce.structure import network_structure
from ccreduce.fixed_points import validate_bijection


def main():
    manifest = json.loads((ROOT / 'data/raw/manifest.json').read_text())
    records = []
    for item in manifest['models']:
        folder = ROOT / 'data/raw' / item['id']
        for entry in item['files']:
            if hashlib.sha256((folder / entry['name']).read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Input checksum mismatch')
        meta = json.loads((folder / 'metadata.json').read_text())
        original = read_bnet(folder / 'model.bnet', meta['input-names'])
        record = {'id': item['id'], 'name': meta['name'], 'source': meta['url-model'],
                  'before': network_structure(original), 'reductions': {}}
        for policy in ('first', 'min_degree', 'min_growth', 'random'):
            reduction = reduce_network(original, policy, 42)
            before_fp, after_fp, lifted = validate_bijection(original, reduction)
            record['reductions'][policy] = {'after': network_structure(reduction.network),
                'survivors': sorted(reduction.network.functions),
                'steps': [{'node': n, 'function': f.as_dict()} for n, f in reduction.steps],
                'functions': {n: f.expression() for n, f in reduction.network.functions.items()},
                'original_fixed_points': before_fp, 'reduced_fixed_points': after_fp,
                'lifted_fixed_points': lifted, 'bijection_verified': True}
        records.append(record)
        b = record['before']
        print(item['id'], 'out_uniform=', b['out_uniform'], 'unate=', b['locally_unate'],
              'MIN_MAX=', b['MIN_MAX_with_constants'], 'conflicts=', list(b['conflicts']))
    output = ROOT / 'results/structure'
    output.mkdir(parents=True, exist_ok=True)
    result = {'scope': 'Five-model BBM pilot, not the Cell Collective catalogue',
              'source_commit': manifest['commit'], 'seed': 42,
              'code_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [Path(__file__), ROOT / 'src/ccreduce/structure.py']},
              'models': records}
    (output / 'pilot.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
