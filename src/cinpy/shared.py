"""Core from_c decorator: compiles inline C and replaces the decorated function."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from .coercion import auto_coerce_return, coerce_args
from .compiler import compile_module
from .errors import CinPyCompileError, CinPyParseError
from .parser import extract_functions, generate_header

type PreProcessor = Callable[[tuple[Any, ...]], tuple[Any, ...]]
type PostProcessor = Callable[[Any], Any]


def from_c(
    c_source: str,
    header: str | None = None,
    *,
    preprocess: PreProcessor | None = None,
    postprocess: PostProcessor | None = None,
    libraries: list[str] | None = None,
    include_dirs: list[str] | None = None,
    extra_compile_args: list[str] | None = None,
    extra_link_args: list[str] | None = None,
    cache_dir: Path | None = None,
) -> Callable:
    """Decorator: compile C source and replace the decorated function with a C call."""

    # Parse functions from source
    functions = extract_functions(c_source)
    if not functions and header is None:
        raise CinPyParseError("No functions found in source", source=c_source)

    # Generate header if not provided
    if header is None:
        cdef_header = generate_header(functions)
    else:
        cdef_header = header if header.endswith(";") else header + ";"

    def decorator(fn: Callable) -> Callable:
        # Find the target function matching the decorated name
        target = None
        for f in functions:
            if f.name == fn.__name__:
                target = f
                break
        if target is None and functions:
            target = functions[0]

        # Compile
        try:
            ffi, lib = compile_module(
                c_source,
                cdef_header,
                libraries=libraries,
                include_dirs=include_dirs,
                extra_compile_args=extra_compile_args,
                extra_link_args=extra_link_args,
                cache_dir=cache_dir,
            )
        except Exception as e:
            raise CinPyCompileError(fn.__name__, str(e), str(e), c_source) from e

        cfunc = getattr(lib, fn.__name__)
        sig = inspect.signature(fn)

        # Extract param types for coercion
        param_types = [p.type for p in target.params] if target else []
        param_names = [p.name for p in target.params] if target else []
        ret_type = target.return_type if target else ""

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if kwargs:
                raise TypeError("C functions do not accept keyword arguments")

            bound = sig.bind_partial(*args)
            bound.apply_defaults()
            final_args = tuple(bound.arguments.values())

            # Coerce arguments
            final_args = coerce_args(
                final_args, param_types, param_names, ffi, fn.__name__, preprocess
            )

            # Call C function
            result = cfunc(*final_args)

            # Coerce return value
            result = auto_coerce_return(result, ret_type, ffi)
            if postprocess:
                result = postprocess(result)
            return result

        wrapper._cfunc = cfunc  # type: ignore[attr-defined]
        wrapper._ffi = ffi  # type: ignore[attr-defined]
        wrapper._lib = lib  # type: ignore[attr-defined]
        return wrapper

    return decorator
