from cinpy import from_c


def test_basic_add():
    @from_c("int add(int a, int b) { return a + b; }")
    def add(a: int, b: int) -> int: ...

    assert add(1, 2) == 3
    assert add(-1, 43) == 42


def test_default_args():
    @from_c("int identity(int n) { return n; }")
    def identity(n: int = 10) -> int: ...

    assert identity() == 10
    assert identity(5) == 5


def test_auto_coerce_str_to_bytes():
    @from_c("int strlen_c(const char* s) { int n=0; while(s[n]) n++; return n; }")
    def strlen_c(s: str) -> int: ...

    assert strlen_c("hello") == 5


def test_libraries_param():
    @from_c(
        "#include <math.h>\ndouble my_sqrt(double x) { return sqrt(x); }",
        libraries=["m"],
    )
    def my_sqrt(x: float) -> float: ...

    assert abs(my_sqrt(9.0) - 3.0) < 1e-9


def test_postprocess():
    @from_c(
        "int double_it(int n) { return n * 2; }",
        postprocess=lambda x: x + 1,
    )
    def double_it(n: int) -> int: ...

    assert double_it(5) == 11  # 5*2 + 1


def test_multi_function_source():
    src = """
    int helper(int x) { return x * 2; }
    int compute(int n) { return helper(n) + 1; }
    """

    @from_c(src)
    def compute(n: int) -> int: ...

    assert compute(3) == 7  # 3*2 + 1


def test_preprocess_backward_compat():
    @from_c(
        "void print_s(char* s) { }",
        preprocess=lambda args: (args[0].encode(),),
    )
    def print_s(s: str) -> None: ...

    print_s("hello")  # Should not raise
