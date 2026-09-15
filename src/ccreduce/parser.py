"""Strict bnet reader. No eval, implicit inputs, or stochastic interpretation."""
import ast
from pathlib import Path
from .boolean import Function, Network


def parse_expression(expression, max_support=16):
    tree = ast.parse(expression.replace('!', '~').strip(), mode='eval').body
    def check(node):
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value in (0, 1):
            return set()
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            return check(node.operand)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor)):
            return check(node.left) | check(node.right)
        raise ValueError(f'Unsupported Boolean syntax: {ast.dump(node)}')
    names = check(tree)
    def value(node, s):
        if isinstance(node, ast.Name):
            return s[node.id]
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp):
            return 1 - value(node.operand, s)
        a, b = value(node.left, s), value(node.right, s)
        return a & b if isinstance(node.op, ast.BitAnd) else a | b if isinstance(node.op, ast.BitOr) else a ^ b
    return Function.build(names, lambda s: value(tree, s), max_support)


def read_bnet(path, inputs=(), max_support=16):
    functions = {}
    for line_number, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        line = line.split('#', 1)[0].strip()
        if not line or line.replace(' ', '').lower() == 'targets,factors':
            continue
        if ',' not in line:
            raise ValueError(f'Line {line_number}: expected target, expression')
        name, expression = map(str.strip, line.split(',', 1))
        if not name.isidentifier() or name in functions:
            raise ValueError(f'Invalid or duplicate target: {name}')
        functions[name] = parse_expression(expression, max_support)
    for name in inputs:
        identity = Function((name,), (0, 1))
        if name in functions and functions[name] != identity:
            raise ValueError(f'Input {name} has a nonidentity rule; review source semantics')
        functions[name] = identity
    return Network(functions, frozenset(inputs))
