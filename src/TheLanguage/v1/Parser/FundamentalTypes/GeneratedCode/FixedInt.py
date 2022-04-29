# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentParserInfo
from v1.Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo
from v1.Parser.ParserInfos.Common.MethodModifier import MethodModifier
from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
from v1.Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier
from v1.Parser.ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
from v1.Parser.ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
from v1.Parser.ParserInfos.ParserInfo import ParserInfoType
from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementClauseParserInfo
from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
from v1.Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
from v1.Parser.Region import Region


# ----------------------------------------------------------------------
region_000000 = Region(begin=Location(line=161, column=4), end=Location(line=161, column=14))
region_000001 = Region(begin=Location(line=161, column=15), end=Location(line=161, column=38))
region_000002 = Region(begin=Location(line=161, column=14), end=Location(line=161, column=39))
region_000003 = Region(begin=Location(line=161, column=4), end=Location(line=161, column=39))
region_000004 = Region(begin=Location(line=162, column=5), end=Location(line=163, column=1))
region_000005 = Region(begin=Location(line=161, column=1), end=Location(line=163, column=1))
region_000006 = Region(begin=Location(line=161, column=39), end=Location(line=163, column=1))


# ----------------------------------------------------------------------
statement_000000 = FuncOrTypeExpressionParserInfo.Create(
    regions=[region_000000, region_000000],
    name="IsDefined!",
)

statement_000001 = StringExpressionParserInfo.Create(
    regions=[region_000001],
    value="__architecture_bytes!",
)

statement_000001 = FuncArgumentParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000001, None],
    expression=statement_000001,
    keyword=None,
)

statement_000002 = FuncArgumentsParserInfo.Create(
    regions=[region_000002, region_000002],
    arguments=[statement_000001, ],
)

statement_000003 = CallExpressionParserInfo.Create(
    regions=[region_000003, region_000002],
    expression=statement_000000,
    arguments=statement_000002,
)

statement_000004 = PassStatementParserInfo.Create([region_000004])
statement_000005 = IfStatementClauseParserInfo.Create(
    regions=[region_000005, region_000006, None],
    expression=statement_000003,
    statements=[statement_000004, ],
    documentation=None,
)

statement_000005 = IfStatementParserInfo.Create(
    regions=[region_000005, None, None],
    clauses=[statement_000005, ],
    else_statements=None,
    else_documentation=None,
)

public_exports = [
    statement_000005,
]
