import time
from pathlib import Path

from cinpy.compiler import compile_module, _cache_key


def test_compile_basic(tmp_path):
    source = '#include <stdio.h>\nint add(int a, int b) { return a + b; }'
    header = 'int add(int a, int b);'
    ffi, lib = compile_module(source, header, cache_dir=tmp_path)
    assert lib.add(2, 3) == 5


def test_cache_hit(tmp_path):
    source = 'int mul(int a, int b) { return a * b; }'
    header = 'int mul(int a, int b);'

    # First compile
    t0 = time.perf_counter()
    ffi1, lib1 = compile_module(source, header, cache_dir=tmp_path)
    first_time = time.perf_counter() - t0

    # Second call should hit cache
    t0 = time.perf_counter()
    ffi2, lib2 = compile_module(source, header, cache_dir=tmp_path)
    second_time = time.perf_counter() - t0

    assert lib2.mul(3, 4) == 12
    # Cache hit should be faster (no compilation)
    assert second_time < first_time


def test_cache_invalidation(tmp_path):
    header = 'int val(void);'
    source1 = 'int val(void) { return 1; }'
    source2 = 'int val(void) { return 2; }'

    _, lib1 = compile_module(source1, header, cache_dir=tmp_path)
    assert lib1.val() == 1

    _, lib2 = compile_module(source2, header, cache_dir=tmp_path)
    assert lib2.val() == 2


def test_libraries(tmp_path):
    source = '#include <math.h>\ndouble my_sqrt(double x) { return sqrt(x); }'
    header = 'double my_sqrt(double x);'
    _, lib = compile_module(source, header, cache_dir=tmp_path, libraries=["m"])
    assert abs(lib.my_sqrt(4.0) - 2.0) < 1e-9


def test_cache_key_differs():
    k1 = _cache_key("int a(){}", "int a();", libraries=["m"])
    k2 = _cache_key("int a(){}", "int a();", libraries=[])
    assert k1 != k2
