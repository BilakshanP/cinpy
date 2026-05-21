from cinpy import from_c

@from_c('void print_int(int n) { printf("%d\\n", n); }')
def print_int(n: int) -> None: ...

@from_c('void print_float(double n) { printf("%.2lf\\n", n); }')
def print_float(n: float) -> None: ...

# Auto-coercion: str -> bytes for char* (no preprocess needed!)
@from_c('void print_str(const char* s) { printf("%s", s); }')
def print_str(s: str) -> None: ...

if __name__ == "__main__":
    print_int(10)
    print_float(3.14)
    print_str("Hello from C!\n")
