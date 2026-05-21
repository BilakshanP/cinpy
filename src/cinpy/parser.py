"""Regex-based C source parser for extracting function signatures and includes."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Param:
    type: str
    name: str


@dataclass(frozen=True, slots=True)
class FunctionSignature:
    return_type: str
    name: str
    params: list[Param]


# Matches #include <...> or #include "..."
_INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]', re.MULTILINE)

# Strip C comments (both /* */ and //)
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)

# Match function definitions: return_type name(params) {
# Handles pointers, const, unsigned, struct prefixes, multi-line
_FUNC_RE = re.compile(
    r"(?:^|\n)\s*"
    r"((?:(?:static|inline|extern|const|unsigned|signed|struct|enum)\s+)*"
    r"[\w][\w\s*]*?)"  # return type (greedy but stops at name)
    r"\b(\w+)\s*"  # function name
    r"\(([^)]*)\)\s*\{",  # params
    re.DOTALL,
)

# Match a single parameter like "const int *x" or "char* s"
_PARAM_RE = re.compile(r"^\s*(.*?[\s*]+)(\w+)\s*$")


def _strip_comments(source: str) -> str:
    return _COMMENT_RE.sub("", source)


def _parse_param(raw: str) -> Param:
    raw = raw.strip()
    if not raw or raw == "void":
        return None  # type: ignore[return-value]
    m = _PARAM_RE.match(raw)
    if m:
        return Param(type=m.group(1).strip(), name=m.group(2).strip())
    # Fallback: no name (e.g., just "int") — synthesize a name
    return Param(type=raw, name="")


def extract_includes(source: str) -> list[str]:
    """Extract all #include lines from source."""
    return [
        f"#include <{m}>" if "<" in line else f'#include "{m}"'
        for line in source.splitlines()
        if (m_obj := _INCLUDE_RE.match(line))
        for m in [m_obj.group(1)]
    ]


def extract_functions(source: str) -> list[FunctionSignature]:
    """Extract all function signatures from C source."""
    cleaned = _strip_comments(source)
    results: list[FunctionSignature] = []
    for m in _FUNC_RE.finditer(cleaned):
        ret_type = " ".join(m.group(1).split())  # normalize whitespace
        name = m.group(2)
        raw_params = m.group(3).strip()
        if not raw_params or raw_params == "void":
            params = []
        else:
            params = [p for raw in raw_params.split(",") if (p := _parse_param(raw)) is not None]
        results.append(FunctionSignature(return_type=ret_type, name=name, params=params))
    return results


def generate_header(functions: list[FunctionSignature]) -> str:
    """Generate a CFFI cdef header string from parsed function signatures."""
    lines: list[str] = []
    for fn in functions:
        if fn.params:
            params_str = ", ".join(f"{p.type} {p.name}" if p.name else p.type for p in fn.params)
        else:
            params_str = "void"
        lines.append(f"{fn.return_type} {fn.name}({params_str});")
    return "\n".join(lines)
