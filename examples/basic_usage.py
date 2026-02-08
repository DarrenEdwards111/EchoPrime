#!/usr/bin/env python3
"""
EchoPrime SDK — Basic Usage Example

Demonstrates the core workflow:
1. Estimate where the n-th safe prime lives
2. Find the actual safe prime near that estimate
3. Verify it with symbolic collapse scoring
4. Create an oracle trace for on-chain publication
"""
from echoprime import (
    estimate_nth_safe_prime,
    find_safe_prime_near,
    verify_safe_prime,
    create_trace,
    A_CONSTANT,
    KNOWN_SAFE_PRIMES,
)


def main():
    print("=" * 60)
    print("EchoPrime SDK — Basic Usage")
    print("=" * 60)

    # 1. Show the analytic constant
    print(f"\nBateman-Horn constant a = {A_CONSTANT}")
    print(f"Known safe primes in library: {len(KNOWN_SAFE_PRIMES)}")

    # 2. Estimate and find safe primes for various indices
    for n in [1, 5, 10, 50, 100]:
        estimate = estimate_nth_safe_prime(n)
        p, q = find_safe_prime_near(n)

        print(f"\n--- Index n={n} ---")
        print(f"  Estimate:    {estimate}")
        print(f"  Found p:     {p}")
        print(f"  Sophie q:    {q}")
        print(f"  p = 2q + 1:  {p == 2 * q + 1}")

        # 3. Verify
        result = verify_safe_prime(p)
        print(f"  Collapse(p): {result['score_p']}")
        print(f"  Collapse(q): {result['score_q']}")
        print(f"  Verified:    {result['verified']}")

        # 4. Create trace
        trace = create_trace(
            index=n,
            p=p,
            q=q,
            score_p=result['score_p'],
            score_q=result['score_q'],
            verified=result['verified'],
        )
        print(f"  Trace hash:  {trace['hash'][:16]}...")

    print("\n" + "=" * 60)
    print("All done!")


if __name__ == "__main__":
    main()
