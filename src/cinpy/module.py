"""CModule: class-based API for multi-function C modules with shared state."""

from __future__ import annotations

from pathlib import Path

from .coercion import auto_coerce_arg, auto_coerce_return
from .compiler import compile_module
from .errors import CinPyCompileError, CinPyParseError
from .parser import extract_functions, generate_header


class CModule:
    """Compile a C source into a module exposing all functions as callable attributes.

    Usage:
        mod = CModule('''
            int add(int a, int b) { return a + b; }
            int mul(int a, int b) { return a * b; }
        ''')
        mod.add(1, 2)  # 3
        mod.mul(3, 4)  # 12
    """

    def __init__(
        self,
        source: str,
        header: str | None = None,
        *,
        libraries: list[str] | None = None,
        include_dirs: list[str] | None = None,
        extra_compile_args: list[str] | None = None,
        extra_link_args: list[str] | None = None,
        cache_dir: Path | None = None,
    ):
        self._source = source
        self._functions = extract_functions(source)
        if not self._functions and header is None:
            raise CinPyParseError("No functions found in source", source=source)

        if header is None:
            self._header = generate_header(self._functions)
        else:
            self._header = header if header.endswith(";") else header + ";"

        try:
            self.ffi, self._lib = compile_module(
                source,
                self._header,
                libraries=libraries,
                include_dirs=include_dirs,
                extra_compile_args=extra_compile_args,
                extra_link_args=extra_link_args,
                cache_dir=cache_dir,
            )
        except Exception as e:
            raise CinPyCompileError("CModule", str(e), str(e), source) from e

        # Build function metadata for coercion
        self._func_meta = {f.name: f for f in self._functions}

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        if not hasattr(self._lib, name):
            raise AttributeError(f"CModule has no function '{name}'")
        cfunc = getattr(self._lib, name)
        meta = self._func_meta.get(name)

        def wrapper(*args):
            if meta:
                coerced = tuple(
                    auto_coerce_arg(a, meta.params[i].type, self.ffi, name, meta.params[i].name)
                    if i < len(meta.params)
                    else a
                    for i, a in enumerate(args)
                )
            else:
                coerced = args
            result = cfunc(*coerced)
            if meta:
                result = auto_coerce_return(result, meta.return_type, self.ffi)
            return result

        # Cache the wrapper on the instance
        setattr(self, name, wrapper)
        return wrapper
