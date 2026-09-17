"""Process every recovered instance; checkpoint each policy and report failures."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / '.tools/research')]
POLICIES = ('first', 'min_degree', 'min_growth', 'random')
ALGORITHM_VERSION = '0.3-taxonomy'


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def worker(ident, dataset='cellcollective'):
    from ccreduce.symbolic import read_symbolic, classify, reduce_symbolic, certify, fixed_point_summary, readable
    sys.setrecursionlimit(10000)
    folder = ROOT / 'data' / dataset / ident
    output = ROOT / 'results' / ('catalogue' if dataset == 'cellcollective' else 'live') / ident
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'data' / dataset / 'manifest.json').read_text())
    record = next(m for m in manifest['models'] if m['id'] == ident)
    for item in record['files']:
        if hashlib.sha256((folder / item['name']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Source checksum mismatch')
    metadata = json.loads((folder / 'metadata.json').read_text())
    original = read_symbolic(folder / 'model.bnet', metadata['input-names'])
    declared = set(metadata['variable-names']) | set(metadata['input-names']) | set(metadata['output-names'])
    if declared != set(original.functions):
        raise ValueError('Metadata and variables disagree')
    before = classify(original)
    write(output / 'before.json', {'id': ident, 'name': metadata['name'], 'source': record,
                                   'classification': before, 'all_rules_classification': classify(original, True)})
    for policy in POLICIES:
        destination = output / f'{policy}.json'
        if destination.exists() and json.loads(destination.read_text()).get('algorithm_version') == ALGORITHM_VERSION and json.loads(destination.read_text())['status'] == 'complete' and json.loads(destination.read_text()).get('certificate', {}).get('bijection_verified', False):
            continue
        start = perf_counter()
        try:
            # Each policy gets a fresh manager: failed trials cannot consume the next budget.
            original = read_symbolic(folder / 'model.bnet', metadata['input-names'])
            reduced, steps = reduce_symbolic(original, policy)
            after = classify(reduced)
            certificate = certify(folder / 'model.bnet', original, reduced, steps)
            if certificate['status'] == 'sat':
                raise AssertionError('SMT found a counterexample to fixed-point preservation')
            roots = {f'final:{n}': f for n, f in reduced.functions.items()}
            roots.update({f'step:{i}:{n}': f for i, (n, f) in enumerate(steps)})
            original.bdd.dump(str(output / f'{policy}.bdd.json'), roots=roots)
            # Bound human-readable output, never the authoritative BDD artifact.
            rules = {n: readable(original.bdd, f) if f.dag_size <= 100 else '[see BDD artifact]'
                     for n, f in reduced.functions.items()}
            trace = [{'node': n, 'support': sorted(f.support),
                      'function': readable(original.bdd, f) if f.dag_size <= 100 else '[see BDD artifact]'} for n, f in steps]
            fp = fixed_point_summary(reduced, limit=256)
            write(destination, {'algorithm_version': ALGORITHM_VERSION, 'id': ident, 'name': metadata['name'], 'policy': policy, 'seed': 42,
                                'status': 'complete', 'before_nodes': len(original.functions),
                                'after': after, 'all_rules_after': classify(reduced, True),
                                'certificate': certificate, 'fixed_points': fp, 'rules': rules,
                                'steps': trace, 'seconds': perf_counter() - start})
            print(f'{ident} {policy}: {len(original.functions)} -> {len(reduced.functions)}; uniform={after["out_uniform"]}; cert={certificate["status"]}', flush=True)
        except Exception as error:
            write(destination, {'id': ident, 'policy': policy, 'status': 'error', 'error': repr(error)})
            print(f'{ident} {policy}: ERROR {error}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--dataset', choices=('cellcollective', 'live'), default='cellcollective')
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.dataset)
        return
    output = ROOT / 'results' / ('catalogue' if args.dataset == 'cellcollective' else 'live')
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'data' / args.dataset / 'manifest.json').read_text())

    def run(model):
        ident = model['id']
        scratch = ROOT / 'tmp/catalogue/workers' / args.dataset / ident
        scratch.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', ident, '--dataset', args.dataset], cwd=scratch,
                                    capture_output=True, text=True, timeout=args.timeout)
            print(result.stdout, end='', flush=True)
            if result.returncode:
                write(output / f'{ident}_failure.json', {'id': ident, 'status': 'process_error', 'error': result.stderr[-4000:]})
            elif (output / f'{ident}_failure.json').exists():
                write(output / f'{ident}_failure.json', {'id': ident, 'status': 'resolved', 'returncode': 0})
            return {'id': ident, 'returncode': result.returncode}
        except subprocess.TimeoutExpired:
            write(output / f'{ident}_failure.json', {'id': ident, 'status': 'timeout', 'seconds': args.timeout})
            print(f'{ident}: timeout; completed checkpoints retained', flush=True)
            return {'id': ident, 'status': 'timeout'}

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(run, manifest['models']))
    import importlib.metadata
    write(output / 'environment.json', {'python': sys.version, 'source_commit': manifest['commit'],
          'packages': {p: importlib.metadata.version(p) for p in ('dd', 'z3-solver')},
          'policies': POLICIES, 'seed': 42, 'seconds_per_model_limit': args.timeout,
          'min_growth_definition': 'sum of estimated essential support size changes; not the pilot trial-table cost',
          'outcomes': outcomes,
          'code_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT / 'src').rglob('*.py'))}})


if __name__ == '__main__':
    main()
