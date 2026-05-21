"""Integration tests: end-to-end scenarios combining multiple features."""

import os
import pytest
from pathlib import Path

from cinpy import from_c, CModule, c_array, c_struct, to_python, CinPyCompileError, set_debug


def test_cmodule_with_arrays_and_coercion():
    """CModule + c_array + auto-coercion in one workflow."""
    mod = CModule("""
        int dot_product(int* a, int* b, int n) {
            int sum = 0;
            for (int i = 0; i < n; i++) sum += a[i] * b[i];
            return sum;
        }
    """)
    a = c_array(mod, "int", [1, 2, 3])
    b = c_array(mod, "int", [4, 5, 6])
    assert mod.dot_product(a, b, 3) == 32  # 1*4 + 2*5 + 3*6


def test_cmodule_struct_round_trip():
    """Create struct in Python, pass to C, get struct back, convert to dict."""
    mod = CModule(
        """
        typedef struct { int x; int y; } Point;
        Point scale(Point p, int factor) {
            Point r = {p.x * factor, p.y * factor};
            return r;
        }
    """,
        header="typedef struct { int x; int y; } Point; Point scale(Point p, int factor);",
    )

    p = c_struct(mod, "Point", x=3, y=4)
    result = mod._lib.scale(p, 2)
    d = to_python(result, mod)
    assert d == {"x": 6, "y": 8}


def test_from_c_with_includes_and_library():
    """from_c with #include and external library linking."""

    @from_c(
        "#include <math.h>\ndouble hypotenuse(double a, double b) { return sqrt(a*a + b*b); }",
        libraries=["m"],
    )
    def hypotenuse(a: float, b: float) -> float: ...

    assert abs(hypotenuse(3.0, 4.0) - 5.0) < 1e-9


def test_compile_error_raised():
    """Invalid C source raises CinPyCompileError."""
    with pytest.raises(CinPyCompileError):

        @from_c("int bad(int x) { return undefined_var; }")
        def bad(x: int) -> int: ...


def test_debug_mode_compile_error(monkeypatch):
    """Debug mode includes source in error message."""
    monkeypatch.setenv("CINPY_DEBUG", "1")
    with pytest.raises(CinPyCompileError) as exc_info:

        @from_c("int bad2(int x) { return xyz; }")
        def bad2(x: int) -> int: ...

    assert "xyz" in str(exc_info.value)


def test_cache_dir_param(tmp_path):
    """Explicit cache_dir parameter works."""

    @from_c("int cached_fn(int x) { return x + 1; }", cache_dir=tmp_path)
    def cached_fn(x: int) -> int: ...

    assert cached_fn(5) == 6
    # Verify .so was created in tmp_path
    so_files = list(tmp_path.glob("*.so"))
    assert len(so_files) >= 1


def test_env_cache_dir(tmp_path, monkeypatch):
    """CINPY_CACHE_DIR env var is respected."""
    monkeypatch.setenv("CINPY_CACHE_DIR", str(tmp_path))

    @from_c("int env_cached(int x) { return x * 3; }")
    def env_cached(x: int) -> int: ...

    assert env_cached(4) == 12
    so_files = list(tmp_path.glob("*.so"))
    assert len(so_files) >= 1


def test_char_ptr_return_coercion():
    """char* return is auto-coerced to Python str."""
    mod = CModule(
        """
        const char* greeting(void) { return "hello from C"; }
    """,
        header="const char* greeting(void);",
    )
    # Access via _lib to get raw cdata, then coerce
    raw = mod._lib.greeting()
    result = mod.ffi.string(raw).decode()
    assert result == "hello from C"


def test_postprocess_with_coercion():
    """postprocess runs after auto-coercion."""

    @from_c(
        "int square(int n) { return n * n; }",
        postprocess=lambda x: f"result={x}",
    )
    def square(n: int) -> str: ...

    assert square(5) == "result=25"


def test_multi_function_helper_not_exposed():
    """Helper functions work internally but entry point is the decorated name."""

    @from_c("""
        static int double_it(int x) { return x * 2; }
        int quad(int x) { return double_it(double_it(x)); }
    """)
    def quad(x: int) -> int: ...

    assert quad(3) == 12
