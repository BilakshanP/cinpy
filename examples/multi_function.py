"""Multi-function module with shared state using CModule."""

from cinpy import CModule

mod = CModule("""
    static int count = 0;

    void push(void) { count++; }
    void pop(void)  { if (count > 0) count--; }
    int  size(void) { return count; }
""")

if __name__ == "__main__":
    mod.push()
    mod.push()
    mod.push()
    mod.pop()
    assert mod.size() == 2
    print("multi_function: OK")
