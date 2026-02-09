# EchoPrime 🔐

[![PyPI](https://img.shields.io/pypi/v/echoprime.svg)](https://pypi.org/project/echoprime/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18529723.svg)](https://doi.org/10.5281/zenodo.18529723)

**Deterministic safe prime oracle and cryptographic primitive.**

EchoPrime provides a deterministic method for estimating, locating, and verifying safe primes using an analytic projection based on the Bateman-Horn heuristic. It includes a symbolic collapse score verifier and an oracle trace format for on-chain publication.

## Key Features

- **Analytic Estimator** — Projects the n-th safe prime location using `p_n ≈ a · n · (log n)²` with empirically fitted constant `a ≈ 2.8913`
- **Symbolic Collapse Verifier** — Verifies primes using binomial coefficient divisibility (Lucas' theorem)
- **Safe Prime Finder** — Deterministic search from estimated regions
- **Oracle Traces** — SHA-256 hashed records for on-chain publication
- **Ethereum Contract Format** — Ready-to-submit tuple format for smart contracts

## Installation

📦 **PyPI:** https://pypi.org/project/echoprime/

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
├── LICENSE                  # Apache 2.0 License
├── setup.py                # Backwards compatibility
├── src/
│   └── echoprime/
│       ├── __init__.py     # Public API
│       ├── estimator.py    # Analytic safe prime estimator
│       ├── verifier.py     # Symbolic collapse score verifier
│       ├── oracle.py       # On-chain oracle trace format
│       └── utils.py        # Utilities and known primes
├── contracts/
│   ├── src/
│   │   ├── EchoPrimeOracle.sol   # Solidity oracle contract
│   │   └── IEchoPrimeOracle.sol  # Contract interface
│   ├── test/                     # 20 Hardhat tests
│   ├── scripts/                  # Deploy + submit scripts
│   ├── hardhat.config.js
│   └── README.md                 # Contract docs
├── whitepaper/
│   ├── echoprime-whitepaper.tex  # LaTeX source
│   └── echoprime-whitepaper.pdf  # Compiled PDF
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

## Smart Contracts

EchoPrime includes an Ethereum-compatible smart contract (`EchoPrimeOracle.sol`) that serves as a public, on-chain registry for verified safe primes.

### Features
- **Submit** — Publish a verified safe prime with its index, collapse scores, and primality verdict
- **Batch submit** — Submit up to 100 primes in a single transaction
- **Query** — Retrieve any published prime by its deterministic index
- **Access control** — Owner can authorize oracle bots as submitters
- **Events** — Every submission emits a `PrimeVerified` event for off-chain indexing

### Quick Start

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat test          # 20 tests
npx hardhat run scripts/deploy.js --network sepolia
```

### Contract API

| Function | Description |
|---|---|
| `submitVerification(index, p, scoreP, scoreQ, verified)` | Submit a verified safe prime |
| `batchSubmit(indices[], primes[], scoresP[], scoresQ[], verifieds[])` | Batch submit (max 100) |
| `getPrime(index)` | Query a prime record by index |
| `isPrimeSubmitted(index)` | Check if an index has been submitted |
| `totalSubmissions` | Total number of published primes |
| `addSubmitter(address)` | Authorize an oracle bot (owner only) |
| `removeSubmitter(address)` | Revoke authorization (owner only) |

See [`contracts/README.md`](contracts/README.md) for full deployment guide and environment setup.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests (`python -m pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## About Mikoshi Ltd

EchoPrime is built by **[Mikoshi Ltd](https://mikoshi.co.uk)** — a UK fintech and cryptographic infrastructure company based in Swansea, Wales.

Mikoshi builds tools at the intersection of finance, AI, and cryptography:

- **[Mikoshi Invest](https://mikoshi.co.uk)** — Investment intelligence platform with AI analysis, ML forecasting, and real-time market signals
- **EchoPrime** — Deterministic safe prime oracle for Web3 and cryptographic infrastructure
- **Mikoshi AI** — AI companion and intelligence products

Mikoshi's mission is to make sophisticated financial and cryptographic tools accessible to everyone — not just Wall Street.

📧 **Contact:** mikoshiuk@gmail.com
🌐 **Website:** [mikoshi.co.uk](https://mikoshi.co.uk)
🔬 **EchoPrime:** [echoprime.xyz](https://echoprime.xyz)
📄 **Paper:** [Edwards, D. (2026). Zenodo. DOI: 10.5281/zenodo.18529723](https://doi.org/10.5281/zenodo.18529723)

## Citation

```bibtex
@article{edwards2026echoprime,
  title   = {EchoPrime: A Verifiable Oracle for Deterministic Safe Prime Generation with On-Chain Audit Trails},
  author  = {Edwards, Darren J.},
  year    = {2026},
  doi     = {10.5281/zenodo.18529723},
  url     = {https://doi.org/10.5281/zenodo.18529723},
  publisher = {Zenodo}
}
```

## License

Licensed under the Apache License, Version 2.0 — see the [LICENSE](LICENSE) file for details.

## Author

**Darren J. Edwards, Ph.D.**
Founder & CEO, Mikoshi Ltd
[GitHub](https://github.com/DarrenEdwards111) · [mikoshi.co.uk](https://mikoshi.co.uk)

---

*EchoPrime: Deterministic cryptographic infrastructure for the future of Web3.*
*© 2025 Mikoshi Ltd. All rights reserved.*
