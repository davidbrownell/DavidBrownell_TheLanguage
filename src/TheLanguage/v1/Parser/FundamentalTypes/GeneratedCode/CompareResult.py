# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.FunctionModifier import FunctionModifier
from v1.Parser.ParserInfos.Common.MethodHierarchyModifier import MethodHierarchyModifier
from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
from v1.Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier
from v1.Parser.ParserInfos.ParserInfo import ParserInfoType
from v1.Parser.ParserInfos.Statements.ClassCapabilities.StandardCapabilities import StandardCapabilities
from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
from v1.Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
from v1.Parser.ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
from v1.Parser.TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
tu_region_000000 = TranslationUnitRegion(begin=Location(line=23, column=5), end=Location(line=24, column=1))
tu_region_000001 = TranslationUnitRegion(begin=Location(line=22, column=1), end=Location(line=24, column=1))
tu_region_000002 = TranslationUnitRegion(begin=Location(line=22, column=1), end=Location(line=22, column=7))
tu_region_000003 = TranslationUnitRegion(begin=Location(line=22, column=14), end=Location(line=22, column=27))
tu_region_000004 = TranslationUnitRegion(begin=Location(line=22, column=27), end=Location(line=24, column=1))
tu_region_000005 = TranslationUnitRegion(begin=Location(line=1, column=1), end=Location(line=24, column=1))


# ----------------------------------------------------------------------
statement_000000 = PassStatementParserInfo.Create([tu_region_000000])
statement_000001 = ClassStatementParserInfo.Create(
    regions=[tu_region_000001, tu_region_000002, tu_region_000004, tu_region_000001, tu_region_000003, None, None, None, None, tu_region_000001, None, None],
    name=r"CompareResult",
    visibility_param=VisibilityModifier.public,
    statements=[statement_000000, ],
    templates_param=None,
    parent_class_capabilities=None,
    class_capabilities=StandardCapabilities,
    class_modifier_param=ClassModifier.immutable,
    documentation=None,
    constraints=None,
    extends=None,
    implements=None,
    uses=None,
    constructor_visibility_param=VisibilityModifier.public,
    is_abstract=None,
    is_final=None,
)

root_parser_info = RootStatementParserInfo.Create(
    regions=[tu_region_000005, tu_region_000005, None],
    name=r"CompareResult.TheLanguage",
    statements=[statement_000001, ],
    documentation=None,
)
