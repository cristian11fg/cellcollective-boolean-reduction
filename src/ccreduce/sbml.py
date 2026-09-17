"""Strict Boolean SBML-qual importer using species IDs, preserving duplicate names.

Only Boolean function terms with default 0 and result 1 are accepted. Unsupported
semantics fail explicitly instead of silently imposing a Booleanization.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

Q = '{http://www.sbml.org/sbml/level3/version1/qual/version1}'
M = '{http://www.w3.org/1998/Math/MathML}'


def sbml_to_bnet(path):
    root = ET.parse(path).getroot()
    species = {s.attrib[Q + 'id']: s.attrib for s in root.iter(Q + 'qualitativeSpecies')}
    if not species:
        raise ValueError('No SBML-qual species')
    if any(a.get(Q + 'maxLevel', '1') != '1' for a in species.values()):
        raise ValueError('Non-Boolean maxLevel')
    identifiers = {sid: 'v_' + sid for sid in species}
    if any(not v.isidentifier() for v in identifiers.values()):
        raise ValueError('Unsupported species identifier')

    def math(node):
        tag = node.tag.removeprefix(M)
        if tag == 'math' and len(node) == 1:
            return math(node[0])
        if tag == 'ci':
            return identifiers[node.text.strip()]
        if tag == 'cn' and node.text.strip() in ('0', '1'):
            return node.text.strip()
        if tag in ('true', 'false'):
            return '1' if tag == 'true' else '0'
        if tag != 'apply' or len(node) < 2:
            raise ValueError(f'Unsupported MathML {tag}')
        op = node[0].tag.removeprefix(M)
        args = [math(child) for child in node[1:]]
        if op in ('and', 'or', 'xor'):
            return '(' + {'and': ' & ', 'or': ' | ', 'xor': ' ^ '}[op].join(args) + ')'
        if op == 'not' and len(args) == 1:
            return '!(' + args[0] + ')'
        if len(args) == 2:
            a, b = args
            # Comparisons over {0,1}; simplify common threshold comparisons.
            if op == 'eq' and b == '1':
                return a
            if op == 'eq' and b == '0':
                return f'!({a})'
            if op == 'eq':
                return f'!(({a}) ^ ({b}))'
            if op == 'neq':
                return f'(({a}) ^ ({b}))'
            if op == 'geq':
                return f'(({a}) | !({b}))'
            if op == 'leq':
                return f'(!({a}) | ({b}))'
            if op == 'gt':
                return f'(({a}) & !({b}))'
            if op == 'lt':
                return f'(!({a}) & ({b}))'
        raise ValueError(f'Unsupported Boolean MathML operator {op}')

    rules = {}
    for transition in root.iter(Q + 'transition'):
        outputs = list(transition.iter(Q + 'output'))
        terms = transition.find(Q + 'listOfFunctionTerms')
        if terms is None or len(outputs) != 1:
            raise ValueError('Expected one output and explicit function terms')
        output = outputs[0]
        if output.attrib.get(Q + 'transitionEffect') != 'assignmentLevel':
            raise ValueError('Unsupported transition effect')
        sid = output.attrib[Q + 'qualitativeSpecies']
        if sid in rules:
            raise ValueError('Multiple transitions for one species')
        default = terms.find(Q + 'defaultTerm')
        if default is None or default.attrib.get(Q + 'resultLevel') != '0':
            raise ValueError('Only default result 0 supported')
        parts = []
        for term in terms.findall(Q + 'functionTerm'):
            if term.attrib.get(Q + 'resultLevel') != '1':
                raise ValueError('Only Boolean positive function terms supported')
            parts.append(math(term.find(M + 'math')))
        rules[sid] = ' | '.join(f'({p})' for p in parts) or '0'
    inputs, fixed = [], {}
    for sid, attributes in species.items():
        if sid in rules:
            if attributes.get(Q + 'constant') == 'true':
                raise ValueError('Constant species with a transition')
            continue
        if attributes.get(Q + 'constant') != 'true':
            raise ValueError(f'No rule for nonconstant species {sid}')
        if attributes.get(Q + 'initialLevel') in ('0', '1'):
            fixed[sid] = int(attributes[Q + 'initialLevel'])
            rules[sid] = str(fixed[sid])
        elif Q + 'initialLevel' not in attributes:
            inputs.append(identifiers[sid])
        else:
            raise ValueError('Non-Boolean initial level')
    bnet = 'targets,factors\n' + '\n'.join(f'{identifiers[s]}, {r}' for s, r in rules.items()) + '\n'
    return bnet, {'input-names': inputs, 'variable-names': [identifiers[s] for s in rules],
                  'output-names': [], 'sbml_species': {identifiers[s]: {'id': s, 'name': a.get(Q + 'name'),
                                         'compartment': a.get(Q + 'compartment')} for s, a in species.items()},
                  'sbml_fixed_components': {identifiers[s]: v for s, v in fixed.items()}}
