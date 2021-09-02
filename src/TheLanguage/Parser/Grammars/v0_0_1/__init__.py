# TODO:

# Statements:
#   - ClassCompilerData


# TODO: Ensure that all phrases are as forgiving as possible during parsing; note that this might not be the way
#       to go now that errors are more precise and ambiguities are properly detected. Make things less forgiving
#       if it makes more sense to go in this direction.

# TODO: Problems when ending with comments:
#     class Foo():
#         pass
#
#     # Comment 1
#     # Comment 2

# TODO: Ensure that everything that uses YamlRepr.ObjectReprImplBase is properly initializing with include_class_info=False
