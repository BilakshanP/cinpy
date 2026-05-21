"""Ergonomic helpers for working with C structs, arrays, and pointers from Python."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cffi import FFI

if TYPE_CHECKING:
    from .module import CModule


def _get_ffi(mod_or_ffi: CModule | FFI) -> FFI:
    if hasattr(mod_or_ffi, "new"):  # It's an FFI-like object
        return mod_or_ffi  # type: ignore[return-value]
    return mod_or_ffi.ffi  # type: ignore[union-attr]


def c_array(mod_or_ffi: CModule | FFI, ctype: str, data: list[Any]) -> Any:
    """Create a CFFI array from a Python list.

    Usage:
        arr = c_array(mod, "int", [1, 2, 3])
    """
    return _get_ffi(mod_or_ffi).new(f"{ctype}[]", data)


def c_struct(mod_or_ffi: CModule | FFI, typedef: str, **fields: Any) -> Any:
    """Create a CFFI struct from keyword arguments.

    Usage:
        p = c_struct(mod, "Point", x=1, y=2)
    """
    return _get_ffi(mod_or_ffi).new(f"{typedef} *", fields)[0]


def to_python(cdata: Any, mod_or_ffi: CModule | FFI) -> Any:
    """Convert CFFI cdata to a Python object.

    - struct -> dict
    - array -> list
    - char* -> str
    - numeric -> int/float
    """
    ffi = _get_ffi(mod_or_ffi)
    typeof = ffi.typeof(cdata)
    kind = typeof.kind

    if kind == "struct":
        return {name: getattr(cdata, name) for name, _ in typeof.fields}
    elif kind == "array":
        return [cdata[i] for i in range(typeof.length)]
    elif kind == "pointer":
        item_type = typeof.item
        if item_type.cname == "char":
            if cdata != ffi.NULL:
                return ffi.string(cdata).decode("utf-8")  # type: ignore[union-attr]
            return None
        return cdata
    elif kind == "primitive":
        if "float" in typeof.cname or "double" in typeof.cname:
            return float(cdata)
        return int(cdata)
    return cdata
