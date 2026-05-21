from cffi import FFI

from cinpy import CModule, c_array, c_struct, to_python


def test_c_array_sum():
    mod = CModule("""
        int sum_arr(int* arr, int n) {
            int s = 0;
            for (int i = 0; i < n; i++) s += arr[i];
            return s;
        }
    """)
    arr = c_array(mod, "int", [1, 2, 3, 4, 5])
    assert mod.sum_arr(arr, 5) == 15


def test_c_struct_pass():
    mod = CModule("""
        typedef struct { int x; int y; } Point;
        int sum_point(Point p) { return p.x + p.y; }
    """, header="typedef struct { int x; int y; } Point; int sum_point(Point p);")
    p = c_struct(mod, "Point", x=10, y=20)
    assert mod.sum_point(p) == 30


def test_to_python_struct():
    mod = CModule("""
        typedef struct { int x; int y; } Point;
        Point make_point(int x, int y) { Point p = {x, y}; return p; }
    """, header="typedef struct { int x; int y; } Point; Point make_point(int x, int y);")
    p = mod._lib.make_point(3, 7)
    d = to_python(p, mod)
    assert d == {"x": 3, "y": 7}


def test_to_python_array():
    ffi = FFI()
    arr = ffi.new("int[3]", [10, 20, 30])
    assert to_python(arr, ffi) == [10, 20, 30]


def test_to_python_char_ptr():
    ffi = FFI()
    s = ffi.new("char[]", b"hello")
    ptr = ffi.cast("char*", s)
    assert to_python(ptr, ffi) == "hello"


def test_backward_compat_with_ffi():
    """Passing ffi directly still works."""
    mod = CModule("int x(int n) { return n; }")
    arr = c_array(mod.ffi, "int", [1, 2])
    assert arr[0] == 1
