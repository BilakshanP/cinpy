from operations import add
from printing import print_int

if __name__ == "__main__":
    a: int = 10
    b: int = 59

    s: int = add(a, b)

    print_int(s)