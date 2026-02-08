#!/usr/bin/env python3
"""
EchoPrime SDK — Batch Verification Example

Demonstrates batch verification of multiple safe prime candidates
and exporting oracle traces to a JSON file.
"""
import os
import tempfile
from echoprime import (
    find_safe_prime_near,
    batch_verify,
    create_trace,
    export_traces,
    KNOWN_SAFE_PRIMES,
)


def main():
    print("=" * 60)
    print("EchoPrime SDK — Batch Verification")
    print("=" * 60)

    # 1. Verify known safe primes
    print(f"\nVerifying first 20 known safe primes...")
    candidates = KNOWN_SAFE_PRIMES[:20]
    results = batch_verify(candidates)

    passed = sum(1 for r in results if r['verified'])
    failed = len(results) - passed
    print(f"  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")

    for r in results:
        status = "✓" if r['verified'] else "✗"
        print(f"  {status} p={r['p']:>6}  q={r['q']:>6}  "
              f"score_p={r['score_p']:.4f}  score_q={r['score_q']:.4f}")

    # 2. Find and verify safe primes for indices 1-50
    print(f"\n--- Finding safe primes for indices 1-50 ---")
    traces = []
    for n in range(1, 51):
        p, q = find_safe_prime_near(n)
        result = batch_verify([p])[0]
        trace = create_trace(
            index=n, p=p, q=q,
            score_p=result['score_p'],
            score_q=result['score_q'],
            verified=result['verified'],
        )
        traces.append(trace)
        if n % 10 == 0:
            print(f"  Processed {n}/50...")

    # 3. Export traces
    output_path = os.path.join(tempfile.gettempdir(), "echoprime_traces.json")
    export_traces(traces, output_path)
    print(f"\nExported {len(traces)} traces to {output_path}")

    all_verified = all(t['verified'] for t in traces)
    print(f"All verified: {all_verified}")

    print("\n" + "=" * 60)
    print("Batch verification complete!")


if __name__ == "__main__":
    main()
