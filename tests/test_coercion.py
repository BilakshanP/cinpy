from cffi import FFI
from cinpy.coercion import auto_coerce_arg, auto_coerce_return, coerce_args


def test_str_to_bytes():
    ffi = FFI()
    result = auto_coerce_arg("hello", "const char*", ffi, "test", "s")
    assert result == b"hello"


def test_str_to_bytes_no_const():
    ffi = FFI()
    result = auto_coerce_arg("hi", "char*", ffi, "test", "s")
    assert result == b"hi"


def test_int_passthrough():
    ffi = FFI()
    result = auto_coerce_arg(42, "int", ffi, "test", "n")
    assert result == 42


def test_float_coercion():
    ffi = FFI()
    result = auto_coerce_arg(3, "double", ffi, "test", "x")
    assert result == 3.0 and isinstance(result, float)


def test_return_char_ptr():
    ffi = FFI()
    ffi.cdef("char* greet(void);")
    # Simulate a char* return
    buf = ffi.new("char[]", b"hello")
    result = auto_coerce_return(buf, "char*", ffi)
    assert result == "hello"


def test_return_null_char_ptr():
    ffi = FFI()
    result = auto_coerce_return(ffi.NULL, "char*", ffi)
    assert result is None


def test_coerce_args_with_preprocess():
    ffi = FFI()
    pre = lambda args: (args[0] * 2,)
    result = coerce_args((3,), ["int"], ["n"], ffi, "test", preprocess=pre)
    assert result == (6,)


def test_coerce_args_auto():
    ffi = FFI()
    result = coerce_args(("hello",), ["const char*"], ["s"], ffi, "test")
    assert result == (b"hello",)
