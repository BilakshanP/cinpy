"""Hybrid type coercion layer: auto for common types, explicit for complex ones."""

from __future__ import annotations

from collections.abc import Callable

from cffi import FFI

# C type patterns that trigger auto-coercion
_CHAR_PTR_TYPES = {"char*", "const char*", "char *", "const char *"}


def auto_coerce_arg(
    value: object,
    c_type: str,
    ffi: FFI,
    func_name: str,
    param_name: str,
) -> object:
    """Auto-coerce a Python value to match the expected C type."""
    c_type_normalized = c_type.replace(" ", "").replace("const", "").strip()

    # str -> bytes for char*
    if c_type.replace(" ", "") in {"char*", "constchar*"} and isinstance(value, str):
        return value.encode("utf-8")

    # Python float -> C double (already handled by CFFI, but be explicit)
    if c_type_normalized in {"double", "float"} and isinstance(value, (int, float)):
        return float(value)

    # Python int -> C int types (CFFI handles this natively)
    return value


def auto_coerce_return(value: object, c_type: str, ffi: FFI) -> object:
    """Auto-coerce a C return value to a Python type."""
    if c_type.replace(" ", "") in {"char*", "constchar*"}:
        if value != ffi.NULL:
            return ffi.string(value).decode("utf-8")  # type: ignore[arg-type]
        return None
    return value


def coerce_args(
    args: tuple,
    param_types: list[str],
    param_names: list[str],
    ffi: FFI,
    func_name: str,
    preprocess: Callable | None = None,
) -> tuple:
    """Apply preprocess hook then auto-coercion to all arguments."""
    if preprocess:
        args = preprocess(args)

    coerced = []
    for i, val in enumerate(args):
        c_type = param_types[i] if i < len(param_types) else ""
        p_name = param_names[i] if i < len(param_names) else f"arg{i}"
        coerced.append(auto_coerce_arg(val, c_type, ffi, func_name, p_name))
    return tuple(coerced)
