"""Passing arrays to C functions."""

from cinpy import CModule, c_array

mod = CModule("""
    int sum(int* arr, int n) {
        int s = 0;
        for (int i = 0; i < n; i++) s += arr[i];
        return s;
    }

    void scale(double* arr, int n, double factor) {
        for (int i = 0; i < n; i++) arr[i] *= factor;
    }
""")

if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    arr = c_array(mod, "int", data)
    assert mod.sum(arr, len(data)) == 15

    floats = c_array(mod, "double", [1.0, 2.0, 3.0])
    mod.scale(floats, 3, 2.5)
    assert [floats[i] for i in range(3)] == [2.5, 5.0, 7.5]
    print("arrays: OK")
