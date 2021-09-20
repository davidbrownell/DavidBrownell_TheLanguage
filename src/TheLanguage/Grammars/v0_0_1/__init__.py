# TODO: Improve performance

# TODO: Support for immediate invocation of anon function:
#           [&ref]() {
#               ...
#               return foo;
#           }();

# TODO: Can 'case' be removed from match statements?
# TODO: Can 'type'/'value' be removed from match statements and inferred by matching content?
# TODO: Char primitive type
# TODO: Introduce 1..N range syntax (can be used as a generator or slice)
# TODO: Need a way to differentiate between an assignment and variable declaration? More Rust-like syntax?
# TODO: Introduce a way where templated expressions can be included by type declarations found in variable assignment statements:
#            Int32 foo = "123".parse()
#                              ^^^^^^ parse<Int32>() is invoked because variable is declared as Int32
# TODO: Add optional visibility to import statements
# TODO: Implement traits (compile-time interfaces)
# TODO: Functionality in Normalize (or maybe NormalizeIterator) so that the same set of tools could be used to parse non-whitespace-delimited languages (like C++ for example)
