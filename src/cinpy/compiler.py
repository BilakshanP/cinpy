"""Compiler engine: CFFI out-of-line API mode with hash-based disk caching."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

from cffi import FFI


def _default_cache_dir() -> Path:
    env = os.environ.get("CINPY_CACHE_DIR")
    if env:
        return Path(env)
    return Path.home() / ".cache" / "cinpy"


def _cache_key(source: str, header: str, **kwargs: Any) -> str:
    blob = f"{source}\n---\n{header}\n---\n{sys.version}\n---\n{kwargs}"
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def compile_module(
    source: str,
    header: str,
    *,
    module_name: str | None = None,
    cache_dir: Path | None = None,
    libraries: list[str] | None = None,
    include_dirs: list[str] | None = None,
    extra_compile_args: list[str] | None = None,
    extra_link_args: list[str] | None = None,
) -> tuple[FFI, Any]:
    """Compile C source and return (ffi, lib) using out-of-line API with caching."""
    cache_dir = cache_dir or _default_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = _cache_key(
        source,
        header,
        libraries=libraries,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
    mod_name = module_name or f"_cinpy_{key}"

    # Check cache for existing .so
    cached = _find_cached(cache_dir, mod_name)
    if cached:
        return _load_cached(cached, header, mod_name)

    # Compile
    ffi = FFI()
    ffi.cdef(header)
    ffi.set_source(
        mod_name,
        source,
        libraries=libraries or [],
        include_dirs=include_dirs or [],
        extra_compile_args=extra_compile_args or [],
        extra_link_args=extra_link_args or [],
    )
    so_path = ffi.compile(tmpdir=str(cache_dir))
    mod = _load_so(so_path, mod_name)
    return mod.ffi, mod.lib


def _find_cached(cache_dir: Path, mod_name: str) -> Path | None:
    for f in cache_dir.iterdir():
        if f.name.startswith(mod_name + ".") and ".so" in f.suffixes:
            return f
    return None


def _load_cached(so_path: Path, header: str, mod_name: str) -> tuple[FFI, Any]:
    mod = _load_so(str(so_path), mod_name)
    return mod.ffi, mod.lib


def _load_so(path: str, mod_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod
