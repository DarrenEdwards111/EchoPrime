"""Integration tests for the full EchoPrime pipeline"""
import hashlib
import pytest
from sympy import isprime
from echoprime.estimator import estimate_nth_safe_prime, find_safe_prime_near
from echoprime.verifier import verify_safe_prime
from echoprime.oracle import create_trace, format_for_contract
from echoprime.utils import KNOWN_SAFE_PRIMES, is_safe_prime


class TestFullPipeline:
    """Test the complete pipeline: index → estimate → find → verify → trace."""

    def test_single_pipeline(self):
        """Run the full pipeline for a single index."""
        n = 10
        # Step 1: Estimate
        estimate = estimate_nth_safe_prime(n)
        assert estimate > 0

        # Step 2: Find safe prime near estimate
        p, q = find_safe_prime_near(n)
        assert isprime(p)
        assert isprime(q)
        assert p == 2 * q + 1

        # Step 3: Verify
        result = verify_safe_prime(p)
        assert result['verified'] is True
        assert result['is_safe_prime'] is True
        assert result['score_p'] == 1.0

        # Step 4: Create trace
        trace = create_trace(
            index=n,
            p=p,
            q=q,
            score_p=result['score_p'],
            score_q=result['score_q'],
            verified=result['verified'],
        )
        assert trace['version'] == '1.0.0'
        assert trace['verified'] is True
        assert 'hash' in trace

    def test_trace_hash_consistency(self):
        """Verify that trace hash is deterministic for same inputs."""
        p, q = 47, 23
        trace1 = create_trace(1, p, q, 1.0, 1.0, True)
        # Recompute hash manually
        trace_data = f"1:{p}:{q}:{1.0}:{1.0}:{True}"
        expected_hash = hashlib.sha256(trace_data.encode()).hexdigest()
        assert trace1['hash'] == expected_hash

    def test_format_for_contract(self):
        """Test contract formatting."""
        trace = create_trace(1, 47, 23, 1.0, 1.0, True)
        contract_data = format_for_contract(trace)
        assert contract_data[0] == 1        # index
        assert contract_data[1] == 47       # p
        assert contract_data[2] == 23       # q
        assert contract_data[3] == 10000    # score_p * 10000
        assert contract_data[4] == 10000    # score_q * 10000
        assert contract_data[5] is True     # verified
        assert isinstance(contract_data[6], bytes)  # hash

    def test_first_20_indices(self):
        """Run pipeline for first 20 indices — all should produce valid safe primes."""
        for n in range(1, 21):
            p, q = find_safe_prime_near(n)
            assert isprime(p), f"Index {n}: p={p} not prime"
            assert isprime(q), f"Index {n}: q={q} not prime"
            assert p == 2 * q + 1, f"Index {n}: p != 2q+1"

            result = verify_safe_prime(p)
            assert result['verified'] is True, f"Index {n}: p={p} failed verification"


class TestKnownSafePrimes:
    """Validate the known safe primes list."""

    def test_all_known_are_safe_primes(self):
        """Every entry in KNOWN_SAFE_PRIMES should actually be a safe prime."""
        for p in KNOWN_SAFE_PRIMES:
            assert is_safe_prime(p), f"{p} is not a safe prime"

    def test_known_list_sorted(self):
        """List should be sorted ascending."""
        for i in range(len(KNOWN_SAFE_PRIMES) - 1):
            assert KNOWN_SAFE_PRIMES[i] < KNOWN_SAFE_PRIMES[i + 1]

    def test_known_list_length(self):
        """Should have exactly 100 known safe primes."""
        assert len(KNOWN_SAFE_PRIMES) == 100


class TestBulkVerification:
    """Bulk verification across multiple indices."""

    def test_100_indices(self):
        """Run 100 indices through find_safe_prime_near and verify all are valid."""
        for n in range(1, 101):
            p, q = find_safe_prime_near(n)
            assert isprime(p), f"Index {n}: p={p} not prime"
            assert isprime(q), f"Index {n}: q={q} not prime"
            assert p == 2 * q + 1, f"Index {n}: safe prime structure violated"
