# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.MiniLanguage.Types.CustomType import CustomType
from v1.Parser.MiniLanguage.Types.NumberType import NumberType
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentParserInfo
from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo
from v1.Parser.ParserInfos.Common.MethodModifier import MethodModifier
from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo
from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo
from v1.Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier
from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
from v1.Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
from v1.Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
from v1.Parser.ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo
from v1.Parser.ParserInfos.ParserInfo import ParserInfoType
from v1.Parser.ParserInfos.Statements.ClassCapabilities.ConceptCapabilities import ConceptCapabilities
from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementDependencyParserInfo
from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionStatementParserInfoOperatorType
from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementItemParserInfo
from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType as ImportStatementParserInfoImportType
from v1.Parser.Region import Region


# ----------------------------------------------------------------------
region_000000 = Region(begin=Location(line=16, column=18), end=Location(line=16, column=21))
region_000001 = Region(begin=Location(line=16, column=1), end=Location(line=18, column=1))
region_000002 = Region(begin=Location(line=16, column=6), end=Location(line=16, column=10))
region_000003 = Region(begin=Location(line=22, column=6), end=Location(line=22, column=9))
region_000004 = Region(begin=Location(line=22, column=12), end=Location(line=22, column=16))
region_000005 = Region(begin=Location(line=22, column=5), end=Location(line=22, column=17))
region_000006 = Region(begin=Location(line=22, column=31), end=Location(line=22, column=35))
region_000007 = Region(begin=Location(line=22, column=5), end=Location(line=22, column=35))
region_000008 = Region(begin=Location(line=22, column=18), end=Location(line=22, column=28))
region_000009 = Region(begin=Location(line=23, column=6), end=Location(line=23, column=9))
region_000010 = Region(begin=Location(line=23, column=12), end=Location(line=23, column=16))
region_000011 = Region(begin=Location(line=23, column=5), end=Location(line=23, column=17))
region_000012 = Region(begin=Location(line=23, column=31), end=Location(line=23, column=35))
region_000013 = Region(begin=Location(line=23, column=5), end=Location(line=23, column=35))
region_000014 = Region(begin=Location(line=23, column=18), end=Location(line=23, column=28))
region_000015 = Region(begin=Location(line=21, column=35), end=Location(line=24, column=2))
region_000016 = Region(begin=Location(line=22, column=5), end=Location(line=23, column=36))
region_000017 = Region(begin=Location(line=25, column=19), end=Location(line=25, column=29))
region_000018 = Region(begin=Location(line=25, column=31), end=Location(line=25, column=41))
region_000019 = Region(begin=Location(line=25, column=17), end=Location(line=25, column=43))
region_000020 = Region(begin=Location(line=25, column=13), end=Location(line=25, column=43))
region_000021 = Region(begin=Location(line=25, column=13), end=Location(line=25, column=16))
region_000022 = Region(begin=Location(line=27, column=32), end=Location(line=27, column=40))
region_000023 = Region(begin=Location(line=27, column=31), end=Location(line=27, column=41))
region_000024 = Region(begin=Location(line=27, column=42), end=Location(line=27, column=54))
region_000025 = Region(begin=Location(line=27, column=42), end=Location(line=27, column=50))
region_000026 = Region(begin=Location(line=27, column=51), end=Location(line=27, column=54))
region_000027 = Region(begin=Location(line=27, column=42), end=Location(line=27, column=62))
region_000028 = Region(begin=Location(line=27, column=55), end=Location(line=27, column=62))
region_000029 = Region(begin=Location(line=27, column=41), end=Location(line=27, column=63))
region_000030 = Region(begin=Location(line=27, column=5), end=Location(line=28, column=1))
region_000031 = Region(begin=Location(line=27, column=5), end=Location(line=27, column=11))
region_000032 = Region(begin=Location(line=27, column=64), end=Location(line=27, column=67))
region_000033 = Region(begin=Location(line=27, column=17), end=Location(line=27, column=31))
region_000034 = Region(begin=Location(line=28, column=29), end=Location(line=28, column=37))
region_000035 = Region(begin=Location(line=28, column=28), end=Location(line=28, column=38))
region_000036 = Region(begin=Location(line=28, column=39), end=Location(line=28, column=51))
region_000037 = Region(begin=Location(line=28, column=39), end=Location(line=28, column=47))
region_000038 = Region(begin=Location(line=28, column=48), end=Location(line=28, column=51))
region_000039 = Region(begin=Location(line=28, column=39), end=Location(line=28, column=59))
region_000040 = Region(begin=Location(line=28, column=52), end=Location(line=28, column=59))
region_000041 = Region(begin=Location(line=28, column=38), end=Location(line=28, column=60))
region_000042 = Region(begin=Location(line=28, column=5), end=Location(line=30, column=1))
region_000043 = Region(begin=Location(line=28, column=5), end=Location(line=28, column=11))
region_000044 = Region(begin=Location(line=28, column=61), end=Location(line=28, column=64))
region_000045 = Region(begin=Location(line=28, column=17), end=Location(line=28, column=28))
region_000046 = Region(begin=Location(line=30, column=36), end=Location(line=30, column=49))
region_000047 = Region(begin=Location(line=30, column=36), end=Location(line=30, column=39))
region_000048 = Region(begin=Location(line=30, column=40), end=Location(line=30, column=49))
region_000049 = Region(begin=Location(line=30, column=36), end=Location(line=30, column=57))
region_000050 = Region(begin=Location(line=30, column=50), end=Location(line=30, column=57))
region_000051 = Region(begin=Location(line=30, column=35), end=Location(line=30, column=58))
region_000052 = Region(begin=Location(line=30, column=5), end=Location(line=31, column=1))
region_000053 = Region(begin=Location(line=30, column=5), end=Location(line=30, column=11))
region_000054 = Region(begin=Location(line=30, column=59), end=Location(line=30, column=62))
region_000055 = Region(begin=Location(line=30, column=17), end=Location(line=30, column=35))
region_000056 = Region(begin=Location(line=31, column=38), end=Location(line=31, column=51))
region_000057 = Region(begin=Location(line=31, column=38), end=Location(line=31, column=41))
region_000058 = Region(begin=Location(line=31, column=42), end=Location(line=31, column=51))
region_000059 = Region(begin=Location(line=31, column=38), end=Location(line=31, column=62))
region_000060 = Region(begin=Location(line=31, column=52), end=Location(line=31, column=62))
region_000061 = Region(begin=Location(line=31, column=37), end=Location(line=31, column=63))
region_000062 = Region(begin=Location(line=31, column=5), end=Location(line=32, column=1))
region_000063 = Region(begin=Location(line=31, column=5), end=Location(line=31, column=11))
region_000064 = Region(begin=Location(line=31, column=64), end=Location(line=31, column=67))
region_000065 = Region(begin=Location(line=31, column=17), end=Location(line=31, column=37))
region_000066 = Region(begin=Location(line=32, column=35), end=Location(line=32, column=48))
region_000067 = Region(begin=Location(line=32, column=35), end=Location(line=32, column=38))
region_000068 = Region(begin=Location(line=32, column=39), end=Location(line=32, column=48))
region_000069 = Region(begin=Location(line=32, column=35), end=Location(line=32, column=57))
region_000070 = Region(begin=Location(line=32, column=49), end=Location(line=32, column=57))
region_000071 = Region(begin=Location(line=32, column=34), end=Location(line=32, column=58))
region_000072 = Region(begin=Location(line=32, column=5), end=Location(line=34, column=1))
region_000073 = Region(begin=Location(line=32, column=5), end=Location(line=32, column=11))
region_000074 = Region(begin=Location(line=32, column=59), end=Location(line=32, column=62))
region_000075 = Region(begin=Location(line=32, column=17), end=Location(line=32, column=34))
region_000076 = Region(begin=Location(line=34, column=33), end=Location(line=34, column=46))
region_000077 = Region(begin=Location(line=34, column=33), end=Location(line=34, column=36))
region_000078 = Region(begin=Location(line=34, column=37), end=Location(line=34, column=46))
region_000079 = Region(begin=Location(line=34, column=33), end=Location(line=34, column=52))
region_000080 = Region(begin=Location(line=34, column=47), end=Location(line=34, column=52))
region_000081 = Region(begin=Location(line=34, column=32), end=Location(line=34, column=53))
region_000082 = Region(begin=Location(line=34, column=5), end=Location(line=35, column=1))
region_000083 = Region(begin=Location(line=34, column=5), end=Location(line=34, column=11))
region_000084 = Region(begin=Location(line=34, column=54), end=Location(line=34, column=57))
region_000085 = Region(begin=Location(line=34, column=17), end=Location(line=34, column=32))
region_000086 = Region(begin=Location(line=35, column=38), end=Location(line=35, column=51))
region_000087 = Region(begin=Location(line=35, column=38), end=Location(line=35, column=41))
region_000088 = Region(begin=Location(line=35, column=42), end=Location(line=35, column=51))
region_000089 = Region(begin=Location(line=35, column=38), end=Location(line=35, column=57))
region_000090 = Region(begin=Location(line=35, column=52), end=Location(line=35, column=57))
region_000091 = Region(begin=Location(line=35, column=37), end=Location(line=35, column=58))
region_000092 = Region(begin=Location(line=35, column=5), end=Location(line=36, column=1))
region_000093 = Region(begin=Location(line=35, column=5), end=Location(line=35, column=11))
region_000094 = Region(begin=Location(line=35, column=59), end=Location(line=35, column=62))
region_000095 = Region(begin=Location(line=35, column=17), end=Location(line=35, column=37))
region_000096 = Region(begin=Location(line=21, column=1), end=Location(line=36, column=1))
region_000097 = Region(begin=Location(line=21, column=1), end=Location(line=21, column=7))
region_000098 = Region(begin=Location(line=21, column=8), end=Location(line=21, column=15))
region_000099 = Region(begin=Location(line=21, column=24), end=Location(line=21, column=34))
region_000100 = Region(begin=Location(line=26, column=1), end=Location(line=36, column=1))


# ----------------------------------------------------------------------
statement_000000 = ImportStatementItemParserInfo.Create(
    regions=[region_000000, region_000000, None],
    name="Num",
    alias=None,
)

statement_000001 = ImportStatementParserInfo.Create(
    regions=[region_000001, region_000001, region_000002],
    visibility_param=VisibilityModifier.private,
    source_filename=".Num",
    import_items=[statement_000000, ],
    import_type=ImportStatementParserInfoImportType.source_is_module,
)

statement_000002 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000003, region_000003, None],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=None,
)

statement_000003 = NoneExpressionParserInfo.Create(
    regions=[region_000004],
)

statement_000004 = VariantExpressionParserInfo.Create(
    regions=[region_000005, None],
    types=[statement_000002, statement_000003, ],
    mutability_modifier=None,
)

statement_000005 = NoneExpressionParserInfo.Create(
    regions=[region_000006],
)

statement_000006 = ConstraintParameterParserInfo.Create(
    regions=[region_000007, region_000008],
    type=statement_000004,
    name="min_value!",
    default_value=statement_000005,
)

statement_000007 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000009, region_000009, None],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=None,
)

statement_000008 = NoneExpressionParserInfo.Create(
    regions=[region_000010],
)

statement_000009 = VariantExpressionParserInfo.Create(
    regions=[region_000011, None],
    types=[statement_000007, statement_000008, ],
    mutability_modifier=None,
)

statement_000010 = NoneExpressionParserInfo.Create(
    regions=[region_000012],
)

statement_000011 = ConstraintParameterParserInfo.Create(
    regions=[region_000013, region_000014],
    type=statement_000009,
    name="max_value!",
    default_value=statement_000010,
)

statement_000012 = ConstraintParametersParserInfo.Create(
    regions=[region_000015, None, region_000016, None],
    positional=None,
    any=[statement_000006, statement_000011, ],
    keyword=None,
)

statement_000013 = VariableExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[region_000017, region_000017],
    name="min_value!",
)

statement_000013 = ConstraintArgumentParserInfo.Create(
    regions=[region_000017, None],
    expression=statement_000013,
    keyword=None,
)

statement_000014 = VariableExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[region_000018, region_000018],
    name="max_value!",
)

statement_000014 = ConstraintArgumentParserInfo.Create(
    regions=[region_000018, None],
    expression=statement_000014,
    keyword=None,
)

statement_000015 = ConstraintArgumentsParserInfo.Create(
    regions=[region_000019, region_000019],
    arguments=[statement_000013, statement_000014, ],
)

statement_000016 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000020, region_000021, None],
    value=NumberType(),
    templates=None,
    constraints=statement_000015,
    mutability_modifier=None,
)

statement_000016 = ClassStatementDependencyParserInfo.Create(
    regions=[region_000020, region_000020],
    visibility=VisibilityModifier.public,
    type=statement_000016,
)

statement_000017 = TemplateTypeParameterParserInfo.Create(
    regions=[region_000022, region_000022, None],
    name="ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000018 = TemplateParametersParserInfo.Create(
    regions=[region_000023, None, region_000022, None],
    positional=None,
    any=[statement_000017, ],
    keyword=None,
)

statement_000019 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000024, region_000025, region_000026],
    value=CustomType("ArchiveT"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000020 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000027, None, region_000028],  # type: ignore
    type=statement_000019,
    is_variadic=None,
    name="archive",
    default_value=None,
)

statement_000021 = FuncParametersParserInfo.Create(
    regions=[region_000029, None, region_000027, None],
    positional=None,
    any_args=[statement_000020, ],
    keyword=None,
)

statement_000022 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000030, region_000029, region_000031, region_000032, region_000030, region_000033, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000021,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.Serialize,
    documentation=None,
    templates=statement_000018,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000023 = TemplateTypeParameterParserInfo.Create(
    regions=[region_000034, region_000034, None],
    name="VisitorT",
    is_variadic=None,
    default_type=None,
)

statement_000024 = TemplateParametersParserInfo.Create(
    regions=[region_000035, None, region_000034, None],
    positional=None,
    any=[statement_000023, ],
    keyword=None,
)

statement_000025 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[region_000036, region_000037, region_000038],
    value=CustomType("VisitorT"),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000026 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000039, None, region_000040],  # type: ignore
    type=statement_000025,
    is_variadic=None,
    name="visitor",
    default_value=None,
)

statement_000027 = FuncParametersParserInfo.Create(
    regions=[region_000041, None, region_000039, None],
    positional=None,
    any_args=[statement_000026, ],
    keyword=None,
)

statement_000028 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000042, region_000041, region_000043, region_000044, region_000042, region_000045, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000027,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.Accept,
    documentation=None,
    templates=statement_000024,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000029 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000046, region_000047, region_000048],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000030 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000049, None, region_000050],  # type: ignore
    type=statement_000029,
    is_variadic=None,
    name="divisor",
    default_value=None,
)

statement_000031 = FuncParametersParserInfo.Create(
    regions=[region_000051, None, region_000049, None],
    positional=None,
    any_args=[statement_000030, ],
    keyword=None,
)

statement_000032 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000052, region_000051, region_000053, region_000054, region_000052, region_000055, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000031,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.DivideInplace,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000033 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000056, region_000057, region_000058],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000034 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000059, None, region_000060],  # type: ignore
    type=statement_000033,
    is_variadic=None,
    name="multiplier",
    default_value=None,
)

statement_000035 = FuncParametersParserInfo.Create(
    regions=[region_000061, None, region_000059, None],
    positional=None,
    any_args=[statement_000034, ],
    keyword=None,
)

statement_000036 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000062, region_000061, region_000063, region_000064, region_000062, region_000065, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000035,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.MultiplyInplace,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000037 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000066, region_000067, region_000068],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000038 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000069, None, region_000070],  # type: ignore
    type=statement_000037,
    is_variadic=None,
    name="exponent",
    default_value=None,
)

statement_000039 = FuncParametersParserInfo.Create(
    regions=[region_000071, None, region_000069, None],
    positional=None,
    any_args=[statement_000038, ],
    keyword=None,
)

statement_000040 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000072, region_000071, region_000073, region_000074, region_000072, region_000075, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000039,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.PowerInplace,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000041 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000076, region_000077, region_000078],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000042 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000079, None, region_000080],  # type: ignore
    type=statement_000041,
    is_variadic=None,
    name="value",
    default_value=None,
)

statement_000043 = FuncParametersParserInfo.Create(
    regions=[region_000081, None, region_000079, None],
    positional=None,
    any_args=[statement_000042, ],
    keyword=None,
)

statement_000044 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000082, region_000081, region_000083, region_000084, region_000082, region_000085, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000043,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.AddInplace,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000045 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Configuration,
    regions=[region_000086, region_000087, region_000088],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000046 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000089, None, region_000090],  # type: ignore
    type=statement_000045,
    is_variadic=None,
    name="value",
    default_value=None,
)

statement_000047 = FuncParametersParserInfo.Create(
    regions=[region_000091, None, region_000089, None],
    positional=None,
    any_args=[statement_000046, ],
    keyword=None,
)

statement_000048 = FuncDefinitionStatementParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[region_000092, region_000091, region_000093, region_000094, region_000092, region_000095, None, None, None, None, None, None, None, None, None],
    parent_class_capabilities=ConceptCapabilities,
    parameters=statement_000047,
    visibility_param=VisibilityModifier.public,
    mutability_param=MutabilityModifier.var,
    method_modifier_param=MethodModifier.abstract,
    return_type=None,
    name=FuncDefinitionStatementParserInfoOperatorType.SubtractInplace,
    documentation=None,
    templates=None,
    captured_variables=None,
    statements=None,
    is_deferred=None,
    is_exceptional=None,
    is_generator=None,
    is_reentrant=None,
    is_scoped=None,
    is_static=None,
)

statement_000049 = ClassStatementParserInfo.Create(
    regions=[region_000096, region_000097, region_000098, region_000099, None, region_000020, None, None, region_000100, region_000096, None, None],
    class_capabilities=ConceptCapabilities,
    visibility_param=VisibilityModifier.public,
    class_modifier_param=ClassModifier.mutable,
    name="MutableNum",
    documentation=None,
    templates=None,
    constraints=statement_000012,
    extends=[statement_000016, ],
    implements=None,
    uses=None,
    statements=[statement_000022, statement_000028, statement_000032, statement_000036, statement_000040, statement_000044, statement_000048, ],
    constructor_visibility_param=VisibilityModifier.public,
    is_abstract=None,
    is_final=None,
)
