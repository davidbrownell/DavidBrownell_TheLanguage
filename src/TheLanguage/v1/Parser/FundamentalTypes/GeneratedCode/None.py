# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.MiniLanguage.Types.BooleanType import BooleanType
from v1.Parser.MiniLanguage.Types.CustomType import CustomType
from v1.Parser.MiniLanguage.Types.NoneType import NoneType
from v1.Parser.MiniLanguage.Types.StringType import StringType
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo
from v1.Parser.ParserInfos.Common.MethodModifier import MethodModifier
from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo
from v1.Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier
from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
from v1.Parser.ParserInfos.ParserInfo import ParserInfoType
from v1.Parser.ParserInfos.Statements.ClassCapabilities.StandardCapabilities import StandardCapabilities
from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionStatementParserInfoOperatorType
from v1.Parser.Region import Region


# ----------------------------------------------------------------------
region_000000 = Region(begin=Location(line=20, column=23), end=Location(line=20, column=34))
region_000001 = Region(begin=Location(line=20, column=23), end=Location(line=20, column=30))
region_000002 = Region(begin=Location(line=20, column=31), end=Location(line=20, column=34))
region_000003 = Region(begin=Location(line=20, column=5), end=Location(line=22, column=1))
region_000004 = Region(begin=Location(line=20, column=16), end=Location(line=20, column=22))
region_000005 = Region(begin=Location(line=20, column=46), end=Location(line=20, column=55))
region_000006 = Region(begin=Location(line=20, column=35), end=Location(line=20, column=43))
region_000007 = Region(begin=Location(line=20, column=43), end=Location(line=20, column=45))
region_000008 = Region(begin=Location(line=20, column=6), end=Location(line=20, column=14))
region_000009 = Region(begin=Location(line=22, column=40), end=Location(line=22, column=52))
region_000010 = Region(begin=Location(line=22, column=40), end=Location(line=22, column=48))
region_000011 = Region(begin=Location(line=22, column=49), end=Location(line=22, column=52))
region_000012 = Region(begin=Location(line=22, column=70), end=Location(line=22, column=78))
region_000013 = Region(begin=Location(line=22, column=69), end=Location(line=22, column=79))
region_000014 = Region(begin=Location(line=22, column=80), end=Location(line=22, column=92))
region_000015 = Region(begin=Location(line=22, column=80), end=Location(line=22, column=88))
region_000016 = Region(begin=Location(line=22, column=89), end=Location(line=22, column=92))
region_000017 = Region(begin=Location(line=22, column=80), end=Location(line=22, column=100))
region_000018 = Region(begin=Location(line=22, column=93), end=Location(line=22, column=100))
region_000019 = Region(begin=Location(line=22, column=79), end=Location(line=22, column=101))
region_000020 = Region(begin=Location(line=22, column=5), end=Location(line=23, column=1))
region_000021 = Region(begin=Location(line=22, column=24), end=Location(line=22, column=30))
region_000022 = Region(begin=Location(line=22, column=31), end=Location(line=22, column=39))
region_000023 = Region(begin=Location(line=22, column=53), end=Location(line=22, column=69))
region_000024 = Region(begin=Location(line=22, column=6), end=Location(line=22, column=14))
region_000025 = Region(begin=Location(line=22, column=16), end=Location(line=22, column=22))
region_000026 = Region(begin=Location(line=23, column=52), end=Location(line=23, column=60))
region_000027 = Region(begin=Location(line=23, column=51), end=Location(line=23, column=61))
region_000028 = Region(begin=Location(line=23, column=62), end=Location(line=23, column=74))
region_000029 = Region(begin=Location(line=23, column=62), end=Location(line=23, column=70))
region_000030 = Region(begin=Location(line=23, column=71), end=Location(line=23, column=74))
region_000031 = Region(begin=Location(line=23, column=62), end=Location(line=23, column=82))
region_000032 = Region(begin=Location(line=23, column=75), end=Location(line=23, column=82))
region_000033 = Region(begin=Location(line=23, column=61), end=Location(line=23, column=83))
region_000034 = Region(begin=Location(line=23, column=5), end=Location(line=25, column=1))
region_000035 = Region(begin=Location(line=23, column=16), end=Location(line=23, column=22))
region_000036 = Region(begin=Location(line=23, column=84), end=Location(line=23, column=93))
region_000037 = Region(begin=Location(line=23, column=23), end=Location(line=23, column=31))
region_000038 = Region(begin=Location(line=23, column=37), end=Location(line=23, column=51))
region_000039 = Region(begin=Location(line=23, column=6), end=Location(line=23, column=14))
region_000040 = Region(begin=Location(line=25, column=49), end=Location(line=25, column=57))
region_000041 = Region(begin=Location(line=25, column=48), end=Location(line=25, column=58))
region_000042 = Region(begin=Location(line=25, column=59), end=Location(line=25, column=71))
region_000043 = Region(begin=Location(line=25, column=59), end=Location(line=25, column=67))
region_000044 = Region(begin=Location(line=25, column=68), end=Location(line=25, column=71))
region_000045 = Region(begin=Location(line=25, column=59), end=Location(line=25, column=79))
region_000046 = Region(begin=Location(line=25, column=72), end=Location(line=25, column=79))
region_000047 = Region(begin=Location(line=25, column=58), end=Location(line=25, column=80))
region_000048 = Region(begin=Location(line=25, column=5), end=Location(line=27, column=1))
region_000049 = Region(begin=Location(line=25, column=16), end=Location(line=25, column=22))
region_000050 = Region(begin=Location(line=25, column=81), end=Location(line=25, column=90))
region_000051 = Region(begin=Location(line=25, column=23), end=Location(line=25, column=31))
region_000052 = Region(begin=Location(line=25, column=37), end=Location(line=25, column=48))
region_000053 = Region(begin=Location(line=25, column=6), end=Location(line=25, column=14))
region_000054 = Region(begin=Location(line=27, column=32), end=Location(line=27, column=44))
region_000055 = Region(begin=Location(line=27, column=32), end=Location(line=27, column=40))
region_000056 = Region(begin=Location(line=27, column=41), end=Location(line=27, column=44))
region_000057 = Region(begin=Location(line=27, column=5), end=Location(line=29, column=1))
region_000058 = Region(begin=Location(line=27, column=16), end=Location(line=27, column=22))
region_000059 = Region(begin=Location(line=27, column=58), end=Location(line=27, column=67))
region_000060 = Region(begin=Location(line=27, column=23), end=Location(line=27, column=31))
region_000061 = Region(begin=Location(line=27, column=45), end=Location(line=27, column=55))
region_000062 = Region(begin=Location(line=27, column=55), end=Location(line=27, column=57))
region_000063 = Region(begin=Location(line=27, column=6), end=Location(line=27, column=14))
region_000064 = Region(begin=Location(line=29, column=32), end=Location(line=29, column=40))
region_000065 = Region(begin=Location(line=29, column=32), end=Location(line=29, column=36))
region_000066 = Region(begin=Location(line=29, column=37), end=Location(line=29, column=40))
region_000067 = Region(begin=Location(line=29, column=5), end=Location(line=30, column=1))
region_000068 = Region(begin=Location(line=29, column=16), end=Location(line=29, column=22))
region_000069 = Region(begin=Location(line=29, column=54), end=Location(line=29, column=63))
region_000070 = Region(begin=Location(line=29, column=23), end=Location(line=29, column=31))
region_000071 = Region(begin=Location(line=29, column=41), end=Location(line=29, column=51))
region_000072 = Region(begin=Location(line=29, column=51), end=Location(line=29, column=53))
region_000073 = Region(begin=Location(line=29, column=6), end=Location(line=29, column=14))
region_000074 = Region(begin=Location(line=30, column=32), end=Location(line=30, column=39))
region_000075 = Region(begin=Location(line=30, column=32), end=Location(line=30, column=35))
region_000076 = Region(begin=Location(line=30, column=36), end=Location(line=30, column=39))
region_000077 = Region(begin=Location(line=30, column=5), end=Location(line=32, column=1))
region_000078 = Region(begin=Location(line=30, column=16), end=Location(line=30, column=22))
region_000079 = Region(begin=Location(line=30, column=56), end=Location(line=30, column=65))
region_000080 = Region(begin=Location(line=30, column=23), end=Location(line=30, column=31))
region_000081 = Region(begin=Location(line=30, column=40), end=Location(line=30, column=53))
region_000082 = Region(begin=Location(line=30, column=53), end=Location(line=30, column=55))
region_000083 = Region(begin=Location(line=30, column=6), end=Location(line=30, column=14))
region_000084 = Region(begin=Location(line=32, column=40), end=Location(line=32, column=57))
region_000085 = Region(begin=Location(line=32, column=40), end=Location(line=32, column=53))
region_000086 = Region(begin=Location(line=32, column=54), end=Location(line=32, column=57))
region_000087 = Region(begin=Location(line=32, column=70), end=Location(line=32, column=88))
region_000088 = Region(begin=Location(line=32, column=70), end=Location(line=32, column=78))
region_000089 = Region(begin=Location(line=32, column=79), end=Location(line=32, column=88))
region_000090 = Region(begin=Location(line=32, column=70), end=Location(line=32, column=93))
region_000091 = Region(begin=Location(line=32, column=89), end=Location(line=32, column=93))
region_000092 = Region(begin=Location(line=32, column=95), end=Location(line=32, column=113))
region_000093 = Region(begin=Location(line=32, column=95), end=Location(line=32, column=103))
region_000094 = Region(begin=Location(line=32, column=104), end=Location(line=32, column=113))
region_000095 = Region(begin=Location(line=32, column=95), end=Location(line=32, column=118))
region_000096 = Region(begin=Location(line=32, column=114), end=Location(line=32, column=118))
region_000097 = Region(begin=Location(line=32, column=69), end=Location(line=32, column=119))
region_000098 = Region(begin=Location(line=32, column=70), end=Location(line=32, column=118))
region_000099 = Region(begin=Location(line=32, column=5), end=Location(line=34, column=1))
region_000100 = Region(begin=Location(line=32, column=24), end=Location(line=32, column=30))
region_000101 = Region(begin=Location(line=32, column=31), end=Location(line=32, column=39))
region_000102 = Region(begin=Location(line=32, column=58), end=Location(line=32, column=69))
region_000103 = Region(begin=Location(line=32, column=6), end=Location(line=32, column=14))
region_000104 = Region(begin=Location(line=32, column=16), end=Location(line=32, column=22))
region_000105 = Region(begin=Location(line=34, column=32), end=Location(line=34, column=40))
region_000106 = Region(begin=Location(line=34, column=32), end=Location(line=34, column=36))
region_000107 = Region(begin=Location(line=34, column=37), end=Location(line=34, column=40))
region_000108 = Region(begin=Location(line=34, column=51), end=Location(line=34, column=65))
region_000109 = Region(begin=Location(line=34, column=51), end=Location(line=34, column=55))
region_000110 = Region(begin=Location(line=34, column=56), end=Location(line=34, column=65))
region_000111 = Region(begin=Location(line=34, column=51), end=Location(line=34, column=70))
region_000112 = Region(begin=Location(line=34, column=66), end=Location(line=34, column=70))
region_000113 = Region(begin=Location(line=34, column=50), end=Location(line=34, column=71))
region_000114 = Region(begin=Location(line=34, column=5), end=Location(line=35, column=1))
region_000115 = Region(begin=Location(line=34, column=16), end=Location(line=34, column=22))
region_000116 = Region(begin=Location(line=34, column=72), end=Location(line=34, column=81))
region_000117 = Region(begin=Location(line=34, column=23), end=Location(line=34, column=31))
region_000118 = Region(begin=Location(line=34, column=41), end=Location(line=34, column=50))
region_000119 = Region(begin=Location(line=34, column=6), end=Location(line=34, column=14))
region_000120 = Region(begin=Location(line=35, column=32), end=Location(line=35, column=40))
region_000121 = Region(begin=Location(line=35, column=32), end=Location(line=35, column=36))
region_000122 = Region(begin=Location(line=35, column=37), end=Location(line=35, column=40))
region_000123 = Region(begin=Location(line=35, column=54), end=Location(line=35, column=68))
region_000124 = Region(begin=Location(line=35, column=54), end=Location(line=35, column=58))
region_000125 = Region(begin=Location(line=35, column=59), end=Location(line=35, column=68))
region_000126 = Region(begin=Location(line=35, column=54), end=Location(line=35, column=73))
region_000127 = Region(begin=Location(line=35, column=69), end=Location(line=35, column=73))
region_000128 = Region(begin=Location(line=35, column=53), end=Location(line=35, column=74))
region_000129 = Region(begin=Location(line=35, column=5), end=Location(line=36, column=1))
region_000130 = Region(begin=Location(line=35, column=16), end=Location(line=35, column=22))
region_000131 = Region(begin=Location(line=35, column=75), end=Location(line=35, column=84))
region_000132 = Region(begin=Location(line=35, column=23), end=Location(line=35, column=31))
region_000133 = Region(begin=Location(line=35, column=41), end=Location(line=35, column=53))
region_000134 = Region(begin=Location(line=35, column=6), end=Location(line=35, column=14))
region_000135 = Region(begin=Location(line=19, column=1), end=Location(line=36, column=1))
region_000136 = Region(begin=Location(line=19, column=1), end=Location(line=19, column=7))
region_000137 = Region(begin=Location(line=19, column=8), end=Location(line=19, column=17))
region_000138 = Region(begin=Location(line=19, column=24), end=Location(line=19, column=28))
region_000139 = Region(begin=Location(line=19, column=28), end=Location(line=36, column=1))


# ----------------------------------------------------------------------
statement_000000 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000000, region_000001, region_000002],
    value=CustomType("ArchInt"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000001 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000003, region_000007, region_000004, region_000005, region_000003, region_000006, None, None, None, region_000008, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=True,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.standard,
    return_type=statement_000000,
    name="GetBytes",
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000002 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000009, region_000010, region_000011],
    value=CustomType("ThisType"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.var,
)

statement_000003 = TemplateTypeParameterParserInfo.Create(
    regions=[region_000012, region_000012, None],
    name="ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000004 = TemplateParametersParserInfo.Create(
    regions=[region_000013, None, region_000012, None],
    positional=None,
    any=[statement_000003, ],
    keyword=None,
)

statement_000005 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000014, region_000015, region_000016],
    value=CustomType("ArchiveT"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000006 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000017, None, region_000018],  # type: ignore
    type=statement_000005,
    is_variadic=None,
    name="archive",
    default_value=None,
)

statement_000007 = FuncParametersParserInfo.Create(
    regions=[region_000019, None, region_000017, None],
    positional=None,
    any_args=[statement_000006, ],
    keyword=None,
)

statement_000008 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000020, region_000019, region_000021, None, region_000022, region_000023, None, None, None, region_000024, None, None, None, None, region_000025],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000007,
    visibility_param=VisibilityModifier.public,
    mutability_param=None,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000002,
    name=FuncDefinitionStatementParserInfoOperatorType.Deserialize,
    documentation=None,
    templates=statement_000004,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=True,
)

statement_000009 = TemplateTypeParameterParserInfo.Create(
    regions=[region_000026, region_000026, None],
    name="ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000010 = TemplateParametersParserInfo.Create(
    regions=[region_000027, None, region_000026, None],
    positional=None,
    any=[statement_000009, ],
    keyword=None,
)

statement_000011 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000028, region_000029, region_000030],
    value=CustomType("ArchiveT"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000012 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000031, None, region_000032],  # type: ignore
    type=statement_000011,
    is_variadic=None,
    name="archive",
    default_value=None,
)

statement_000013 = FuncParametersParserInfo.Create(
    regions=[region_000033, None, region_000031, None],
    positional=None,
    any_args=[statement_000012, ],
    keyword=None,
)

statement_000014 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000034, region_000033, region_000035, region_000036, region_000037, region_000038, None, None, None, region_000039, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000013,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.Serialize,
    documentation=None,
    templates=statement_000010,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000015 = TemplateTypeParameterParserInfo.Create(
    regions=[region_000040, region_000040, None],
    name="VisitorT",
    is_variadic=None,
    default_type=None,
)

statement_000016 = TemplateParametersParserInfo.Create(
    regions=[region_000041, None, region_000040, None],
    positional=None,
    any=[statement_000015, ],
    keyword=None,
)

statement_000017 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000042, region_000043, region_000044],
    value=CustomType("VisitorT"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000018 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000045, None, region_000046],  # type: ignore
    type=statement_000017,
    is_variadic=None,
    name="visitor",
    default_value=None,
)

statement_000019 = FuncParametersParserInfo.Create(
    regions=[region_000047, None, region_000045, None],
    positional=None,
    any_args=[statement_000018, ],
    keyword=None,
)

statement_000020 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000048, region_000047, region_000049, region_000050, region_000051, region_000052, None, None, None, region_000053, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000019,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.Accept,
    documentation=None,
    templates=statement_000016,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000021 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000054, region_000055, region_000056],
    value=CustomType("ThisType"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.var,
)

statement_000022 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000057, region_000062, region_000058, region_000059, region_000060, region_000061, None, None, None, region_000063, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=True,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000021,
    name=FuncDefinitionStatementParserInfoOperatorType.Clone,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000023 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000064, region_000065, region_000066],
    value=BooleanType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000024 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000067, region_000072, region_000068, region_000069, region_000070, region_000071, None, None, None, region_000073, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=True,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000023,
    name=FuncDefinitionStatementParserInfoOperatorType.ToBool,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000025 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000074, region_000075, region_000076],
    value=StringType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000026 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000077, region_000082, region_000078, region_000079, region_000080, region_000081, None, None, None, region_000083, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=True,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000025,
    name=FuncDefinitionStatementParserInfoOperatorType.ToString,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000027 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000084, region_000085, region_000086],
    value=CustomType("CompareResult"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000028 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000087, region_000088, region_000089],
    value=CustomType("ThisType"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000029 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000090, None, region_000091],  # type: ignore
    type=statement_000028,
    is_variadic=None,
    name="this",
    default_value=None,
)

statement_000030 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000092, region_000093, region_000094],
    value=CustomType("ThisType"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000031 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000095, None, region_000096],  # type: ignore
    type=statement_000030,
    is_variadic=None,
    name="that",
    default_value=None,
)

statement_000032 = FuncParametersParserInfo.Create(
    regions=[region_000097, None, region_000098, None],
    positional=None,
    any_args=[statement_000029, statement_000031, ],
    keyword=None,
)

statement_000033 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000099, region_000097, region_000100, None, region_000101, region_000102, None, None, None, region_000103, None, None, None, None, region_000104],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000032,
    visibility_param=VisibilityModifier.public,
    mutability_param=None,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000027,
    name=FuncDefinitionStatementParserInfoOperatorType.Compare,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=True,
)

statement_000034 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000105, region_000106, region_000107],
    value=BooleanType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000035 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000108, region_000109, region_000110],
    value=NoneType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000036 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000111, None, region_000112],  # type: ignore
    type=statement_000035,
    is_variadic=None,
    name="that",
    default_value=None,
)

statement_000037 = FuncParametersParserInfo.Create(
    regions=[region_000113, None, region_000111, None],
    positional=None,
    any_args=[statement_000036, ],
    keyword=None,
)

statement_000038 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000114, region_000113, region_000115, region_000116, region_000117, region_000118, None, None, None, region_000119, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000037,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000034,
    name=FuncDefinitionStatementParserInfoOperatorType.Equal,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000039 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000120, region_000121, region_000122],
    value=BooleanType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.val,
)

statement_000040 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000123, region_000124, region_000125],
    value=NoneType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000041 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000126, None, region_000127],  # type: ignore
    type=statement_000040,
    is_variadic=None,
    name="that",
    default_value=None,
)

statement_000042 = FuncParametersParserInfo.Create(
    regions=[region_000128, None, region_000126, None],
    positional=None,
    any_args=[statement_000041, ],
    keyword=None,
)

statement_000043 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000129, region_000128, region_000130, region_000131, region_000132, region_000133, None, None, None, region_000134, None, None, None, None, None],
    parent_class_capabilities=StandardCapabilities,
    parameters=statement_000042,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.immutable,
    method_modifier_param=MethodModifier.override,
    return_type=statement_000039,
    name=FuncDefinitionStatementParserInfoOperatorType.NotEqual,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=True,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000044 = ClassStatementParserInfo.Create(
    regions=[region_000135, region_000136, region_000137, region_000138, None, None, None, None, region_000139, region_000135, None, None],
    class_capabilities=StandardCapabilities,
    visibility_param=VisibilityModifier.public,
    class_modifier_param=ClassModifier.immutable,
    name="None",
    documentation=None,
    templates=None,
    constraints=None,
    extends=None,
    implements=None,
    uses=None,
    statements=[statement_000001, statement_000008, statement_000014, statement_000020, statement_000022, statement_000024, statement_000026, statement_000033, statement_000038, statement_000043, ],
    constructor_visibility_param=VisibilityModifier.public,
    is_abstract=None,
    is_final=None,
)
