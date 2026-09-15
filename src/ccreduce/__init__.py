"""Exact, dependency-free reference implementation of Boolean reduction."""
from .boolean import Function, Network
from .reduction import reduce_network

__all__ = ['Function', 'Network', 'reduce_network']
