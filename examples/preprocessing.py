from cinpy import from_c
from typing import Any

def str_to_bytes(args: tuple[Any, ...]) -> tuple[Any, ...]:
    out: list[Any] = []
    for a in args:
        if isinstance(a, str):
            out.append(a.encode("utf-8"))
        else:
            out.append(a)
    return tuple(out)

@from_c(
    r"""
    int strlen_c(const char* s) {
        int n = 0;
        while (s[n]) n++;
        return n;
    }
    """,
    preprocess=str_to_bytes,
)
def strlen_c(s: str) -> int: ...

if __name__ == "__main__":
    assert strlen_c("hello") == 5
