# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo
from v1.Parser.ParserInfos.Common.FunctionModifier import FunctionModifier
from v1.Parser.ParserInfos.Common.MethodHierarchyModifier import MethodHierarchyModifier
from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo
from v1.Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier
from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
from v1.Parser.ParserInfos.ParserInfo import ParserInfoType
from v1.Parser.ParserInfos.Statements.ClassCapabilities.StandardCapabilities import StandardCapabilities
from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionStatementParserInfoOperatorType
from v1.Parser.ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
from v1.Parser.TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
tu_region_000000 = TranslationUnitRegion(begin=Location(line=20, column=23), end=Location(line=20, column=34))
tu_region_000001 = TranslationUnitRegion(begin=Location(line=20, column=23), end=Location(line=20, column=30))
tu_region_000002 = TranslationUnitRegion(begin=Location(line=20, column=31), end=Location(line=20, column=34))
tu_region_000003 = TranslationUnitRegion(begin=Location(line=20, column=5), end=Location(line=22, column=1))
tu_region_000004 = TranslationUnitRegion(begin=Location(line=20, column=16), end=Location(line=20, column=22))
tu_region_000005 = TranslationUnitRegion(begin=Location(line=20, column=46), end=Location(line=20, column=55))
tu_region_000006 = TranslationUnitRegion(begin=Location(line=20, column=35), end=Location(line=20, column=43))
tu_region_000007 = TranslationUnitRegion(begin=Location(line=20, column=43), end=Location(line=20, column=45))
tu_region_000008 = TranslationUnitRegion(begin=Location(line=20, column=6), end=Location(line=20, column=14))
tu_region_000009 = TranslationUnitRegion(begin=Location(line=22, column=40), end=Location(line=22, column=52))
tu_region_000010 = TranslationUnitRegion(begin=Location(line=22, column=40), end=Location(line=22, column=48))
tu_region_000011 = TranslationUnitRegion(begin=Location(line=22, column=49), end=Location(line=22, column=52))
tu_region_000012 = TranslationUnitRegion(begin=Location(line=22, column=79), end=Location(line=22, column=87))
tu_region_000013 = TranslationUnitRegion(begin=Location(line=22, column=69), end=Location(line=22, column=97))
tu_region_000014 = TranslationUnitRegion(begin=Location(line=22, column=98), end=Location(line=22, column=110))
tu_region_000015 = TranslationUnitRegion(begin=Location(line=22, column=98), end=Location(line=22, column=106))
tu_region_000016 = TranslationUnitRegion(begin=Location(line=22, column=107), end=Location(line=22, column=110))
tu_region_000017 = TranslationUnitRegion(begin=Location(line=22, column=98), end=Location(line=22, column=118))
tu_region_000018 = TranslationUnitRegion(begin=Location(line=22, column=111), end=Location(line=22, column=118))
tu_region_000019 = TranslationUnitRegion(begin=Location(line=22, column=97), end=Location(line=22, column=119))
tu_region_000020 = TranslationUnitRegion(begin=Location(line=22, column=5), end=Location(line=23, column=1))
tu_region_000021 = TranslationUnitRegion(begin=Location(line=22, column=24), end=Location(line=22, column=30))
tu_region_000022 = TranslationUnitRegion(begin=Location(line=22, column=31), end=Location(line=22, column=39))
tu_region_000023 = TranslationUnitRegion(begin=Location(line=22, column=53), end=Location(line=22, column=69))
tu_region_000024 = TranslationUnitRegion(begin=Location(line=22, column=6), end=Location(line=22, column=14))
tu_region_000025 = TranslationUnitRegion(begin=Location(line=22, column=16), end=Location(line=22, column=22))
tu_region_000026 = TranslationUnitRegion(begin=Location(line=23, column=61), end=Location(line=23, column=69))
tu_region_000027 = TranslationUnitRegion(begin=Location(line=23, column=51), end=Location(line=23, column=79))
tu_region_000028 = TranslationUnitRegion(begin=Location(line=23, column=80), end=Location(line=23, column=92))
tu_region_000029 = TranslationUnitRegion(begin=Location(line=23, column=80), end=Location(line=23, column=88))
tu_region_000030 = TranslationUnitRegion(begin=Location(line=23, column=89), end=Location(line=23, column=92))
tu_region_000031 = TranslationUnitRegion(begin=Location(line=23, column=80), end=Location(line=23, column=100))
tu_region_000032 = TranslationUnitRegion(begin=Location(line=23, column=93), end=Location(line=23, column=100))
tu_region_000033 = TranslationUnitRegion(begin=Location(line=23, column=79), end=Location(line=23, column=101))
tu_region_000034 = TranslationUnitRegion(begin=Location(line=23, column=5), end=Location(line=25, column=1))
tu_region_000035 = TranslationUnitRegion(begin=Location(line=23, column=16), end=Location(line=23, column=22))
tu_region_000036 = TranslationUnitRegion(begin=Location(line=23, column=102), end=Location(line=23, column=111))
tu_region_000037 = TranslationUnitRegion(begin=Location(line=23, column=23), end=Location(line=23, column=31))
tu_region_000038 = TranslationUnitRegion(begin=Location(line=23, column=37), end=Location(line=23, column=51))
tu_region_000039 = TranslationUnitRegion(begin=Location(line=23, column=6), end=Location(line=23, column=14))
tu_region_000040 = TranslationUnitRegion(begin=Location(line=25, column=58), end=Location(line=25, column=66))
tu_region_000041 = TranslationUnitRegion(begin=Location(line=25, column=48), end=Location(line=25, column=76))
tu_region_000042 = TranslationUnitRegion(begin=Location(line=25, column=77), end=Location(line=25, column=89))
tu_region_000043 = TranslationUnitRegion(begin=Location(line=25, column=77), end=Location(line=25, column=85))
tu_region_000044 = TranslationUnitRegion(begin=Location(line=25, column=86), end=Location(line=25, column=89))
tu_region_000045 = TranslationUnitRegion(begin=Location(line=25, column=77), end=Location(line=25, column=97))
tu_region_000046 = TranslationUnitRegion(begin=Location(line=25, column=90), end=Location(line=25, column=97))
tu_region_000047 = TranslationUnitRegion(begin=Location(line=25, column=76), end=Location(line=25, column=98))
tu_region_000048 = TranslationUnitRegion(begin=Location(line=25, column=5), end=Location(line=27, column=1))
tu_region_000049 = TranslationUnitRegion(begin=Location(line=25, column=16), end=Location(line=25, column=22))
tu_region_000050 = TranslationUnitRegion(begin=Location(line=25, column=99), end=Location(line=25, column=108))
tu_region_000051 = TranslationUnitRegion(begin=Location(line=25, column=23), end=Location(line=25, column=31))
tu_region_000052 = TranslationUnitRegion(begin=Location(line=25, column=37), end=Location(line=25, column=48))
tu_region_000053 = TranslationUnitRegion(begin=Location(line=25, column=6), end=Location(line=25, column=14))
tu_region_000054 = TranslationUnitRegion(begin=Location(line=27, column=32), end=Location(line=27, column=44))
tu_region_000055 = TranslationUnitRegion(begin=Location(line=27, column=32), end=Location(line=27, column=40))
tu_region_000056 = TranslationUnitRegion(begin=Location(line=27, column=41), end=Location(line=27, column=44))
tu_region_000057 = TranslationUnitRegion(begin=Location(line=27, column=5), end=Location(line=29, column=1))
tu_region_000058 = TranslationUnitRegion(begin=Location(line=27, column=16), end=Location(line=27, column=22))
tu_region_000059 = TranslationUnitRegion(begin=Location(line=27, column=58), end=Location(line=27, column=67))
tu_region_000060 = TranslationUnitRegion(begin=Location(line=27, column=23), end=Location(line=27, column=31))
tu_region_000061 = TranslationUnitRegion(begin=Location(line=27, column=45), end=Location(line=27, column=55))
tu_region_000062 = TranslationUnitRegion(begin=Location(line=27, column=55), end=Location(line=27, column=57))
tu_region_000063 = TranslationUnitRegion(begin=Location(line=27, column=6), end=Location(line=27, column=14))
tu_region_000064 = TranslationUnitRegion(begin=Location(line=29, column=32), end=Location(line=29, column=40))
tu_region_000065 = TranslationUnitRegion(begin=Location(line=29, column=32), end=Location(line=29, column=36))
tu_region_000066 = TranslationUnitRegion(begin=Location(line=29, column=37), end=Location(line=29, column=40))
tu_region_000067 = TranslationUnitRegion(begin=Location(line=29, column=5), end=Location(line=30, column=1))
tu_region_000068 = TranslationUnitRegion(begin=Location(line=29, column=16), end=Location(line=29, column=22))
tu_region_000069 = TranslationUnitRegion(begin=Location(line=29, column=54), end=Location(line=29, column=63))
tu_region_000070 = TranslationUnitRegion(begin=Location(line=29, column=23), end=Location(line=29, column=31))
tu_region_000071 = TranslationUnitRegion(begin=Location(line=29, column=41), end=Location(line=29, column=51))
tu_region_000072 = TranslationUnitRegion(begin=Location(line=29, column=51), end=Location(line=29, column=53))
tu_region_000073 = TranslationUnitRegion(begin=Location(line=29, column=6), end=Location(line=29, column=14))
tu_region_000074 = TranslationUnitRegion(begin=Location(line=30, column=32), end=Location(line=30, column=39))
tu_region_000075 = TranslationUnitRegion(begin=Location(line=30, column=32), end=Location(line=30, column=35))
tu_region_000076 = TranslationUnitRegion(begin=Location(line=30, column=36), end=Location(line=30, column=39))
tu_region_000077 = TranslationUnitRegion(begin=Location(line=30, column=5), end=Location(line=32, column=1))
tu_region_000078 = TranslationUnitRegion(begin=Location(line=30, column=16), end=Location(line=30, column=22))
tu_region_000079 = TranslationUnitRegion(begin=Location(line=30, column=56), end=Location(line=30, column=65))
tu_region_000080 = TranslationUnitRegion(begin=Location(line=30, column=23), end=Location(line=30, column=31))
tu_region_000081 = TranslationUnitRegion(begin=Location(line=30, column=40), end=Location(line=30, column=53))
tu_region_000082 = TranslationUnitRegion(begin=Location(line=30, column=53), end=Location(line=30, column=55))
tu_region_000083 = TranslationUnitRegion(begin=Location(line=30, column=6), end=Location(line=30, column=14))
tu_region_000084 = TranslationUnitRegion(begin=Location(line=32, column=40), end=Location(line=32, column=57))
tu_region_000085 = TranslationUnitRegion(begin=Location(line=32, column=40), end=Location(line=32, column=53))
tu_region_000086 = TranslationUnitRegion(begin=Location(line=32, column=54), end=Location(line=32, column=57))
tu_region_000087 = TranslationUnitRegion(begin=Location(line=32, column=70), end=Location(line=32, column=88))
tu_region_000088 = TranslationUnitRegion(begin=Location(line=32, column=70), end=Location(line=32, column=78))
tu_region_000089 = TranslationUnitRegion(begin=Location(line=32, column=79), end=Location(line=32, column=88))
tu_region_000090 = TranslationUnitRegion(begin=Location(line=32, column=70), end=Location(line=32, column=93))
tu_region_000091 = TranslationUnitRegion(begin=Location(line=32, column=89), end=Location(line=32, column=93))
tu_region_000092 = TranslationUnitRegion(begin=Location(line=32, column=95), end=Location(line=32, column=113))
tu_region_000093 = TranslationUnitRegion(begin=Location(line=32, column=95), end=Location(line=32, column=103))
tu_region_000094 = TranslationUnitRegion(begin=Location(line=32, column=104), end=Location(line=32, column=113))
tu_region_000095 = TranslationUnitRegion(begin=Location(line=32, column=95), end=Location(line=32, column=118))
tu_region_000096 = TranslationUnitRegion(begin=Location(line=32, column=114), end=Location(line=32, column=118))
tu_region_000097 = TranslationUnitRegion(begin=Location(line=32, column=69), end=Location(line=32, column=119))
tu_region_000098 = TranslationUnitRegion(begin=Location(line=32, column=70), end=Location(line=32, column=118))
tu_region_000099 = TranslationUnitRegion(begin=Location(line=32, column=5), end=Location(line=34, column=1))
tu_region_000100 = TranslationUnitRegion(begin=Location(line=32, column=24), end=Location(line=32, column=30))
tu_region_000101 = TranslationUnitRegion(begin=Location(line=32, column=31), end=Location(line=32, column=39))
tu_region_000102 = TranslationUnitRegion(begin=Location(line=32, column=58), end=Location(line=32, column=69))
tu_region_000103 = TranslationUnitRegion(begin=Location(line=32, column=6), end=Location(line=32, column=14))
tu_region_000104 = TranslationUnitRegion(begin=Location(line=32, column=16), end=Location(line=32, column=22))
tu_region_000105 = TranslationUnitRegion(begin=Location(line=34, column=32), end=Location(line=34, column=40))
tu_region_000106 = TranslationUnitRegion(begin=Location(line=34, column=32), end=Location(line=34, column=36))
tu_region_000107 = TranslationUnitRegion(begin=Location(line=34, column=37), end=Location(line=34, column=40))
tu_region_000108 = TranslationUnitRegion(begin=Location(line=34, column=51), end=Location(line=34, column=65))
tu_region_000109 = TranslationUnitRegion(begin=Location(line=34, column=51), end=Location(line=34, column=55))
tu_region_000110 = TranslationUnitRegion(begin=Location(line=34, column=56), end=Location(line=34, column=65))
tu_region_000111 = TranslationUnitRegion(begin=Location(line=34, column=51), end=Location(line=34, column=70))
tu_region_000112 = TranslationUnitRegion(begin=Location(line=34, column=66), end=Location(line=34, column=70))
tu_region_000113 = TranslationUnitRegion(begin=Location(line=34, column=50), end=Location(line=34, column=71))
tu_region_000114 = TranslationUnitRegion(begin=Location(line=34, column=5), end=Location(line=35, column=1))
tu_region_000115 = TranslationUnitRegion(begin=Location(line=34, column=16), end=Location(line=34, column=22))
tu_region_000116 = TranslationUnitRegion(begin=Location(line=34, column=72), end=Location(line=34, column=81))
tu_region_000117 = TranslationUnitRegion(begin=Location(line=34, column=23), end=Location(line=34, column=31))
tu_region_000118 = TranslationUnitRegion(begin=Location(line=34, column=41), end=Location(line=34, column=50))
tu_region_000119 = TranslationUnitRegion(begin=Location(line=34, column=6), end=Location(line=34, column=14))
tu_region_000120 = TranslationUnitRegion(begin=Location(line=35, column=32), end=Location(line=35, column=40))
tu_region_000121 = TranslationUnitRegion(begin=Location(line=35, column=32), end=Location(line=35, column=36))
tu_region_000122 = TranslationUnitRegion(begin=Location(line=35, column=37), end=Location(line=35, column=40))
tu_region_000123 = TranslationUnitRegion(begin=Location(line=35, column=54), end=Location(line=35, column=68))
tu_region_000124 = TranslationUnitRegion(begin=Location(line=35, column=54), end=Location(line=35, column=58))
tu_region_000125 = TranslationUnitRegion(begin=Location(line=35, column=59), end=Location(line=35, column=68))
tu_region_000126 = TranslationUnitRegion(begin=Location(line=35, column=54), end=Location(line=35, column=73))
tu_region_000127 = TranslationUnitRegion(begin=Location(line=35, column=69), end=Location(line=35, column=73))
tu_region_000128 = TranslationUnitRegion(begin=Location(line=35, column=53), end=Location(line=35, column=74))
tu_region_000129 = TranslationUnitRegion(begin=Location(line=35, column=5), end=Location(line=36, column=1))
tu_region_000130 = TranslationUnitRegion(begin=Location(line=35, column=16), end=Location(line=35, column=22))
tu_region_000131 = TranslationUnitRegion(begin=Location(line=35, column=75), end=Location(line=35, column=84))
tu_region_000132 = TranslationUnitRegion(begin=Location(line=35, column=23), end=Location(line=35, column=31))
tu_region_000133 = TranslationUnitRegion(begin=Location(line=35, column=41), end=Location(line=35, column=53))
tu_region_000134 = TranslationUnitRegion(begin=Location(line=35, column=6), end=Location(line=35, column=14))
tu_region_000135 = TranslationUnitRegion(begin=Location(line=19, column=1), end=Location(line=36, column=1))
tu_region_000136 = TranslationUnitRegion(begin=Location(line=19, column=1), end=Location(line=19, column=7))
tu_region_000137 = TranslationUnitRegion(begin=Location(line=19, column=8), end=Location(line=19, column=17))
tu_region_000138 = TranslationUnitRegion(begin=Location(line=19, column=24), end=Location(line=19, column=28))
tu_region_000139 = TranslationUnitRegion(begin=Location(line=19, column=28), end=Location(line=36, column=1))
tu_region_000140 = TranslationUnitRegion(begin=Location(line=1, column=1), end=Location(line=36, column=1))


# ----------------------------------------------------------------------
statement_000000 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000000, tu_region_000001, tu_region_000002],
    value="ArchInt",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000001 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000003, tu_region_000006, tu_region_000004, None, tu_region_000003, tu_region_000007, tu_region_000005, tu_region_000003, None, None, tu_region_000008, None, None],
    name=r"GetBytes",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=True,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.standard,
    return_type=statement_000000,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000002 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000009, tu_region_000010, tu_region_000011],
    value="ThisType",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.var,
)

statement_000003 = TemplateTypeParameterParserInfo.Create(
    regions=[tu_region_000012, tu_region_000012, None],
    name=r"ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000004 = TemplateParametersParserInfo.Create(
    regions=[tu_region_000013, None, tu_region_000012, None],
    positional=None,
    any=[statement_000003, ],
    keyword=None,
)

statement_000005 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000014, tu_region_000015, tu_region_000016],
    value="ArchiveT",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000006 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000017, None, tu_region_000018],  # type: ignore
    type=statement_000005,
    is_variadic=None,
    name=r"archive",
    default_value=None,
)

statement_000007 = FuncParametersParserInfo.Create(
    regions=[tu_region_000019, None, tu_region_000017, None],
    positional=None,
    any=[statement_000006, ],
    keyword=None,
)

statement_000008 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000020, tu_region_000023, tu_region_000021, None, tu_region_000020, tu_region_000019, None, tu_region_000022, None, None, tu_region_000024, None, tu_region_000025],
    name=r"OperatorType.Deserialize",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=statement_000004,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000007,
    mutability_param=None,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000002,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=True,
)

statement_000009 = TemplateTypeParameterParserInfo.Create(
    regions=[tu_region_000026, tu_region_000026, None],
    name=r"ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000010 = TemplateParametersParserInfo.Create(
    regions=[tu_region_000027, None, tu_region_000026, None],
    positional=None,
    any=[statement_000009, ],
    keyword=None,
)

statement_000011 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000028, tu_region_000029, tu_region_000030],
    value="ArchiveT",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000012 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000031, None, tu_region_000032],  # type: ignore
    type=statement_000011,
    is_variadic=None,
    name=r"archive",
    default_value=None,
)

statement_000013 = FuncParametersParserInfo.Create(
    regions=[tu_region_000033, None, tu_region_000031, None],
    positional=None,
    any=[statement_000012, ],
    keyword=None,
)

statement_000014 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000034, tu_region_000038, tu_region_000035, None, tu_region_000034, tu_region_000033, tu_region_000036, tu_region_000037, None, None, tu_region_000039, None, None],
    name=r"OperatorType.Serialize",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=statement_000010,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000013,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000015 = TemplateTypeParameterParserInfo.Create(
    regions=[tu_region_000040, tu_region_000040, None],
    name=r"VisitorT",
    is_variadic=None,
    default_type=None,
)

statement_000016 = TemplateParametersParserInfo.Create(
    regions=[tu_region_000041, None, tu_region_000040, None],
    positional=None,
    any=[statement_000015, ],
    keyword=None,
)

statement_000017 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000042, tu_region_000043, tu_region_000044],
    value="VisitorT",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000018 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000045, None, tu_region_000046],  # type: ignore
    type=statement_000017,
    is_variadic=None,
    name=r"visitor",
    default_value=None,
)

statement_000019 = FuncParametersParserInfo.Create(
    regions=[tu_region_000047, None, tu_region_000045, None],
    positional=None,
    any=[statement_000018, ],
    keyword=None,
)

statement_000020 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000048, tu_region_000052, tu_region_000049, None, tu_region_000048, tu_region_000047, tu_region_000050, tu_region_000051, None, None, tu_region_000053, None, None],
    name=r"OperatorType.Accept",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=statement_000016,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000019,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000021 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000054, tu_region_000055, tu_region_000056],
    value="ThisType",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.var,
)

statement_000022 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000057, tu_region_000061, tu_region_000058, None, tu_region_000057, tu_region_000062, tu_region_000059, tu_region_000060, None, None, tu_region_000063, None, None],
    name=r"OperatorType.Clone",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=True,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000021,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000023 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000064, tu_region_000065, tu_region_000066],
    value="Bool",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000024 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000067, tu_region_000071, tu_region_000068, None, tu_region_000067, tu_region_000072, tu_region_000069, tu_region_000070, None, None, tu_region_000073, None, None],
    name=r"OperatorType.ToBool",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=True,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000023,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000025 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000074, tu_region_000075, tu_region_000076],
    value="Str",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000026 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000077, tu_region_000081, tu_region_000078, None, tu_region_000077, tu_region_000082, tu_region_000079, tu_region_000080, None, None, tu_region_000083, None, None],
    name=r"OperatorType.ToString",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=True,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000025,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000027 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000084, tu_region_000085, tu_region_000086],
    value="CompareResult",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000028 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000087, tu_region_000088, tu_region_000089],
    value="ThisType",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000029 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000090, None, tu_region_000091],  # type: ignore
    type=statement_000028,
    is_variadic=None,
    name=r"this",
    default_value=None,
)

statement_000030 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000092, tu_region_000093, tu_region_000094],
    value="ThisType",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000031 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000095, None, tu_region_000096],  # type: ignore
    type=statement_000030,
    is_variadic=None,
    name=r"that",
    default_value=None,
)

statement_000032 = FuncParametersParserInfo.Create(
    regions=[tu_region_000097, None, tu_region_000098, None],
    positional=None,
    any=[statement_000029, statement_000031, ],
    keyword=None,
)

statement_000033 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000099, tu_region_000102, tu_region_000100, None, tu_region_000099, tu_region_000097, None, tu_region_000101, None, None, tu_region_000103, None, tu_region_000104],
    name=r"OperatorType.Compare",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000032,
    mutability_param=None,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000027,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=True,
)

statement_000034 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000105, tu_region_000106, tu_region_000107],
    value="Bool",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000035 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000108, tu_region_000109, tu_region_000110],
    value="None",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000036 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000111, None, tu_region_000112],  # type: ignore
    type=statement_000035,
    is_variadic=None,
    name=r"that",
    default_value=None,
)

statement_000037 = FuncParametersParserInfo.Create(
    regions=[tu_region_000113, None, tu_region_000111, None],
    positional=None,
    any=[statement_000036, ],
    keyword=None,
)

statement_000038 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000114, tu_region_000118, tu_region_000115, None, tu_region_000114, tu_region_000113, tu_region_000116, tu_region_000117, None, None, tu_region_000119, None, None],
    name=r"OperatorType.Equal",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000037,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000034,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000039 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000120, tu_region_000121, tu_region_000122],
    value="Bool",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000040 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000123, tu_region_000124, tu_region_000125],
    value="None",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000041 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000126, None, tu_region_000127],  # type: ignore
    type=statement_000040,
    is_variadic=None,
    name=r"that",
    default_value=None,
)

statement_000042 = FuncParametersParserInfo.Create(
    regions=[tu_region_000128, None, tu_region_000126, None],
    positional=None,
    any=[statement_000041, ],
    keyword=None,
)

statement_000043 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000129, tu_region_000133, tu_region_000130, None, tu_region_000129, tu_region_000128, tu_region_000131, tu_region_000132, None, None, tu_region_000134, None, None],
    name=r"OperatorType.NotEqual",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=StandardCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000042,
    mutability_param=MutabilityModifier.immutable,
    method_hierarchy_modifier_param=MethodHierarchyModifier.override,
    return_type=statement_000039,
    documentation=None,
    captured_variables=None,
    is_deferred=True,
    is_exceptional=None,
    is_static=None,
)

statement_000044 = ClassStatementParserInfo.Create(
    regions=[tu_region_000135, tu_region_000136, tu_region_000139, tu_region_000137, tu_region_000138, None, None, None, None, tu_region_000135, None, None],
    name=r"None",
    visibility_param=VisibilityModifier.public,
    statements=[statement_000001, statement_000008, statement_000014, statement_000020, statement_000022, statement_000024, statement_000026, statement_000033, statement_000038, statement_000043, ],
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
    self_referencing_type_names=[r"ThisType", ],
)

root_parser_info = RootStatementParserInfo.Create(
    regions=[tu_region_000140, tu_region_000140, None],
    name=r"None",
    statements=[statement_000044, ],
    documentation=None,
)
