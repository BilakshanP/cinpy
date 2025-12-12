from __future__ import annotations
from typing import Callable, ParamSpec, TypeVar, Any
from functools import wraps
import inspect
from cffi import FFI

P = ParamSpec("P")
R = TypeVar("R")

PreProcessor = Callable[[tuple[Any, ...]], tuple[Any, ...]]

def from_c(
    c_source: str,
    header: str | None = None,
    preprocess: PreProcessor | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator: compile the provided C source (single translation unit)
    and replace the decorated Python function with a thin shim calling
    the compiled C symbol named as the Python function.
    """

    ffi = FFI()

    if header is None:
        prefix = c_source.split("{", 1)[0].strip()
        header = prefix if prefix.endswith(";") else prefix + ";"
    else:
        header = header if header.endswith(";") else header + ";"

    ffi.cdef(header)

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        module = ffi.verify(c_source)
        cfunc = getattr(module, fn.__name__)
        sig = inspect.signature(fn)

        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if kwargs:
                raise TypeError("C functions do not accept keyword arguments")

            bound = sig.bind_partial(*args)
            bound.apply_defaults()

            final_args = tuple(bound.arguments.values())
            if preprocess:
                final_args = preprocess(final_args)

            return cfunc(*final_args)  # type: ignore[no-any-return]

        wrapper._cfunc = cfunc   # type: ignore[attr-defined]
        wrapper._ffi = ffi       # type: ignore[attr-defined]
        wrapper._module = module # type: ignore[attr-defined]
        return wrapper

    return decorator
