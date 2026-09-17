"""Rebuild auditable census tables and candidate lists from completed records."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICIES = ('first', 'min_degree', 'min_growth', 'random')
PROPERTIES = {
    'out_uniform': 'Uniforme respecto de NOT (incluye casos vacíos)',
    'out_uniform_nonvacuous': 'Uniforme NOT con alguna regla interna no constante',
    'AND_OR_NOT_out_uniform': 'MIN/MAX (AND/OR/NOT) y out-uniform',
    'AND_OR_NAND_NOR_out_uniform': 'AND/OR/NAND/NOR y out-uniform',
    'homogeneous_MIN': 'Homogénea MIN y uniforme NOT',
    'homogeneous_MAX': 'Homogénea MAX y uniforme NOT',
    'homogeneous_gate': 'Una misma puerta en todas las reglas no constantes',
    'positive_AND': 'AND positiva', 'positive_OR': 'OR positiva',
    'affine': 'Afín (ecuaciones lineales sobre F2)',
    'MIN_MAX': 'MIN/MAX sin exigir uniformidad NOT',
    'locally_unate': 'Cada regla es unate (condición local)',
    'vacuous': 'Sin reglas internas no constantes',
}


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', choices=('cellcollective', 'live'), default='live')
    args = parser.parse_args()
    suffix = 'catalogue' if args.dataset == 'cellcollective' else 'live'
    output = ROOT / 'results' / suffix
    manifest = read(ROOT / 'data' / args.dataset / 'manifest.json')
    before, after, rows, candidates = {}, {}, [], []
    for model in manifest['models']:
        ident = model['id']
        folder = output / ident
        bpath = folder / 'before.json'
        b = read(bpath) if bpath.exists() else None
        if b:
            before[ident] = b['classification']
        for policy in POLICIES:
            path = folder / f'{policy}.json'
            a = read(path) if path.exists() else {'status': 'missing'}
            row = {'id': ident, 'name': model['name'], 'policy': policy, 'status': a['status']}
            if b:
                row.update({f'before_{k}': v for k, v in b['classification'].items() if isinstance(v, (int, bool, str))})
            if a['status'] == 'complete':
                after.setdefault(ident, {})[policy] = a
                row.update({f'after_{k}': v for k, v in a['after'].items() if isinstance(v, (int, bool, str))})
                row['bijection_verified'] = a['certificate']['bijection_verified']
                row['fixed_points_exact'] = a['fixed_points']['exact']
                row['fixed_points_count_or_lower_bound'] = a['fixed_points'].get('count', a['fixed_points'].get('lower_bound'))
                row['all_rules_out_uniform'] = a['all_rules_after']['out_uniform']
                p = a['after']
                if (p['AND_OR_NOT_out_uniform'] or p['affine'] or p['positive_AND'] or p['positive_OR']) and a['steps']:
                    candidates.append({'id': ident, 'name': model['name'], 'policy': policy,
                                       'before_nodes': a['before_nodes'], 'after_nodes': p['nodes'],
                                       'inputs': p['inputs'], 'nonconstant_internal': p['nonconstant_rules'],
                                       'MIN': p['homogeneous_MIN'], 'MAX': p['homogeneous_MAX'],
                                       'affine': p['affine'], 'positive_AND': p['positive_AND'], 'positive_OR': p['positive_OR'],
                                       'reciprocal_support': p['reciprocal_support'],
                                       'all_rules_uniform': a['all_rules_after']['out_uniform'],
                                       'certificate': a['certificate']['bijection_verified'],
                                       'fixed_points': a['fixed_points'].get('count'), 'rules': a['rules']})
            else:
                row['error'] = a.get('error', 'No completed result')
            rows.append(row)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    counts = {key: {'before': sum(b[key] for b in before.values()),
                    'after_first': sum(a['first']['after'][key] for a in after.values() if 'first' in a),
                    'after_any_policy': sum(any(v['after'][key] for v in a.values()) for a in after.values()),
                    'models_any_before': len({ident.split('_')[0] for ident, b in before.items() if b[key]}),
                    'models_any_after': len({ident.split('_')[0] for ident, a in after.items() if any(v['after'][key] for v in a.values())})}
              for key in PROPERTIES}
    summary = {'source': args.dataset, 'instances': len(manifest['models']), 'classified_before': len(before),
               'complete_runs': sum(len(a) for a in after.values()), 'expected_runs': len(manifest['models']) * len(POLICIES),
               'first_complete': sum('first' in a for a in after.values()),
               'instances_any_complete': len(after), 'counts': counts,
               'certified_runs': sum(v['certificate']['bijection_verified'] for a in after.values() for v in a.values()),
               'failures': [r for r in rows if r['status'] != 'complete']}
    (output / 'counts.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (output / 'candidates.json').write_text(json.dumps(candidates, indent=2), encoding='utf-8')
    title = 'Cell Collective: catálogo público directo' if args.dataset == 'live' else 'Cell Collective: instancias archivadas en BBM'
    lines = [f'# {title}', '',
             f'Instancias recuperadas: **{summary["instances"]}**; clasificadas antes: **{len(before)}**. '
             f'Reducciones completas: **{summary["complete_runs"]}/{summary["expected_runs"]}**; '
             f'certificados SMT: **{summary["certified_runs"]}**.', '',
             'Los recuentos son por instancia/version, no por ejecución. «Algún orden» significa al menos uno de los '
             'cuatro órdenes probados; un resultado negativo no prueba imposibilidad para todos los órdenes.', '',
             'Las entradas se conservan como parámetros libres. La tabla principal excluye sus identidades artificiales '
             'del censo de signos. Los JSON incluyen también el análisis de todas las reglas, con esas identidades.', '',
             'Se admiten constantes en las familias. Las familias MIN/MAX, de puertas y afines exigen al menos una regla '
             'interna no constante; las redes vacías/solo entradas/solo constantes tienen fila propia.', '',
             '| Propiedad | Original | Reducida: first | Reducida: algún orden |',
             '|---|---:|---:|---:|']
    for key, label in PROPERTIES.items():
        c = counts[key]
        lines.append(f'| {label} | {c["before"]} | {c["after_first"]} | {c["after_any_policy"]} |')
    lines += ['', '## Candidatos con reducción efectiva', '',
              'La pertenencia a una familia no certifica por sí sola todas las hipótesis de un teorema. '
              'Hay que revisar las entradas, los bucles y la reciprocidad antes de aplicar resultados sobre grafos no dirigidos.', '',
              '| ID | Nombre | Orden | Nodos antes → después | Entradas | MIN | MAX | Afín | PF exactos |',
              '|---|---|---|---:|---:|---|---|---|---:|']
    best = {}
    for c in sorted(candidates, key=lambda c: (not (c['MIN'] or c['MAX']), c['after_nodes'], c['inputs'], c['id'], c['policy'])):
        best.setdefault(c['id'], c)
    for c in best.values():
        lines.append(f'| {c["id"]} | {c["name"]} | {c["policy"]} | {c["before_nodes"]} → {c["after_nodes"]} | {c["inputs"]} | {c["MIN"]} | {c["MAX"]} | {c["affine"]} | {c["fixed_points"] if c["fixed_points"] is not None else "pendiente"} |')
    lines += ['', '## Funciones de los candidatos', '']
    for c in best.values():
        lines += [f'### {c["id"]}: {c["name"]} ({c["policy"]})', '',
                  '```text', *[f'{n} = {f}' for n, f in c['rules'].items()], '```', '',
                  f'Traza y certificado: [{c["policy"]}.json](../results/{suffix}/{c["id"]}/{c["policy"]}.json).', '']
    lines += ['## Cobertura y reproducibilidad', '',
              f'[Manifiesto](../data/{args.dataset}/manifest.json), [tabla completa](../results/{suffix}/summary.csv), '
              f'[recuentos](../results/{suffix}/counts.json), [entorno](../results/{suffix}/environment.json).', '',
              'La enumeración SMT de puntos fijos se limita a 256 soluciones por ejecución: «pendiente» no significa cero. '
              'La equivalencia de los conjuntos de puntos fijos se comprueba por separado, sin enumerarlos.', '',
              '## Ejecuciones incompletas', '']
    lines += [f'- {r["id"]}, {r["policy"]}: {r.get("error")}' for r in summary['failures']] or ['Ninguna.']
    (ROOT / 'docs' / f'censo_{suffix}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('counts', 'failures')}, indent=2))
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
