#!/usr/bin/env python3
"""
EchoPrime SDK — Million Candidate Benchmark

Runs the 1M candidate benchmark from the whitepaper.
Tests the estimator + verifier pipeline at scale.

Usage:
    python benchmarks/million_run.py [--count N] [--sample-rate R]

Options:
    --count N         Number of candidates to generate (default: 1_000_000)
    --sample-rate R   Fraction of candidates to fully verify (default: 0.001)
"""
import argparse
import time
import sys
import math
from echoprime.estimator import estimate_nth_safe_prime, find_safe_prime_near, A_CONSTANT
from echoprime.verifier import verify_safe_prime, collapse_score
from echoprime.utils import is_safe_prime


def run_benchmark(count=1_000_000, sample_rate=0.001):
    print("=" * 70)
    print(f"EchoPrime Million Candidate Benchmark")
    print(f"  Candidates:   {count:,}")
    print(f"  Sample rate:  {sample_rate} ({int(count * sample_rate):,} full verifications)")
    print(f"  Constant a:   {A_CONSTANT}")
    print("=" * 70)

    sample_every = max(1, int(1 / sample_rate))
    total_found = 0
    total_verified = 0
    total_failed = 0
    errors = []

    t_start = time.time()
    t_last_report = t_start

    for n in range(1, count + 1):
        try:
            # Generate estimate
            estimate = estimate_nth_safe_prime(n)

            # Only do full pipeline on sampled indices
            if n % sample_every == 0 or n <= 10:
                p, q = find_safe_prime_near(n)
                total_found += 1

                result = verify_safe_prime(p)
                if result['verified']:
                    total_verified += 1
                else:
                    total_failed += 1
                    errors.append((n, p, result))

        except Exception as e:
            errors.append((n, None, str(e)))
            total_failed += 1

        # Progress report every 10 seconds
        now = time.time()
        if now - t_last_report > 10:
            elapsed = now - t_start
            rate = n / elapsed
            eta = (count - n) / rate if rate > 0 else 0
            print(f"  Progress: {n:>10,}/{count:,} "
                  f"({100*n/count:.1f}%) "
                  f"rate={rate:.0f}/s "
                  f"ETA={eta:.0f}s "
                  f"verified={total_verified} "
                  f"failed={total_failed}")
            t_last_report = now

    t_end = time.time()
    elapsed = t_end - t_start

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Total candidates:    {count:,}")
    print(f"  Sampled & found:     {total_found:,}")
    print(f"  Verified (pass):     {total_verified:,}")
    print(f"  Failed:              {total_failed:,}")
    print(f"  Pass rate:           {100*total_verified/max(1,total_found):.2f}%")
    print(f"  Total time:          {elapsed:.2f}s")
    print(f"  Rate:                {count/elapsed:.0f} estimates/s")
    print(f"  Full verify rate:    {total_found/elapsed:.1f} verified/s")

    if errors:
        print(f"\n  First 10 errors:")
        for n, p, err in errors[:10]:
            print(f"    Index {n}: p={p} — {err}")

    print("=" * 70)
    return total_failed == 0


def main():
    parser = argparse.ArgumentParser(description="EchoPrime Million Candidate Benchmark")
    parser.add_argument("--count", type=int, default=1_000_000,
                        help="Number of candidates (default: 1,000,000)")
    parser.add_argument("--sample-rate", type=float, default=0.001,
                        help="Fraction to fully verify (default: 0.001)")
    args = parser.parse_args()

    success = run_benchmark(count=args.count, sample_rate=args.sample_rate)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
