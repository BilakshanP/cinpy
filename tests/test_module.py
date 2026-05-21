import pytest
from cinpy import CModule, CinPyParseError


def test_multi_function():
    mod = CModule("""
        int add(int a, int b) { return a + b; }
        int mul(int a, int b) { return a * b; }
    """)
    assert mod.add(2, 3) == 5
    assert mod.mul(4, 5) == 20


def test_shared_state():
    mod = CModule("""
        static int counter = 0;
        int increment(void) { return ++counter; }
        int get_count(void) { return counter; }
    """)
    assert mod.increment() == 1
    assert mod.increment() == 2
    assert mod.get_count() == 2


def test_auto_coerce_str():
    mod = CModule("int len_c(const char* s) { int n=0; while(s[n]) n++; return n; }")
    assert mod.len_c("hello") == 5


def test_libraries():
    mod = CModule(
        "#include <math.h>\ndouble my_sin(double x) { return sin(x); }",
        libraries=["m"],
    )
    assert abs(mod.my_sin(0.0)) < 1e-9


def test_no_functions_raises():
    with pytest.raises(CinPyParseError):
        CModule("// nothing here")


def test_attribute_error():
    mod = CModule("int foo(int x) { return x; }")
    with pytest.raises(AttributeError):
        mod.nonexistent(1)


def test_struct_via_ffi():
    mod = CModule(
        """
        typedef struct { int x; int y; } Point;
        int sum_point(Point p) { return p.x + p.y; }
    """,
        header="typedef struct { int x; int y; } Point; int sum_point(Point p);",
    )
    p = mod.ffi.new("Point *", {"x": 3, "y": 7})
    assert mod.sum_point(p[0]) == 10
