# EchoPrime 🔐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/DarrenEdwards111/echoprime)

**Deterministic safe prime oracle and cryptographic primitive.**

EchoPrime provides a deterministic method for estimating, locating, and verifying safe primes using an analytic projection based on the Bateman-Horn heuristic. It includes a symbolic collapse score verifier and an oracle trace format for on-chain publication.

## Key Features

- **Analytic Estimator** — Projects the n-th safe prime location using `p_n ≈ a · n · (log n)²` with empirically fitted constant `a ≈ 2.8913`
- **Symbolic Collapse Verifier** — Verifies primes using binomial coefficient divisibility (Lucas' theorem)
- **Safe Prime Finder** — Deterministic search from estimated regions
- **Oracle Traces** — SHA-256 hashed records for on-chain publication
- **Ethereum Contract Format** — Ready-to-submit tuple format for smart contracts

## Installation

```bash
pip install echoprime
```

Or from source:

```bash
git clone https://github.com/DarrenEdwards111/echoprime.git
cd echoprime
pip install -e .
```

## Quick Start

```python
from echoprime import (
    estimate_nth_safe_prime,
    find_safe_prime_near,
    verify_safe_prime,
    create_trace,
)

# Estimate where the 100th safe prime lives
estimate = estimate_nth_safe_prime(100)
print(f"Estimate for index 100: {estimate}")

# Find the actual safe prime near that estimate
p, q = find_safe_prime_near(100)
print(f"Found safe prime p={p}, Sophie Germain q={q}")

# Verify with symbolic collapse scoring
result = verify_safe_prime(p)
print(f"Verified: {result['verified']}")
print(f"Collapse score (p): {result['score_p']}")
print(f"Collapse score (q): {result['score_q']}")

# Create oracle trace for on-chain publication
trace = create_trace(
    index=100, p=p, q=q,
    score_p=result['score_p'],
    score_q=result['score_q'],
    verified=result['verified'],
)
print(f"Trace hash: {trace['hash']}")
```

## API Reference

### Estimator (`echoprime.estimator`)

| Function | Description |
|---|---|
| `estimate_nth_safe_prime(n)` | Estimate the n-th safe prime: `p_n ≈ a · n · (log n)²` |
| `find_safe_prime_near(n)` | Find actual safe prime at/above the estimate for index n |
| `get_candidate_from_index(k)` | Get a candidate `p = 2·nextprime(raw)+1` from index k |
| `projector_index(epoch_n, offset=0)` | Map epoch number to starting lattice index |
| `A_CONSTANT` | Bateman-Horn fitted constant ≈ 2.8913 |

### Verifier (`echoprime.verifier`)

| Function | Description |
|---|---|
| `collapse_score(p, window=128)` | Symbolic collapse score: fraction of C(p,k) ≡ 0 mod p |
| `verify_safe_prime(p, window=128, threshold=0.95)` | Full verification with primality + collapse scoring |
| `batch_verify(candidates, window=128, threshold=0.95)` | Verify multiple candidates |

### Oracle (`echoprime.oracle`)

| Function | Description |
|---|---|
| `create_trace(index, p, q, score_p, score_q, verified)` | Create SHA-256 hashed oracle trace record |
| `format_for_contract(trace)` | Format for Ethereum smart contract submission |
| `export_traces(traces, filepath)` | Export traces to JSON file |

### Utilities (`echoprime.utils`)

| Symbol | Description |
|---|---|
| `KNOWN_SAFE_PRIMES` | First 100 known safe primes for validation |
| `is_safe_prime(p)` | Quick safe prime check |
| `timer(func)` | Decorator that returns `(result, elapsed_seconds)` |

## The Math

### Safe Primes

A **safe prime** is a prime `p` such that `q = (p-1)/2` is also prime. The prime `q` is called a **Sophie Germain prime**.

### Analytic Projection

The n-th safe prime is estimated using:

```
p_n ≈ a · n · (ln n)²
```

where `a ≈ 2.8913` is an empirically fitted constant derived from the Bateman-Horn conjecture applied to the polynomial pair `(x, 2x+1)`.

### Symbolic Collapse Score

For a candidate prime `p`, the collapse score measures:

```
S(p) = |{k ∈ [1,T] : C(p,k) ≡ 0 (mod p)}| / T
```

By **Lucas' theorem**, for any prime `p > T`, all binomial coefficients `C(p,k)` for `1 ≤ k ≤ T` are divisible by `p`. Therefore `S(p) = 1.0` for all primes above the window size (default T=128).

## Examples

See the `examples/` directory:

- **`basic_usage.py`** — Core workflow demonstration
- **`batch_verify.py`** — Batch verification with JSON export

## Benchmarks

```bash
# Quick test (1000 candidates, 10% sampled)
python benchmarks/million_run.py --count 1000 --sample-rate 0.1

# Full million-candidate benchmark
python benchmarks/million_run.py
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Project Structure

```
echoprime/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── LICENSE                  # MIT License
├── setup.py                # Backwards compatibility
├── src/
│   └── echoprime/
│       ├── __init__.py     # Public API
│       ├── estimator.py    # Analytic safe prime estimator
│       ├── verifier.py     # Symbolic collapse score verifier
│       ├── oracle.py       # On-chain oracle trace format
│       └── utils.py        # Utilities and known primes
├── tests/
│   ├── test_estimator.py   # Estimator tests
│   ├── test_verifier.py    # Verifier tests
│   └── test_integration.py # Full pipeline tests
├── examples/
│   ├── basic_usage.py      # Basic workflow
│   └── batch_verify.py     # Batch verification
└── benchmarks/
    └── million_run.py      # 1M candidate benchmark
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests (`python -m pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

**Darren J. Edwards** — [Mikoshi Ltd.](https://github.com/DarrenEdwards111)

---

*EchoPrime: Where number theory meets deterministic oracle design.*
