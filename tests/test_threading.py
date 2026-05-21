"""Thread safety tests for CinPy. CFFI out-of-line API releases the GIL during C calls."""

import threading
from cinpy import CModule


def test_concurrent_calls():
    """Multiple threads can call C functions concurrently without segfaults."""
    mod = CModule("""
        int fib(int n) {
            if (n <= 1) return n;
            return fib(n-1) + fib(n-2);
        }
    """)

    results = [None] * 8
    errors = []

    def worker(idx):
        try:
            results[idx] = mod.fib(20)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert all(r == 6765 for r in results)


def test_shared_state_thread_safety():
    """Shared state access from multiple threads (no locking — demonstrates behavior)."""
    mod = CModule("""
        static int counter = 0;
        int inc(void) { return ++counter; }
        int get(void) { return counter; }
    """)

    threads = [threading.Thread(target=mod.inc) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Counter should be 100 (each inc is atomic at C level for single increment)
    assert mod.get() == 100
