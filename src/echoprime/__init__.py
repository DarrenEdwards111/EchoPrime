"""
EchoPrime Protocol SDK
Copyright (c) 2025 Mikoshi Ltd.
Licensed under the MIT License.

Deterministic safe prime oracle and cryptographic primitive.
"""

from .estimator import (
    estimate_nth_safe_prime,
    get_candidate_from_index,
    projector_index,
    find_safe_prime_near,
    A_CONSTANT,
)
from .verifier import (
    verify_safe_prime,
    collapse_score,
    batch_verify,
)
from .oracle import (
    create_trace,
    format_for_contract,
    export_traces,
)
from .utils import (
    KNOWN_SAFE_PRIMES,
    is_safe_prime,
)

__version__ = '1.0.0'
__author__ = 'Mikoshi Ltd'
__email__ = 'mikoshiuk@gmail.com'

__all__ = [
    'estimate_nth_safe_prime',
    'get_candidate_from_index',
    'projector_index',
    'find_safe_prime_near',
    'verify_safe_prime',
    'collapse_score',
    'batch_verify',
    'create_trace',
    'format_for_contract',
    'export_traces',
    'KNOWN_SAFE_PRIMES',
    'is_safe_prime',
    'A_CONSTANT',
]
