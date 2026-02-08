"""Symbolic Collapse Score Verifier"""
from sympy import isprime, binomial

DEFAULT_WINDOW = 128
DEFAULT_THRESHOLD = 0.95

def collapse_score(p, window=DEFAULT_WINDOW):
    """Compute symbolic collapse score for candidate p.
    Tests C(p,k) mod p == 0 for k=1..window.
    By Lucas' theorem, this should be 1.0 for any prime p > window.
    """
    if p < 2:
        return 0.0
    hits = 0
    T = min(window, p - 1)  # Can't test beyond p-1
    for k in range(1, T + 1):
        if binomial(p, k) % p == 0:
            hits += 1
    return hits / T if T > 0 else 0.0

def verify_safe_prime(p, window=DEFAULT_WINDOW, threshold=DEFAULT_THRESHOLD):
    """Full verification of a safe prime candidate.
    Returns dict with scores, primality checks, and pass/fail.
    """
    q = (p - 1) // 2
    
    # Check basic structure
    if p < 5 or p % 2 == 0:
        return {
            'p': p,
            'q': q,
            'is_safe_prime': False,
            'score_p': 0.0,
            'score_q': 0.0,
            'symbolic_pass': False,
            'fallback_ok': False,
            'verified': False,
            'reason': 'Invalid candidate (too small or even)'
        }
    
    # Cryptographic primality check (Baillie-PSW via sympy)
    p_is_prime = isprime(p)
    q_is_prime = isprime(q)
    fallback_ok = p_is_prime and q_is_prime and (2 * q + 1 == p)
    
    # Symbolic collapse scores
    score_p = collapse_score(p, window)
    score_q = collapse_score(q, window)
    symbolic_pass = score_p >= threshold and score_q >= threshold
    
    return {
        'p': p,
        'q': q,
        'is_safe_prime': fallback_ok,
        'score_p': round(score_p, 6),
        'score_q': round(score_q, 6),
        'symbolic_pass': symbolic_pass,
        'fallback_ok': fallback_ok,
        'verified': fallback_ok and symbolic_pass,
        'window': window,
        'threshold': threshold,
    }

def batch_verify(candidates, window=DEFAULT_WINDOW, threshold=DEFAULT_THRESHOLD):
    """Verify a batch of candidates. Returns list of results."""
    return [verify_safe_prime(p, window, threshold) for p in candidates]
