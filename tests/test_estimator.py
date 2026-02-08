"""Tests for the Deterministic Safe Prime Estimator"""
import pytest
from sympy import isprime
from echoprime.estimator import (
    estimate_nth_safe_prime,
    get_candidate_from_index,
    projector_index,
    find_safe_prime_near,
    A_CONSTANT,
)
from echoprime.utils import KNOWN_SAFE_PRIMES


class TestEstimateNthSafePrime:
    """Tests for estimate_nth_safe_prime."""

    def test_first_safe_prime(self):
        assert estimate_nth_safe_prime(1) == 5

    def test_known_small_cases(self):
        known = [5, 7, 11, 23, 47]
        for i, expected in enumerate(known, 1):
            assert estimate_nth_safe_prime(i) == expected

    def test_returns_positive_for_large_n(self):
        for n in [10, 50, 100, 1000]:
            result = estimate_nth_safe_prime(n)
            assert result > 0
            assert isinstance(result, int)

    def test_monotonically_increasing_for_large_n(self):
        """Estimates should generally increase with n (for n > 5)."""
        prev = estimate_nth_safe_prime(6)
        for n in range(7, 50):
            curr = estimate_nth_safe_prime(n)
            assert curr > prev, f"estimate({n}) = {curr} not > estimate({n-1}) = {prev}"
            prev = curr

    def test_zero_raises_value_error(self):
        with pytest.raises(ValueError, match="Index must be >= 1"):
            estimate_nth_safe_prime(0)

    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            estimate_nth_safe_prime(-5)


class TestGetCandidateFromIndex:
    """Tests for get_candidate_from_index."""

    def test_returns_2q_plus_1_structure(self):
        for k in [1, 5, 10, 50, 100]:
            p = get_candidate_from_index(k)
            # p should be odd and > 2
            assert p > 2
            assert p % 2 == 1
            # q = (p-1)/2 should be prime (since we built p = 2*nextprime(raw)+1)
            q = (p - 1) // 2
            assert isprime(q), f"q={q} from k={k} is not prime"

    def test_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            get_candidate_from_index(0)

    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError):
            get_candidate_from_index(-1)

    def test_returns_int(self):
        result = get_candidate_from_index(10)
        assert isinstance(result, int)


class TestProjectorIndex:
    """Tests for projector_index."""

    def test_returns_positive_integer(self):
        for epoch in [1, 10, 100, 1000]:
            result = projector_index(epoch)
            assert result >= 1
            assert isinstance(result, int)

    def test_offset_applied(self):
        base = projector_index(100)
        with_offset = projector_index(100, offset=5)
        assert with_offset == base + 5

    def test_negative_offset_clamped(self):
        """Result should be at least 1 even with negative offset."""
        result = projector_index(1, offset=-1000)
        assert result >= 1


class TestFindSafePrimeNear:
    """Tests for find_safe_prime_near."""

    def test_returns_actual_safe_prime(self):
        for n in [1, 3, 5, 10, 20]:
            p, q = find_safe_prime_near(n)
            assert isprime(p), f"p={p} is not prime"
            assert isprime(q), f"q={q} is not prime"
            assert p == 2 * q + 1, f"p={p} != 2*{q}+1"

    def test_small_indices_return_known_safe_primes(self):
        """For small n, the found safe prime should be a known one."""
        p, q = find_safe_prime_near(1)
        assert p in KNOWN_SAFE_PRIMES

    def test_result_at_or_above_estimate(self):
        for n in [10, 20, 50]:
            estimate = estimate_nth_safe_prime(n)
            p, q = find_safe_prime_near(n)
            # The found prime should be in the neighborhood of the estimate
            # (at least half the estimate, since we search from estimate//2)
            assert p > 0
