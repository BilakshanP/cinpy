from cinpy import from_c

@from_c("""
    int factorial(int n) {
        if (n <= 0) return 1;
        return n * factorial(n - 1);
    }
""")
def factorial(n: int) -> int: ...

if __name__ == "__main__":
    assert factorial(-1) == 1
    assert factorial(5) == 120
    print("recursion: OK")
