"""Tests for the Symbolic Collapse Score Verifier"""
import pytest
from sympy import isprime
from echoprime.verifier import (
    collapse_score,
    verify_safe_prime,
    batch_verify,
    DEFAULT_WINDOW,
    DEFAULT_THRESHOLD,
)
from echoprime.utils import KNOWN_SAFE_PRIMES


class TestCollapseScore:
    """Tests for collapse_score."""

    def test_primes_above_window_score_one(self):
        """By Lucas' theorem, C(p,k) ≡ 0 mod p for all 1 <= k <= T when p > T."""
        # Use primes well above 128
        for p in [131, 137, 139, 149, 151, 157, 503, 1019]:
            score = collapse_score(p, window=128)
            assert score == 1.0, f"collapse_score({p}) = {score}, expected 1.0"

    def test_small_primes_score(self):
        """Small primes should still get high scores (all C(p,k) mod p == 0 for 1<=k<p)."""
        # For prime p, C(p,k) mod p == 0 for 1 <= k <= p-1
        # So for p=5, window=128: T=min(128,4)=4, all 4 hit → score=1.0
        assert collapse_score(5, window=128) == 1.0
        assert collapse_score(7, window=128) == 1.0
        assert collapse_score(11, window=128) == 1.0

    def test_composite_score_less_than_one(self):
        """Composites should not achieve perfect collapse scores."""
        composites = [4, 6, 8, 9, 10, 12, 15, 21, 100, 1000]
        for c in composites:
            score = collapse_score(c, window=128)
            assert score < 1.0, f"collapse_score({c}) = {score}, expected < 1.0"

    def test_score_zero_for_invalid(self):
        assert collapse_score(0) == 0.0
        assert collapse_score(1) == 0.0
        assert collapse_score(-5) == 0.0

    def test_custom_window(self):
        score_small = collapse_score(251, window=10)
        score_large = collapse_score(251, window=128)
        # Both should be 1.0 for a prime > both windows
        assert score_small == 1.0
        assert score_large == 1.0


class TestVerifySafePrime:
    """Tests for verify_safe_prime."""

    def test_known_safe_primes_pass(self):
        """All known safe primes should pass full verification."""
        test_primes = [5, 7, 11, 23, 47, 59, 83, 107]
        for p in test_primes:
            result = verify_safe_prime(p)
            assert result['is_safe_prime'] is True, f"p={p} failed is_safe_prime"
            assert result['fallback_ok'] is True, f"p={p} failed fallback_ok"
            assert result['verified'] is True, f"p={p} failed verified"
            assert result['score_p'] == 1.0, f"p={p} score_p={result['score_p']}"

    def test_composite_fails(self):
        """Composite numbers should fail verification."""
        composites = [4, 6, 9, 15, 100, 1000]
        for c in composites:
            result = verify_safe_prime(c)
            assert result['verified'] is False or result.get('is_safe_prime') is False, \
                f"Composite {c} incorrectly passed"

    def test_even_numbers_rejected(self):
        result = verify_safe_prime(4)
        assert result['is_safe_prime'] is False
        assert 'reason' in result

    def test_small_numbers_rejected(self):
        result = verify_safe_prime(2)
        assert result['is_safe_prime'] is False

    def test_prime_but_not_safe_prime(self):
        """A prime p where (p-1)/2 is not prime should fail."""
        # 13 is prime but (13-1)/2 = 6 is not prime
        result = verify_safe_prime(13)
        assert result['is_safe_prime'] is False
        assert result['fallback_ok'] is False

    def test_non_prime_of_form_2q_plus_1(self):
        """If p = 2q+1 where q is prime but p is not, should fail."""
        # q=7 is prime, p=15 is not prime
        result = verify_safe_prime(15)
        assert result['is_safe_prime'] is False
        assert result['fallback_ok'] is False

    def test_result_contains_all_fields(self):
        result = verify_safe_prime(47)
        expected_keys = {'p', 'q', 'is_safe_prime', 'score_p', 'score_q',
                         'symbolic_pass', 'fallback_ok', 'verified', 'window', 'threshold'}
        assert expected_keys.issubset(set(result.keys()))

    def test_large_safe_prime(self):
        """Test with a larger known safe prime."""
        result = verify_safe_prime(1019)
        assert result['verified'] is True
        assert result['score_p'] == 1.0
        assert result['score_q'] == 1.0


class TestBatchVerify:
    """Tests for batch_verify."""

    def test_batch_returns_list(self):
        results = batch_verify([5, 7, 11])
        assert isinstance(results, list)
        assert len(results) == 3

    def test_batch_all_safe_primes(self):
        results = batch_verify([5, 7, 11, 23, 47])
        for r in results:
            assert r['verified'] is True

    def test_batch_mixed(self):
        results = batch_verify([5, 6, 7, 8])
        assert results[0]['verified'] is True  # 5 is safe prime
        assert results[1]['verified'] is False or results[1].get('is_safe_prime') is False  # 6
        assert results[2]['verified'] is True  # 7 is safe prime
        assert results[3]['verified'] is False or results[3].get('is_safe_prime') is False  # 8

    def test_batch_empty(self):
        results = batch_verify([])
        assert results == []
