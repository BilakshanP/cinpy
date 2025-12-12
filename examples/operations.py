from cinpy import from_c

@from_c("int add(int a, int b) { return a + b; }")
def add(a: int, b: int) -> int: ...

if __name__ == "__main__":
    assert add(-1, 43) == 42