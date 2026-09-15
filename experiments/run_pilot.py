"""Run all policies, save full traces, metrics, and exhaustive FP certificates."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ccreduce.parser import read_bnet
from ccreduce.reduction import reduce_network
from ccreduce.fixed_points import fixed_points, validate_bijection
from ccreduce.metrics import metrics


def main():
    output = ROOT / 'results/pilot'
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'data/raw/manifest.json').read_text())
    rows = []
    for model in manifest['models']:
        directory = ROOT / 'data/raw' / model['id']
        for item in model['files']:
            if hashlib.sha256((directory / item['name']).read_bytes()).hexdigest() != item['sha256']:
                raise ValueError(f'Checksum mismatch: {item["name"]}')
        metadata = json.loads((directory / 'metadata.json').read_text())
        original = read_bnet(directory / 'model.bnet', metadata['input-names'])
        declared = set(metadata['variable-names']) | set(metadata['input-names']) | set(metadata['output-names'])
        if set(original.functions) != declared:
            raise ValueError('Metadata and model variables disagree')
        start = perf_counter()
        original_fp = fixed_points(original)
        fp_before_seconds = perf_counter() - start
        for policy in ('first', 'min_degree', 'min_growth', 'random'):
            start = perf_counter()
            reduction = reduce_network(original, policy, seed=42)
            reduction_seconds = perf_counter() - start
            start = perf_counter()
            reduced_fp = fixed_points(reduction.network)
            fp_after_seconds = perf_counter() - start
            _, _, lifted = validate_bijection(original, reduction)
            before, after = metrics(original), metrics(reduction.network)
            row = {'model_id': model['id'], 'name': metadata['name'], 'policy': policy, 'seed': 42,
                   'reduction_fraction': 1 - after['nodes'] / before['nodes'],
                   'internal_reduction_fraction': 1 - after['internal_nodes'] / before['internal_nodes'] if before['internal_nodes'] else None,
                   'fixed_points_before': len(original_fp), 'fixed_points_after': len(reduced_fp),
                   'bijection_verified': True, 'reduction_seconds': reduction_seconds,
                   'fp_before_seconds': fp_before_seconds, 'fp_after_seconds': fp_after_seconds}
            for prefix, values in (('before', before), ('after', after)):
                row.update({f'{prefix}_{k}': json.dumps(v, sort_keys=True) if isinstance(v, dict) else v for k, v in values.items()})
            rows.append(row)
            detail = {'source': model, 'metadata': metadata, 'summary': row, 'original': original.as_dict(),
                      'reduced': reduction.network.as_dict(),
                      'steps': [{'node': n, 'function': f.as_dict()} for n, f in reduction.steps],
                      'original_fixed_points': original_fp, 'reduced_fixed_points': reduced_fp, 'lifted_fixed_points': lifted}
            from ccreduce.boolean import states
            detail['fixed_points_by_input'] = [{'input': s, 'count': sum(all(fp[n] == v for n, v in s.items()) for fp in original_fp)} for s in states(tuple(sorted(original.inputs)))]
            (output / f'{model["id"]}_{policy}.json').write_text(json.dumps(detail, indent=2), encoding='utf-8')
            expressions = '\n'.join(f'{n}, {f.expression()}' for n, f in reduction.network.functions.items())
            (output / f'{model["id"]}_{policy}.bnet').write_text('targets,factors\n' + (expressions + '\n' if expressions else ''), encoding='utf-8')
            print(f'{model["id"]} {policy}: {before["nodes"]} -> {after["nodes"]}; FP={len(reduced_fp)}; verified')
    with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / 'environment.json').write_text(json.dumps({'python': sys.version, 'platform': platform.platform(), 'max_support': 16, 'max_fp_nodes': 20, 'input_policy': 'free constant parameters encoded by identity; fixed points pooled over all assignments', 'source_commit': manifest['commit'], 'code_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'src').rglob('*.py'))}}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
