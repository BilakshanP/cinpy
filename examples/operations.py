from cinpy import from_c

@from_c("int add(int a, int b) { return a + b; }")
def add(a: int, b: int) -> int: ...

@from_c("int sub(int a, int b) { return a - b; }")
def sub(a: int, b: int) -> int: ...

if __name__ == "__main__":
    assert add(-1, 43) == 42
    assert sub(10, 3) == 7
    print("operations: OK")
