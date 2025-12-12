from cinpy import from_c

@from_c(r"""
        void print_int(int n) {
            printf("%d\n", n);
        }
        """)
def print_int(n: int) -> None: ...

@from_c(r"""
        void print_float(double n) {
            printf("%.2lf\n", n);
        }
        """)
def print_float(n: float) -> None:
    """
    Print the provided `float` to the `stdout` upto `2` decimal places.
    """

    ...

@from_c(
        r"""
        void print_str(char* s) {
            printf("%s", s);
        }
        """,
        preprocess=lambda s: (s[0].encode(),)
)
def print_str(s: str) -> None: ...

if __name__ == "__main__":
    print_int(10)
    print_float(10)
    # print_s(bytes("Hi", "utf-8"))
    print_str("Hi\n")