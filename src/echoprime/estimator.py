"""Deterministic Safe Prime Estimator"""
import math
from sympy import nextprime, isprime

# Empirically fitted constant from Bateman-Horn heuristic
A_CONSTANT = 2.8913

def estimate_nth_safe_prime(n):
    """Estimate the n-th safe prime using analytic projection.
    p_n ≈ a · n · (log n)²
    """
    if n < 1:
        raise ValueError("Index must be >= 1")
    if n <= 5:
        # Small cases: return known safe primes directly
        known = [5, 7, 11, 23, 47]
        return known[n-1]
    ln_n = math.log(n)
    estimate = int(A_CONSTANT * n * ln_n * ln_n)
    return estimate

def get_candidate_from_index(k):
    """Get a safe prime candidate from deterministic index k.
    Projects k to a region and finds the next prime q, then p = 2q + 1.
    """
    if k < 1:
        raise ValueError("Index must be >= 1")
    ln_k = math.log(max(k, 2))
    raw = int(A_CONSTANT * k * ln_k * ln_k)
    q = int(nextprime(raw))
    p = 2 * q + 1
    return p

def projector_index(epoch_n, offset=0):
    """Map an epoch number to a starting lattice index.
    For large epochs, scales the search space appropriately.
    """
    ln_n = math.log(max(epoch_n, 2))
    k_start = int(epoch_n / (A_CONSTANT * ln_n * ln_n))
    return max(1, k_start + offset)

def find_safe_prime_near(n):
    """Find the nearest safe prime at or above the estimate for index n."""
    estimate = estimate_nth_safe_prime(n)
    # Search forward from estimate
    q_candidate = int(nextprime(estimate // 2))
    attempts = 0
    max_attempts = 10000
    while attempts < max_attempts:
        p = 2 * q_candidate + 1
        if isprime(p):
            return p, q_candidate
        q_candidate = int(nextprime(q_candidate))
        attempts += 1
    raise RuntimeError(f"No safe prime found after {max_attempts} attempts from index {n}")
