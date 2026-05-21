# CinPy

Inline C for Python — write C functions directly in your Python code and call them at native speed.

Built on [CFFI](https://cffi.readthedocs.io/) (out-of-line API mode) with automatic compilation caching, type coercion, and multi-function module support.

## Requirements

- Python 3.12+
- Linux (gcc or clang)
- `cffi >= 1.17`

## Install

```bash
pip install .
# or for development:
pip install -e ".[dev]"
```

### From GitHub

In your `requirements.txt`:

```
cinpy @ git+https://github.com/bilakshanp/cinpy.git@main
```

Or install directly:

```bash
pip install git+https://github.com/bilakshanp/cinpy.git
```

## Quick Start

```python
from cinpy import from_c

@from_c("int add(int a, int b) { return a + b; }")
def add(a: int, b: int) -> int: ...

add(1, 2)  # 3
```

The decorated function body is just `...` — it's a type stub replaced at runtime by the compiled C function.

## Features

### Auto Type Coercion

Python `str` is automatically converted to `bytes` for `char*` parameters. No manual preprocessing needed:

```python
@from_c('int strlen_c(const char* s) { int n=0; while(s[n]) n++; return n; }')
def strlen_c(s: str) -> int: ...

strlen_c("hello")  # 5
```

`char*` return values are automatically decoded to Python `str`.

### External Libraries

Link system libraries with the `libraries` parameter:

```python
@from_c(
    '#include <math.h>\ndouble my_sqrt(double x) { return sqrt(x); }',
    libraries=["m"],
)
def my_sqrt(x: float) -> float: ...
```

### Multi-Function Sources

Sources with multiple functions compile together — helper functions are available internally:

```python
@from_c("""
    int helper(int x) { return x * 2; }
    int compute(int n) { return helper(n) + 1; }
""")
def compute(n: int) -> int: ...
```

### CModule — Advanced Multi-Function API

For modules with shared state, structs, or multiple entry points:

```python
from cinpy import CModule

mod = CModule("""
    static int counter = 0;
    int increment(void) { return ++counter; }
    int get_count(void) { return counter; }
""")

mod.increment()  # 1
mod.increment()  # 2
mod.get_count()  # 2
```

### Structs

Use `CModule` with explicit headers for struct support:

```python
from cinpy import CModule, c_struct, to_python

mod = CModule("""
    typedef struct { int x; int y; } Point;
    int sum_point(Point p) { return p.x + p.y; }
""", header="typedef struct { int x; int y; } Point; int sum_point(Point p);")

p = c_struct(mod, "Point", x=3, y=7)
mod.sum_point(p)  # 10
```

### Arrays

Pass Python lists to C via `c_array`:

```python
from cinpy import CModule, c_array

mod = CModule("""
    int sum(int* arr, int n) {
        int s = 0;
        for (int i = 0; i < n; i++) s += arr[i];
        return s;
    }
""")

arr = c_array(mod, "int", [1, 2, 3, 4, 5])
mod.sum(arr, 5)  # 15
```

### Pre/Post Processing

Custom argument transformation (backward compatible with v1):

```python
@from_c(
    "int double_it(int n) { return n * 2; }",
    postprocess=lambda x: x + 1,
)
def double_it(n: int) -> int: ...

double_it(5)  # 11 (5*2 + 1)
```

## Configuration

### Cache Directory

Compiled `.so` files are cached to avoid recompilation. Resolution order:

1. `cache_dir` parameter on `from_c()` / `CModule()`
2. `CINPY_CACHE_DIR` environment variable
3. `~/.cache/cinpy` (default)

### Debug Mode

For detailed error messages including full compiler output:

```bash
export CINPY_DEBUG=1
```

Or programmatically:

```python
from cinpy import set_debug
set_debug(True)
```

## API Reference

### `from_c(source, header=None, *, preprocess=None, postprocess=None, libraries=None, include_dirs=None, extra_compile_args=None, extra_link_args=None, cache_dir=None)`

Decorator that compiles C source and replaces the decorated function.

### `CModule(source, header=None, *, libraries=None, include_dirs=None, extra_compile_args=None, extra_link_args=None, cache_dir=None)`

Class that compiles a C source module and exposes all functions as attributes.

- `mod.ffi` — the CFFI FFI instance (for creating structs, arrays, etc.)
- `mod._lib` — the raw compiled library (for struct return values)

### `c_array(mod, ctype, data)` — Create a CFFI array from a Python list
### `c_struct(mod, typedef, **fields)` — Create a CFFI struct from kwargs
### `to_python(cdata, mod)` — Convert CFFI cdata to Python (struct→dict, array→list, char*→str)

## Thread Safety

CinPy uses CFFI's out-of-line API mode, which **automatically releases the GIL** during C function calls. This means:

- Multiple threads can call C functions concurrently
- Long-running C computations don't block other Python threads
- No explicit `nogil` parameter is needed

**Note:** If your C code accesses shared mutable state, you must handle synchronization yourself (mutexes, atomics, etc.).

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

### Running Examples

```bash
uv run cinpy-example operations
uv run cinpy-example structs
uv run cinpy-example arrays
```

List all available examples:

```bash
uv run cinpy-example
```

### Linting & Type Checking

```bash
ruff check src/          # lint
ruff format src/         # format
basedpyright src/        # type check
```
