from cinpy import from_c

@from_c(r"""
        int default_eg(int n) {
            return n;
        }
        """)
def default_eg(n: int = 10) -> int: ...

if __name__ == "__main__":
    assert default_eg() == 10
    assert default_eg(1) == 1
