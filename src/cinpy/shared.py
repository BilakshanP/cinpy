from __future__ import annotations
from typing import Callable, ParamSpec, TypeVar
from cffi import FFI

P = ParamSpec("P")
R = TypeVar("R")

def from_c(c_source: str, header: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator: compile the provided C source (single translation unit)
    and replace the decorated Python function with a thin shim calling
    the compiled C symbol named as the Python function.
    """

    ffi = FFI()

    if not header:
        header = c_source.split("{", 1)[0].strip()
    
    if not header.endswith(";"):
        header = header + ";"

    ffi.cdef(header)

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        module = ffi.verify(c_source)
        cfunc = getattr(module, fn.__name__)

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if kwargs:
                raise TypeError("C functions do not accept keyword arguments")
            return cfunc(*args)  # type: ignore[no-any-return]

        # expose internals for advanced usage / preconversion
        wrapper._cfunc = cfunc  # type: ignore[attr-defined]
        wrapper._ffi = ffi  # type: ignore[attr-defined]
        wrapper._module = module  # type: ignore[attr-defined]
        return wrapper

    return decorator
