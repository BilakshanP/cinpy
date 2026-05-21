"""Using external libraries with from_c (linking -lm)."""

from cinpy import from_c


@from_c(
    "#include <math.h>\ndouble my_sin(double x) { return sin(x); }",
    libraries=["m"],
)
def my_sin(x: float) -> float: ...


@from_c(
    "#include <math.h>\ndouble my_cos(double x) { return cos(x); }",
    libraries=["m"],
)
def my_cos(x: float) -> float: ...


if __name__ == "__main__":
    import math

    assert abs(my_sin(0.0)) < 1e-9
    assert abs(my_cos(0.0) - 1.0) < 1e-9
    assert abs(my_sin(math.pi / 2) - 1.0) < 1e-9
    print("math_lib: OK")
