"""Utility functions"""
import time

# First 100 known safe primes for validation
KNOWN_SAFE_PRIMES = [
    5, 7, 11, 23, 47, 59, 83, 107, 167, 179,
    227, 263, 347, 359, 383, 467, 479, 503, 563, 587,
    719, 839, 863, 887, 983, 1019, 1187, 1283, 1307, 1319,
    1367, 1439, 1487, 1523, 1619, 1823, 1907, 2027, 2039, 2063,
    2099, 2207, 2447, 2459, 2579, 2819, 2879, 2903, 2963, 2999,
    3023, 3119, 3167, 3203, 3467, 3623, 3779, 3803, 3863, 3947,
    4007, 4079, 4127, 4139, 4259, 4283, 4547, 4679, 4703, 4787,
    4799, 4919, 5039, 5099, 5387, 5399, 5483, 5507, 5639, 5807,
    5879, 5927, 5939, 6047, 6599, 6659, 6719, 6779, 6827, 6899,
    6983, 7079, 7187, 7247, 7349, 7457, 7487, 7523, 7559, 7607,
]

def is_safe_prime(p):
    """Quick check if p is a safe prime."""
    from sympy import isprime
    if not isprime(p):
        return False
    q = (p - 1) // 2
    return isprime(q)

def timer(func):
    """Decorator to time function execution."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed
    return wrapper
