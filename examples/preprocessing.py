"""Demonstrates auto-coercion (v2) vs manual preprocess (v1 compat)."""

from cinpy import from_c

# v2: auto-coercion handles str -> bytes for char* automatically
@from_c('int strlen_c(const char* s) { int n=0; while(s[n]) n++; return n; }')
def strlen_c(s: str) -> int: ...

# v1 compat: manual preprocess still works
@from_c(
    'int strlen_manual(const char* s) { int n=0; while(s[n]) n++; return n; }',
    preprocess=lambda args: (args[0].encode(),),
)
def strlen_manual(s: str) -> int: ...

if __name__ == "__main__":
    assert strlen_c("hello") == 5
    assert strlen_manual("hello") == 5
    print("preprocessing: OK")
