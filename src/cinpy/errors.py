"""Layered error handling for CinPy. Short messages by default, full detail with CINPY_DEBUG=1."""

from __future__ import annotations

import os


def _debug_enabled() -> bool:
    return os.environ.get("CINPY_DEBUG", "0") == "1"


_debug_mode = False


def set_debug(enabled: bool) -> None:
    """Programmatically enable/disable debug output."""
    global _debug_mode
    _debug_mode = enabled


def is_debug() -> bool:
    return _debug_mode or _debug_enabled()


class CinPyError(Exception):
    """Base exception for CinPy."""


class CinPyCompileError(CinPyError):
    """Raised when C compilation fails."""

    def __init__(self, func_name: str, short_msg: str, full_output: str = "", source: str = ""):
        self.func_name = func_name
        self.short_msg = short_msg
        self.full_output = full_output
        self.source = source
        if is_debug():
            detail = f"\n--- Source ---\n{source}\n--- Compiler Output ---\n{full_output}"
            msg = f"Compilation failed for '{func_name}': {short_msg}{detail}"
        else:
            msg = (
                f"Compilation failed for '{func_name}': {short_msg}."
                " Set CINPY_DEBUG=1 for full output."
            )
        super().__init__(msg)


class CinPyTypeError(CinPyError):
    """Raised on type coercion failures."""

    def __init__(self, func_name: str, param_name: str, expected: str, got: str):
        self.func_name = func_name
        self.param_name = param_name
        msg = f"Type error in '{func_name}': param '{param_name}' expected {expected}, got {got}"
        super().__init__(msg)


class CinPyParseError(CinPyError):
    """Raised when source parsing fails."""

    def __init__(self, msg: str, source: str = ""):
        self.source = source
        if is_debug() and source:
            msg = f"{msg}\n--- Source ---\n{source}"
        super().__init__(msg)
