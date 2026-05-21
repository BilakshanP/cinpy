"""Working with C structs via CModule."""

from cinpy import CModule, c_struct, to_python

mod = CModule(
    """
    typedef struct { double x; double y; } Vec2;

    Vec2 vec2_add(Vec2 a, Vec2 b) {
        Vec2 r = {a.x + b.x, a.y + b.y};
        return r;
    }

    double vec2_dot(Vec2 a, Vec2 b) {
        return a.x * b.x + a.y * b.y;
    }
""",
    header="""
    typedef struct { double x; double y; } Vec2;
    Vec2 vec2_add(Vec2 a, Vec2 b);
    double vec2_dot(Vec2 a, Vec2 b);
""",
)

if __name__ == "__main__":
    a = c_struct(mod, "Vec2", x=1.0, y=2.0)
    b = c_struct(mod, "Vec2", x=3.0, y=4.0)

    result = mod._lib.vec2_add(a, b)
    print(to_python(result, mod))  # {'x': 4.0, 'y': 6.0}

    dot = mod.vec2_dot(a, b)
    print(f"dot product: {dot}")  # 11.0
    assert dot == 11.0
    print("structs: OK")
