"""Benchmarks comparing pure Python vs CinPy (compiled C) performance."""

import time

from cinpy import CModule, from_c


# --- Fibonacci ---

def py_fib(n: int) -> int:
    if n <= 1:
        return n
    return py_fib(n - 1) + py_fib(n - 2)


@from_c("""
    int c_fib(int n) {
        if (n <= 1) return n;
        return c_fib(n - 1) + c_fib(n - 2);
    }
""")
def c_fib(n: int) -> int: ...


# --- Sum array ---

def py_sum(data: list[int]) -> int:
    total = 0
    for x in data:
        total += x
    return total


sum_mod = CModule("""
    long c_sum(long* arr, int n) {
        long s = 0;
        for (int i = 0; i < n; i++) s += arr[i];
        return s;
    }
""")


# --- Prime sieve ---

def py_count_primes(n: int) -> int:
    if n < 2:
        return 0
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return sum(sieve)


@from_c("""
    int c_count_primes(int n) {
        if (n < 2) return 0;
        char* sieve = (char*)malloc(n + 1);
        for (int i = 0; i <= n; i++) sieve[i] = 1;
        sieve[0] = sieve[1] = 0;
        for (int i = 2; i * i <= n; i++) {
            if (sieve[i]) {
                for (int j = i * i; j <= n; j += i)
                    sieve[j] = 0;
            }
        }
        int count = 0;
        for (int i = 0; i <= n; i++) count += sieve[i];
        free(sieve);
        return count;
    }
""", header="int c_count_primes(int n);")
def c_count_primes(n: int) -> int: ...


def bench(label: str, fn, *args, runs: int = 5):
    """Run fn multiple times and report best time."""
    best = float("inf")
    for _ in range(runs):
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        best = min(best, elapsed)
    return result, best


def fmt(seconds: float) -> str:
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} µs"
    if seconds < 1:
        return f"{seconds * 1e3:.1f} ms"
    return f"{seconds:.2f} s"


if __name__ == "__main__":
    from cinpy.types import c_array

    print("=" * 60)
    print(f"{'Benchmark':<25} {'Python':<12} {'CinPy':<12} {'Speedup':<10}")
    print("=" * 60)

    # Fibonacci(35)
    _, py_t = bench("fib(35)", py_fib, 35)
    _, c_t = bench("fib(35)", c_fib, 35)
    print(f"{'fib(35)':<25} {fmt(py_t):<12} {fmt(c_t):<12} {py_t/c_t:.1f}x")

    # Sum 1M integers
    data = list(range(1_000_000))
    arr = c_array(sum_mod, "long", data)
    _, py_t = bench("sum(1M ints)", py_sum, data)
    _, c_t = bench("sum(1M ints)", lambda: sum_mod.c_sum(arr, len(data)), runs=5)
    print(f"{'sum(1M ints)':<25} {fmt(py_t):<12} {fmt(c_t):<12} {py_t/c_t:.1f}x")

    # Prime sieve up to 1M
    _, py_t = bench("primes(<1M)", py_count_primes, 1_000_000)
    _, c_t = bench("primes(<1M)", c_count_primes, 1_000_000)
    print(f"{'primes(<1M)':<25} {fmt(py_t):<12} {fmt(c_t):<12} {py_t/c_t:.1f}x")

    print("=" * 60)
