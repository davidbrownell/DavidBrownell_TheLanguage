# ----------------------------------------------------------------------
# This code was automatically generated by the PythonTarget. Any changes made to this
# file will be overwritten during the next generation!
# ----------------------------------------------------------------------

from v1.Lexer.Location import Location
from v1.Parser.MiniLanguage.Types.NumberType import NumberType
from v1.Parser.ParserInfos.AggregateParserInfo import AggregateParserInfo
from v1.Parser.ParserInfos.Common.ClassModifier import ClassModifier
from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentParserInfo
from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo
from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo
from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo
from v1.Parser.ParserInfos.Common.FunctionModifier import FunctionModifier
from v1.Parser.ParserInfos.Common.MethodHierarchyModifier import MethodHierarchyModifier
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
from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType as ImportStatementParserInfoImportType
from v1.Parser.ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
from v1.Parser.TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
tu_region_000000 = TranslationUnitRegion(begin=Location(line=16, column=1), end=Location(line=18, column=1))
tu_region_000001 = TranslationUnitRegion(begin=Location(line=16, column=18), end=Location(line=16, column=21))
tu_region_000002 = TranslationUnitRegion(begin=Location(line=16, column=6), end=Location(line=16, column=10))
tu_region_000003 = TranslationUnitRegion(begin=Location(line=22, column=6), end=Location(line=22, column=10))
tu_region_000004 = TranslationUnitRegion(begin=Location(line=22, column=13), end=Location(line=22, column=18))
tu_region_000005 = TranslationUnitRegion(begin=Location(line=22, column=5), end=Location(line=22, column=19))
tu_region_000006 = TranslationUnitRegion(begin=Location(line=22, column=33), end=Location(line=22, column=38))
tu_region_000007 = TranslationUnitRegion(begin=Location(line=22, column=5), end=Location(line=22, column=38))
tu_region_000008 = TranslationUnitRegion(begin=Location(line=22, column=20), end=Location(line=22, column=30))
tu_region_000009 = TranslationUnitRegion(begin=Location(line=23, column=6), end=Location(line=23, column=10))
tu_region_000010 = TranslationUnitRegion(begin=Location(line=23, column=13), end=Location(line=23, column=18))
tu_region_000011 = TranslationUnitRegion(begin=Location(line=23, column=5), end=Location(line=23, column=19))
tu_region_000012 = TranslationUnitRegion(begin=Location(line=23, column=33), end=Location(line=23, column=38))
tu_region_000013 = TranslationUnitRegion(begin=Location(line=23, column=5), end=Location(line=23, column=38))
tu_region_000014 = TranslationUnitRegion(begin=Location(line=23, column=20), end=Location(line=23, column=30))
tu_region_000015 = TranslationUnitRegion(begin=Location(line=21, column=35), end=Location(line=24, column=2))
tu_region_000016 = TranslationUnitRegion(begin=Location(line=22, column=5), end=Location(line=23, column=39))
tu_region_000017 = TranslationUnitRegion(begin=Location(line=25, column=19), end=Location(line=25, column=29))
tu_region_000018 = TranslationUnitRegion(begin=Location(line=25, column=31), end=Location(line=25, column=41))
tu_region_000019 = TranslationUnitRegion(begin=Location(line=25, column=17), end=Location(line=25, column=43))
tu_region_000020 = TranslationUnitRegion(begin=Location(line=25, column=13), end=Location(line=25, column=43))
tu_region_000021 = TranslationUnitRegion(begin=Location(line=25, column=13), end=Location(line=25, column=16))
tu_region_000022 = TranslationUnitRegion(begin=Location(line=27, column=41), end=Location(line=27, column=49))
tu_region_000023 = TranslationUnitRegion(begin=Location(line=27, column=31), end=Location(line=27, column=59))
tu_region_000024 = TranslationUnitRegion(begin=Location(line=27, column=60), end=Location(line=27, column=72))
tu_region_000025 = TranslationUnitRegion(begin=Location(line=27, column=60), end=Location(line=27, column=68))
tu_region_000026 = TranslationUnitRegion(begin=Location(line=27, column=69), end=Location(line=27, column=72))
tu_region_000027 = TranslationUnitRegion(begin=Location(line=27, column=60), end=Location(line=27, column=80))
tu_region_000028 = TranslationUnitRegion(begin=Location(line=27, column=73), end=Location(line=27, column=80))
tu_region_000029 = TranslationUnitRegion(begin=Location(line=27, column=59), end=Location(line=27, column=81))
tu_region_000030 = TranslationUnitRegion(begin=Location(line=27, column=5), end=Location(line=28, column=1))
tu_region_000031 = TranslationUnitRegion(begin=Location(line=27, column=5), end=Location(line=27, column=11))
tu_region_000032 = TranslationUnitRegion(begin=Location(line=27, column=82), end=Location(line=27, column=85))
tu_region_000033 = TranslationUnitRegion(begin=Location(line=27, column=17), end=Location(line=27, column=31))
tu_region_000034 = TranslationUnitRegion(begin=Location(line=28, column=38), end=Location(line=28, column=46))
tu_region_000035 = TranslationUnitRegion(begin=Location(line=28, column=28), end=Location(line=28, column=56))
tu_region_000036 = TranslationUnitRegion(begin=Location(line=28, column=57), end=Location(line=28, column=69))
tu_region_000037 = TranslationUnitRegion(begin=Location(line=28, column=57), end=Location(line=28, column=65))
tu_region_000038 = TranslationUnitRegion(begin=Location(line=28, column=66), end=Location(line=28, column=69))
tu_region_000039 = TranslationUnitRegion(begin=Location(line=28, column=57), end=Location(line=28, column=77))
tu_region_000040 = TranslationUnitRegion(begin=Location(line=28, column=70), end=Location(line=28, column=77))
tu_region_000041 = TranslationUnitRegion(begin=Location(line=28, column=56), end=Location(line=28, column=78))
tu_region_000042 = TranslationUnitRegion(begin=Location(line=28, column=5), end=Location(line=30, column=1))
tu_region_000043 = TranslationUnitRegion(begin=Location(line=28, column=5), end=Location(line=28, column=11))
tu_region_000044 = TranslationUnitRegion(begin=Location(line=28, column=79), end=Location(line=28, column=82))
tu_region_000045 = TranslationUnitRegion(begin=Location(line=28, column=17), end=Location(line=28, column=28))
tu_region_000046 = TranslationUnitRegion(begin=Location(line=30, column=36), end=Location(line=30, column=49))
tu_region_000047 = TranslationUnitRegion(begin=Location(line=30, column=36), end=Location(line=30, column=39))
tu_region_000048 = TranslationUnitRegion(begin=Location(line=30, column=40), end=Location(line=30, column=49))
tu_region_000049 = TranslationUnitRegion(begin=Location(line=30, column=36), end=Location(line=30, column=57))
tu_region_000050 = TranslationUnitRegion(begin=Location(line=30, column=50), end=Location(line=30, column=57))
tu_region_000051 = TranslationUnitRegion(begin=Location(line=30, column=35), end=Location(line=30, column=58))
tu_region_000052 = TranslationUnitRegion(begin=Location(line=30, column=5), end=Location(line=31, column=1))
tu_region_000053 = TranslationUnitRegion(begin=Location(line=30, column=5), end=Location(line=30, column=11))
tu_region_000054 = TranslationUnitRegion(begin=Location(line=30, column=59), end=Location(line=30, column=62))
tu_region_000055 = TranslationUnitRegion(begin=Location(line=30, column=17), end=Location(line=30, column=35))
tu_region_000056 = TranslationUnitRegion(begin=Location(line=31, column=38), end=Location(line=31, column=51))
tu_region_000057 = TranslationUnitRegion(begin=Location(line=31, column=38), end=Location(line=31, column=41))
tu_region_000058 = TranslationUnitRegion(begin=Location(line=31, column=42), end=Location(line=31, column=51))
tu_region_000059 = TranslationUnitRegion(begin=Location(line=31, column=38), end=Location(line=31, column=62))
tu_region_000060 = TranslationUnitRegion(begin=Location(line=31, column=52), end=Location(line=31, column=62))
tu_region_000061 = TranslationUnitRegion(begin=Location(line=31, column=37), end=Location(line=31, column=63))
tu_region_000062 = TranslationUnitRegion(begin=Location(line=31, column=5), end=Location(line=32, column=1))
tu_region_000063 = TranslationUnitRegion(begin=Location(line=31, column=5), end=Location(line=31, column=11))
tu_region_000064 = TranslationUnitRegion(begin=Location(line=31, column=64), end=Location(line=31, column=67))
tu_region_000065 = TranslationUnitRegion(begin=Location(line=31, column=17), end=Location(line=31, column=37))
tu_region_000066 = TranslationUnitRegion(begin=Location(line=32, column=35), end=Location(line=32, column=48))
tu_region_000067 = TranslationUnitRegion(begin=Location(line=32, column=35), end=Location(line=32, column=38))
tu_region_000068 = TranslationUnitRegion(begin=Location(line=32, column=39), end=Location(line=32, column=48))
tu_region_000069 = TranslationUnitRegion(begin=Location(line=32, column=35), end=Location(line=32, column=57))
tu_region_000070 = TranslationUnitRegion(begin=Location(line=32, column=49), end=Location(line=32, column=57))
tu_region_000071 = TranslationUnitRegion(begin=Location(line=32, column=34), end=Location(line=32, column=58))
tu_region_000072 = TranslationUnitRegion(begin=Location(line=32, column=5), end=Location(line=34, column=1))
tu_region_000073 = TranslationUnitRegion(begin=Location(line=32, column=5), end=Location(line=32, column=11))
tu_region_000074 = TranslationUnitRegion(begin=Location(line=32, column=59), end=Location(line=32, column=62))
tu_region_000075 = TranslationUnitRegion(begin=Location(line=32, column=17), end=Location(line=32, column=34))
tu_region_000076 = TranslationUnitRegion(begin=Location(line=34, column=33), end=Location(line=34, column=46))
tu_region_000077 = TranslationUnitRegion(begin=Location(line=34, column=33), end=Location(line=34, column=36))
tu_region_000078 = TranslationUnitRegion(begin=Location(line=34, column=37), end=Location(line=34, column=46))
tu_region_000079 = TranslationUnitRegion(begin=Location(line=34, column=33), end=Location(line=34, column=52))
tu_region_000080 = TranslationUnitRegion(begin=Location(line=34, column=47), end=Location(line=34, column=52))
tu_region_000081 = TranslationUnitRegion(begin=Location(line=34, column=32), end=Location(line=34, column=53))
tu_region_000082 = TranslationUnitRegion(begin=Location(line=34, column=5), end=Location(line=35, column=1))
tu_region_000083 = TranslationUnitRegion(begin=Location(line=34, column=5), end=Location(line=34, column=11))
tu_region_000084 = TranslationUnitRegion(begin=Location(line=34, column=54), end=Location(line=34, column=57))
tu_region_000085 = TranslationUnitRegion(begin=Location(line=34, column=17), end=Location(line=34, column=32))
tu_region_000086 = TranslationUnitRegion(begin=Location(line=35, column=38), end=Location(line=35, column=51))
tu_region_000087 = TranslationUnitRegion(begin=Location(line=35, column=38), end=Location(line=35, column=41))
tu_region_000088 = TranslationUnitRegion(begin=Location(line=35, column=42), end=Location(line=35, column=51))
tu_region_000089 = TranslationUnitRegion(begin=Location(line=35, column=38), end=Location(line=35, column=57))
tu_region_000090 = TranslationUnitRegion(begin=Location(line=35, column=52), end=Location(line=35, column=57))
tu_region_000091 = TranslationUnitRegion(begin=Location(line=35, column=37), end=Location(line=35, column=58))
tu_region_000092 = TranslationUnitRegion(begin=Location(line=35, column=5), end=Location(line=36, column=1))
tu_region_000093 = TranslationUnitRegion(begin=Location(line=35, column=5), end=Location(line=35, column=11))
tu_region_000094 = TranslationUnitRegion(begin=Location(line=35, column=59), end=Location(line=35, column=62))
tu_region_000095 = TranslationUnitRegion(begin=Location(line=35, column=17), end=Location(line=35, column=37))
tu_region_000096 = TranslationUnitRegion(begin=Location(line=21, column=1), end=Location(line=36, column=1))
tu_region_000097 = TranslationUnitRegion(begin=Location(line=21, column=1), end=Location(line=21, column=7))
tu_region_000098 = TranslationUnitRegion(begin=Location(line=21, column=8), end=Location(line=21, column=15))
tu_region_000099 = TranslationUnitRegion(begin=Location(line=21, column=24), end=Location(line=21, column=34))
tu_region_000100 = TranslationUnitRegion(begin=Location(line=26, column=1), end=Location(line=36, column=1))
tu_region_000101 = TranslationUnitRegion(begin=Location(line=1, column=1), end=Location(line=36, column=1))


# ----------------------------------------------------------------------
statement_000000 = ImportStatementParserInfo.Create(
    regions=[tu_region_000000, tu_region_000001, tu_region_000000, tu_region_000002, tu_region_000001],
    name=r"Num",
    visibility_param=VisibilityModifier.private,
    source_parts=['Num'],
    importing_name=r"Num",
    import_type=ImportStatementParserInfoImportType.source_is_module,
)

statement_000001 = AggregateParserInfo(
    parser_infos=[statement_000000, ],
)

statement_000002 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000003, tu_region_000003, None],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=None,
)

statement_000003 = NoneExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000004],
)

statement_000004 = VariantExpressionParserInfo.Create(
    regions=[tu_region_000005, None],
    types=[statement_000002, statement_000003, ],
    mutability_modifier=None,
)

statement_000005 = NoneExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000006],
)

statement_000006 = ConstraintParameterParserInfo.Create(
    regions=[tu_region_000007, tu_region_000008],
    type=statement_000004,
    name=r"min_value!",
    default_value=statement_000005,
)

statement_000007 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000009, tu_region_000009, None],
    value=NumberType(),
    templates=None,
    constraints=None,
    mutability_modifier=None,
)

statement_000008 = NoneExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000010],
)

statement_000009 = VariantExpressionParserInfo.Create(
    regions=[tu_region_000011, None],
    types=[statement_000007, statement_000008, ],
    mutability_modifier=None,
)

statement_000010 = NoneExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000012],
)

statement_000011 = ConstraintParameterParserInfo.Create(
    regions=[tu_region_000013, tu_region_000014],
    type=statement_000009,
    name=r"max_value!",
    default_value=statement_000010,
)

statement_000012 = ConstraintParametersParserInfo.Create(
    regions=[tu_region_000015, None, tu_region_000016, None],
    positional=None,
    any=[statement_000006, statement_000011, ],
    keyword=None,
)

statement_000013 = VariableExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000017, tu_region_000017],
    name=r"min_value!",
)

statement_000014 = ConstraintArgumentParserInfo.Create(
    regions=[tu_region_000017, None],
    expression=statement_000013,
    keyword=None,
)

statement_000015 = VariableExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.TypeCustomization,
    regions=[tu_region_000018, tu_region_000018],
    name=r"max_value!",
)

statement_000016 = ConstraintArgumentParserInfo.Create(
    regions=[tu_region_000018, None],
    expression=statement_000015,
    keyword=None,
)

statement_000017 = ConstraintArgumentsParserInfo.Create(
    regions=[tu_region_000019, tu_region_000019],
    arguments=[statement_000014, statement_000016, ],
)

statement_000018 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000020, tu_region_000021, None],
    value="Num",
    templates=None,
    constraints=statement_000017,
    mutability_modifier=None,
)

statement_000019 = ClassStatementDependencyParserInfo.Create(
    regions=[tu_region_000020, tu_region_000020],
    visibility=VisibilityModifier.public,
    type=statement_000018,
)

statement_000020 = TemplateTypeParameterParserInfo.Create(
    regions=[tu_region_000022, tu_region_000022, None],
    name=r"ArchiveT",
    is_variadic=None,
    default_type=None,
)

statement_000021 = TemplateParametersParserInfo.Create(
    regions=[tu_region_000023, None, tu_region_000022, None],
    positional=None,
    any=[statement_000020, ],
    keyword=None,
)

statement_000022 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000024, tu_region_000025, tu_region_000026],
    value="ArchiveT",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000023 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000027, None, tu_region_000028],  # type: ignore
    type=statement_000022,
    is_variadic=None,
    name=r"archive",
    default_value=None,
)

statement_000024 = FuncParametersParserInfo.Create(
    regions=[tu_region_000029, None, tu_region_000027, None],
    positional=None,
    any=[statement_000023, ],
    keyword=None,
)

statement_000025 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000030, tu_region_000033, tu_region_000031, None, tu_region_000030, tu_region_000029, tu_region_000032, tu_region_000030, None, None, None, None, None],
    name=r"OperatorType.Serialize",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=statement_000021,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000024,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000026 = TemplateTypeParameterParserInfo.Create(
    regions=[tu_region_000034, tu_region_000034, None],
    name=r"VisitorT",
    is_variadic=None,
    default_type=None,
)

statement_000027 = TemplateParametersParserInfo.Create(
    regions=[tu_region_000035, None, tu_region_000034, None],
    positional=None,
    any=[statement_000026, ],
    keyword=None,
)

statement_000028 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000036, tu_region_000037, tu_region_000038],
    value="VisitorT",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.ref,
)

statement_000029 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000039, None, tu_region_000040],  # type: ignore
    type=statement_000028,
    is_variadic=None,
    name=r"visitor",
    default_value=None,
)

statement_000030 = FuncParametersParserInfo.Create(
    regions=[tu_region_000041, None, tu_region_000039, None],
    positional=None,
    any=[statement_000029, ],
    keyword=None,
)

statement_000031 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000042, tu_region_000045, tu_region_000043, None, tu_region_000042, tu_region_000041, tu_region_000044, tu_region_000042, None, None, None, None, None],
    name=r"OperatorType.Accept",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=statement_000027,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000030,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000032 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000046, tu_region_000047, tu_region_000048],
    value="Num",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000033 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000049, None, tu_region_000050],  # type: ignore
    type=statement_000032,
    is_variadic=None,
    name=r"divisor",
    default_value=None,
)

statement_000034 = FuncParametersParserInfo.Create(
    regions=[tu_region_000051, None, tu_region_000049, None],
    positional=None,
    any=[statement_000033, ],
    keyword=None,
)

statement_000035 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000052, tu_region_000055, tu_region_000053, None, tu_region_000052, tu_region_000051, tu_region_000054, tu_region_000052, None, None, None, None, None],
    name=r"OperatorType.DivideInplace",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000034,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000036 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000056, tu_region_000057, tu_region_000058],
    value="Num",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000037 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000059, None, tu_region_000060],  # type: ignore
    type=statement_000036,
    is_variadic=None,
    name=r"multiplier",
    default_value=None,
)

statement_000038 = FuncParametersParserInfo.Create(
    regions=[tu_region_000061, None, tu_region_000059, None],
    positional=None,
    any=[statement_000037, ],
    keyword=None,
)

statement_000039 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000062, tu_region_000065, tu_region_000063, None, tu_region_000062, tu_region_000061, tu_region_000064, tu_region_000062, None, None, None, None, None],
    name=r"OperatorType.MultiplyInplace",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000038,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000040 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000066, tu_region_000067, tu_region_000068],
    value="Num",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000041 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000069, None, tu_region_000070],  # type: ignore
    type=statement_000040,
    is_variadic=None,
    name=r"exponent",
    default_value=None,
)

statement_000042 = FuncParametersParserInfo.Create(
    regions=[tu_region_000071, None, tu_region_000069, None],
    positional=None,
    any=[statement_000041, ],
    keyword=None,
)

statement_000043 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000072, tu_region_000075, tu_region_000073, None, tu_region_000072, tu_region_000071, tu_region_000074, tu_region_000072, None, None, None, None, None],
    name=r"OperatorType.PowerInplace",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000042,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000044 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000076, tu_region_000077, tu_region_000078],
    value="Num",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000045 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000079, None, tu_region_000080],  # type: ignore
    type=statement_000044,
    is_variadic=None,
    name=r"value",
    default_value=None,
)

statement_000046 = FuncParametersParserInfo.Create(
    regions=[tu_region_000081, None, tu_region_000079, None],
    positional=None,
    any=[statement_000045, ],
    keyword=None,
)

statement_000047 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000082, tu_region_000085, tu_region_000083, None, tu_region_000082, tu_region_000081, tu_region_000084, tu_region_000082, None, None, None, None, None],
    name=r"OperatorType.AddInplace",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000046,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000048 = FuncOrTypeExpressionParserInfo.Create(
    parser_info_type=ParserInfoType.Unknown,
    regions=[tu_region_000086, tu_region_000087, tu_region_000088],
    value="Num",
    templates=None,
    constraints=None,
    mutability_modifier=MutabilityModifier.immutable,
)

statement_000049 = FuncParameterParserInfo.Create(
    parser_info_type=ParserInfoType.Standard,
    regions=[tu_region_000089, None, tu_region_000090],  # type: ignore
    type=statement_000048,
    is_variadic=None,
    name=r"value",
    default_value=None,
)

statement_000050 = FuncParametersParserInfo.Create(
    regions=[tu_region_000091, None, tu_region_000089, None],
    positional=None,
    any=[statement_000049, ],
    keyword=None,
)

statement_000051 = FuncDefinitionStatementParserInfo.Create(
    regions=[tu_region_000092, tu_region_000095, tu_region_000093, None, tu_region_000092, tu_region_000091, tu_region_000094, tu_region_000092, None, None, None, None, None],
    name=r"OperatorType.SubtractInplace",
    visibility_param=VisibilityModifier.public,
    statements=None,
    templates_param=None,
    parent_class_capabilities=ConceptCapabilities,
    function_modifier_param=FunctionModifier.standard,
    parameters=statement_000050,
    mutability_param=MutabilityModifier.var,
    method_hierarchy_modifier_param=MethodHierarchyModifier.abstract,
    return_type=None,
    documentation=None,
    captured_variables=None,
    is_deferred=None,
    is_exceptional=None,
    is_static=None,
)

statement_000052 = ClassStatementParserInfo.Create(
    regions=[tu_region_000096, tu_region_000097, tu_region_000100, tu_region_000098, tu_region_000099, None, tu_region_000020, None, None, tu_region_000096, None, None],
    name=r"MutableNum",
    visibility_param=VisibilityModifier.public,
    statements=[statement_000025, statement_000031, statement_000035, statement_000039, statement_000043, statement_000047, statement_000051, ],
    templates_param=None,
    parent_class_capabilities=None,
    class_capabilities=ConceptCapabilities,
    class_modifier_param=ClassModifier.mutable,
    documentation=None,
    constraints=statement_000012,
    extends=[statement_000019, ],
    implements=None,
    uses=None,
    constructor_visibility_param=VisibilityModifier.public,
    is_abstract=None,
    is_final=None,
)

root_parser_info = RootStatementParserInfo.Create(
    regions=[tu_region_000101, tu_region_000101, None],
    name=r"Concepts.MutableNum",
    statements=[statement_000001, statement_000052, ],
    documentation=None,
)
