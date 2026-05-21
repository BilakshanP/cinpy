import os
import pytest
from cinpy.errors import (
    CinPyCompileError, CinPyTypeError, CinPyParseError,
    set_debug, is_debug,
)


def test_compile_error_short():
    err = CinPyCompileError("add", "undeclared identifier 'x'", "full gcc output", "int add(){}")
    assert "add" in str(err)
    assert "CINPY_DEBUG=1" in str(err)
    assert "full gcc output" not in str(err)


def test_compile_error_debug(monkeypatch):
    monkeypatch.setenv("CINPY_DEBUG", "1")
    err = CinPyCompileError("add", "undeclared identifier", "gcc: error...", "int add(){}")
    assert "gcc: error..." in str(err)
    assert "int add(){}" in str(err)


def test_set_debug():
    set_debug(True)
    assert is_debug()
    set_debug(False)
    assert not is_debug()


def test_type_error():
    err = CinPyTypeError("strlen", "s", "bytes", "str")
    assert "strlen" in str(err)
    assert "param 's'" in str(err)


def test_parse_error():
    err = CinPyParseError("No functions found")
    assert "No functions found" in str(err)


def test_parse_error_debug(monkeypatch):
    monkeypatch.setenv("CINPY_DEBUG", "1")
    err = CinPyParseError("No functions found", source="bad source")
    assert "bad source" in str(err)
