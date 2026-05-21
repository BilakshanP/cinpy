from cinpy.parser import extract_functions, extract_includes, generate_header, Param, FunctionSignature


def test_simple_function():
    src = "int add(int a, int b) { return a + b; }"
    fns = extract_functions(src)
    assert len(fns) == 1
    assert fns[0].name == "add"
    assert fns[0].return_type == "int"
    assert fns[0].params == [Param("int", "a"), Param("int", "b")]


def test_void_return_no_params():
    src = "void hello(void) { printf(\"hi\"); }"
    fns = extract_functions(src)
    assert fns[0].return_type == "void"
    assert fns[0].params == []


def test_pointer_params():
    src = 'int strlen_c(const char* s) { return 0; }'
    fns = extract_functions(src)
    assert fns[0].params[0].type == "const char*"
    assert fns[0].params[0].name == "s"


def test_pointer_return():
    src = 'char* greet(int n) { return "hi"; }'
    fns = extract_functions(src)
    assert fns[0].return_type == "char*"


def test_multi_function():
    src = """
    int add(int a, int b) { return a + b; }
    int sub(int a, int b) { return a - b; }
    """
    fns = extract_functions(src)
    assert len(fns) == 2
    assert fns[0].name == "add"
    assert fns[1].name == "sub"


def test_multiline_signature():
    src = """
    int
    factorial(int n) {
        if (n <= 0) return 1;
        return n * factorial(n - 1);
    }
    """
    fns = extract_functions(src)
    assert fns[0].name == "factorial"
    assert fns[0].return_type == "int"


def test_comments_stripped():
    src = """
    // this is a comment
    /* multi
       line */
    int foo(int x) { return x; }
    """
    fns = extract_functions(src)
    assert len(fns) == 1
    assert fns[0].name == "foo"


def test_extract_includes():
    src = """
    #include <stdio.h>
    #include "myheader.h"
    int foo(int x) { return x; }
    """
    includes = extract_includes(src)
    assert '#include <stdio.h>' in includes
    assert '#include "myheader.h"' in includes


def test_generate_header():
    fns = [
        FunctionSignature("int", "add", [Param("int", "a"), Param("int", "b")]),
        FunctionSignature("void", "hello", []),
    ]
    header = generate_header(fns)
    assert "int add(int a, int b);" in header
    assert "void hello(void);" in header


def test_static_function():
    src = "static int helper(int x) { return x * 2; }"
    fns = extract_functions(src)
    assert fns[0].name == "helper"
    assert "static" in fns[0].return_type
