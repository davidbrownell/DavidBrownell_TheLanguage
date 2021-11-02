import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.StandardTypeImpl import StandardTypeImpl

    from ...GrammarInfo import AST, DynamicPhrasesType


# ----------------------------------------------------------------------
class StandardTemplateDecoratorType(StandardTypeImpl):
    """\
    Type declaration.

    <type_name> <modifier>?

    Examples:
        Int
        Int var
    """

    PHRASE_NAME                             = "Standard TemplateDecoratorType"

    # We are using StandardTypeImpl so that we can better control errors generated
    # when someone attempts to use detailed information as they would when using the
    # type as a part of standard code.

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardTemplateDecoratorType, self).__init__(
            self.PHRASE_NAME,
            DynamicPhrasesType.TemplateDecoratorTypes,
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ):
        parser_info = super(StandardTemplateDecoratorType, cls).ExtractParserInfo(node)

        if parser_info.TypeName not in [
            "Bool",
            "Int",
            "Num",
            "String",
        ]:
            raise Exception("BugBug0")

        if parser_info.Modifier is not None:
            raise Exception("BugBug1")

        if parser_info.Templates is not None:
            raise Exception("BugBug2")

        if parser_info.Constraints is not None:
            raise Exception("BugBug3")
