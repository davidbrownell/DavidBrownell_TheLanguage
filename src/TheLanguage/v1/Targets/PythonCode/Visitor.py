# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-25 08:13:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

import os
import textwrap

from typing import cast

from io import StringIO
from typing import Dict, List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# TODO: Refine how enums are printed handled
# TODO: Return value when processing lists?
# TODO: Break into components

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Lexer.Location import Location

    from ...Parser.Parser import Region, RootParserInfo

    from ...Parser.ParserInfos.ParserInfo import ParserInfo, VisitControl

    from ...Parser.ParserInfos.Common.ClassModifier import ClassModifier
    from ...Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo, ConstraintArgumentParserInfo
    from ...Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ...Parser.ParserInfos.Common.MethodModifier import MethodModifier
    from ...Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier
    from ...Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo, FuncArgumentParserInfo
    from ...Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ...Parser.ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateDecoratorArgumentParserInfo, TemplateTypeArgumentParserInfo
    from ...Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateTypeParameterParserInfo, TemplateDecoratorParameterParserInfo
    from ...Parser.ParserInfos.Common.VariableNameParserInfo import VariableNameParserInfo
    from ...Parser.ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ...Parser.ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ...Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo

    from ...Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo
    from ...Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from ...Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
    from ...Parser.ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...Parser.ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ...Parser.ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...Parser.ParserInfos.Types.TypeParserInfo import TypeParserInfo
    from ...Parser.ParserInfos.Types.StandardTypeParserInfo import StandardTypeParserInfo, StandardTypeItemParserInfo
    from ...Parser.ParserInfos.Types.TupleTypeParserInfo import TupleTypeParserInfo
    from ...Parser.ParserInfos.Types.VariantTypeParserInfo import VariantTypeParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class Visitor(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self._stream                        = StringIO()

        self._imports                                   = set()
        self._statement_names: Dict[str, ParserInfo]    = {}

        self._imports.add("from v1.Lexer.Location import Location")
        self._imports.add("from v1.Parser.Region import Region")
        self._imports.add("from v1.Parser.ParserInfos.ParserInfo import ParserInfoType")

        for common_import in [
            "ClassModifier",
            "MethodModifier",
            "MutabilityModifier",
            "VisibilityModifier",
        ]:
            self._imports.add(
                "from v1.Parser.ParserInfos.Common.{common_import} import {common_import}".format(
                    common_import=common_import,
                ),
            )

        for capabilities in [
            "Concept",
            "Exception",
            "ImmutablePOD",
            "Interface",
            "Mixin",
            "MutablePOD",
            "Standard",
        ]:
            self._imports.add(
                "from v1.Parser.ParserInfos.Statements.ClassCapabilities.{name}Capabilities import {name}Capabilities".format(
                    name=capabilities,
                ),
            )

    # ----------------------------------------------------------------------
    def GetContent(self) -> str:
        return textwrap.dedent(
            """\
            # ----------------------------------------------------------------------
            # This code was automatically generated by the PythonTarget. Any changes made to this
            # file will be overwritten during the next generation!
            # ----------------------------------------------------------------------

            {imports}


            # ----------------------------------------------------------------------
            {content}
            """,
        ).format(
            imports="\n".join(sorted(self._imports)),
            content="\n".join(line.rstrip() for line in self._stream.getvalue().rstrip().splitlines()),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterScope(
        parser_info: ParserInfo,
    ) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @staticmethod
    def OnExitScope(
        parser_info: ParserInfo,
    ) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    def OnEnterRootParserInfo(
        self,
        parser_info: RootParserInfo,
    ) -> None:
        if parser_info.documentation is not None:
            self._stream.write(
                textwrap.dedent(
                    '''
                    """\\
                    {}
                    """

                    ''',
                ).format(parser_info.documentation),
            )

    # ----------------------------------------------------------------------
    def OnExitRootParserInfo(
        self,
        parser_info: RootParserInfo,
    ) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # |  ConstraintArgumentsParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterConstraintArgumentsParserInfo(
        parser_info: ConstraintArgumentsParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitConstraintArgumentsParserInfo(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ConstraintArgumentsParserInfo.Create(
                    regions=[{self_region}, {arguments_region}],
                    arguments={arguments},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                arguments=self._ToString(cast(List[ParserInfo], parser_info.arguments)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnConstraintArgumentsParserInfo_Arguments(
        self,
        parser_infos: List[ConstraintArgumentParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterConstraintArgumentParserInfo(
        parser_info: ConstraintArgumentParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitConstraintArgumentParserInfo(
        self,
        parser_info: ConstraintArgumentParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ConstraintArgumentParserInfo.Create(
                    regions=[{self_region}, {keyword_region}],
                    expression={expression},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                expression=self._ToString(parser_info.expression),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    def OnConstraintArgumentParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  ConstraintParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterConstraintParametersParserInfo(
        parser_info: ConstraintParametersParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitConstraintParametersParserInfo(
        self,
        parser_info: ConstraintParametersParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ConstraintParametersParserInfo.Create(
                    regions=[{self_region}, {positional_region}, {any_region}, {keyword_region}],
                    positional={positional},
                    any={any},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                positional_region=self._ToString(parser_info.regions__.positional),
                any_region=self._ToString(parser_info.regions__.any),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                positional=self._ToString(cast(Optional[List[ParserInfo]], parser_info.positional)),
                any=self._ToString(cast(Optional[List[ParserInfo]], parser_info.any)),
                keyword=self._ToString(cast(Optional[List[ParserInfo]], parser_info.keyword)),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnConstraintParametersParserInfo_Positional(
        self,
        parser_infos: List[ConstraintParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnConstraintParametersParserInfo_Any(
        self,
        parser_infos: List[ConstraintParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnConstraintParametersParserInfo_Keyword(
        self,
        parser_infos: List[ConstraintParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterConstraintParameterParserInfo(
        parser_info: ConstraintParameterParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParameterParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ConstraintParameterParserInfo.Create(
                    regions=[{self_region}, {name_region}],
                    type={type},
                    name={name},
                    default_value={default_value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                type=self._ToString(parser_info.type),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnConstraintParameterParserInfo_Type(
        self,
        parser_info: TypeParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnConstraintParameterParserInfo_DefaultValue(
        self,
        parser_info: ExpressionParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  FuncArgumentsParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterFuncArgumentsParserInfo(
        parser_info: FuncArgumentsParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitFuncArgumentsParserInfo(
        self,
        parser_info: FuncArgumentsParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncArgumentsParserInfo.Create(
                    regions=[{self_region}, {arguments_region}],
                    arguments={arguments},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                arguments=self._ToString(cast(List[ParserInfo], parser_info.arguments)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncArgumentsParserInfo_Arguments(
        self,
        parser_infos: List[FuncArgumentParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterFuncArgumentParserInfo(
        parser_info: FuncArgumentParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitFuncArgumentParserInfo(
        self,
        parser_info: FuncArgumentParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncArgumentParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {keyword_region}],
                    expression={expression},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                parser_info_type=str(parser_info.parser_info_type__),  # type: ignore
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                expression=self._ToString(parser_info.expression),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncArgumentParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  FuncParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterFuncParametersParserInfo(
        parser_info: FuncParametersParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitFuncParametersParserInfo(
        self,
        parser_info: FuncParametersParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncParametersParserInfo.Create(
                    regions=[{self_region}, {positional_region}, {any_region}, {keyword_region}],
                    positional={positional},
                    any_args={any},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                positional_region=self._ToString(parser_info.regions__.positional),
                any_region=self._ToString(parser_info.regions__.any),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                positional=self._ToString(cast(Optional[List[ParserInfo]], parser_info.positional)),
                any=self._ToString(cast(Optional[List[ParserInfo]], parser_info.any)),
                keyword=self._ToString(cast(Optional[List[ParserInfo]], parser_info.keyword)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncParametersParserInfo_Positional(
        self,
        parser_infos: List[FuncParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncParametersParserInfo_Any(
        self,
        parser_infos: List[FuncParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncParametersParserInfo_Keyword(
        self,
        parser_infos: List[FuncParameterParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterFuncParameterParserInfo(
        parser_info: FuncParameterParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitFuncParameterParserInfo(
        self,
        parser_info: FuncParameterParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncParameterParserInfo.Create(
                    regions=[{self_region}, {is_compile_time_region}, {is_variadic_region}, {name_region}],  # type: ignore
                    is_compile_time={is_compile_time},
                    type={type},
                    is_variadic={is_variadic},
                    name={name},
                    default_value={default_value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                is_compile_time_region=self._ToString(parser_info.regions__.is_compile_time),
                is_variadic_region=self._ToString(parser_info.regions__.is_variadic),
                name_region=self._ToString(parser_info.regions__.name),
                is_compile_time=self._ToString(parser_info.is_compile_time or False),
                type=self._ToString(parser_info.type),
                is_variadic=self._ToString(parser_info.is_variadic),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncParameterParserInfo_Type(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncParameterParserInfo_DefaultValue(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  TemplateParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTemplateParametersParserInfo(
        parser_info: TemplateParametersParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTemplateParametersParserInfo(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateParametersParserInfo.Create(
                    regions=[{self_region}, {positional_region}, {any_region}, {keyword_region}],
                    positional={positional},
                    any={any},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                positional_region=self._ToString(parser_info.regions__.positional),
                any_region=self._ToString(parser_info.regions__.any),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                positional=self._ToString(cast(Optional[List[ParserInfo]], parser_info.positional)),
                any=self._ToString(cast(Optional[List[ParserInfo]], parser_info.any)),
                keyword=self._ToString(cast(Optional[List[ParserInfo]], parser_info.keyword)),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnTemplateParametersParserInfo_Positional(
        self,
        parser_infos: List[TemplateParametersParserInfo.ParameterType],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTemplateParametersParserInfo_Any(
        self,
        parser_infos: List[TemplateParametersParserInfo.ParameterType],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTemplateParametersParserInfo_Keyword(
        self,
        parser_infos: List[TemplateParametersParserInfo.ParameterType],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTemplateTypeParameterParserInfo(
        parser_info: TemplateTypeParameterParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateTypeParameterParserInfo.Create(
                    regions=[{self_region}, {name_region}, {is_variadic_region}],
                    name={name},
                    is_variadic={is_variadic},
                    default_type={default_type},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                is_variadic_region=self._ToString(parser_info.regions__.is_variadic),
                name=self._ToString(parser_info.name),
                is_variadic=self._ToString(parser_info.is_variadic),
                default_type=self._ToString(parser_info.default_type),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnTemplateTypeParameterParserInfo_DefaultType(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTemplateDecoratorParameterParserInfo(
        parser_info: TemplateDecoratorParameterParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateDecoratorParameterParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateDecoratorParameterParserInfo.Create(
                    regions=[{self_region}, {name_region}],
                    type={type},
                    name={name},
                    default_value={default_value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                type=self._ToString(parser_info.type),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorParameterParserInfo_Type(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorParameterParserInfo_DefaultValue(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # |  BinaryExpressionParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterBinaryExpressionParserInfo(
        parser_info: BinaryExpressionParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitBinaryExpressionParserInfo(
        self,
        parser_info: BinaryExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = BinaryExpressionParserInfo.Create(
                    regions=[{self_region}, {operator_region}],
                    left_expression={left_expression},
                    operator={operator},
                    right_expression={right_expression},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                operator_region=self._ToString(parser_info.regions__.operator),
                left_expression=self._ToString(parser_info.left_expression),
                operator="BinaryExpressionOperatorType.{}".format(parser_info.operator.name),
                right_expression=self._ToString(parser_info.right_expression),
            ),
        )

    # ----------------------------------------------------------------------
    def OnBinaryExpressionParserInfo_LeftExpression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnBinaryExpressionParserInfo_RightExpression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  BooleanExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnBooleanExpressionParserInfo(
        self,
        parser_info: BooleanExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = BooleanExpressionParserInfo.Create(
                    regions=[{self_region}],
                    value={value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=self._ToString(parser_info.value),
            ),
        )

    # ----------------------------------------------------------------------
    # |  CallExpressionParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterCallExpressionParserInfo(
        parser_info: CallExpressionParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitCallExpressionParserInfo(
        self,
        parser_info: CallExpressionParserInfo,
    ) -> None:
        self._imports.add("from v1.Parser.ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = CallExpressionParserInfo.Create(
                    regions=[{self_region}, {arguments_region}],
                    expression={expression},
                    arguments={arguments},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                expression=self._ToString(parser_info.expression),
                arguments=self._ToString(parser_info.arguments),
            ),
        )

    # ----------------------------------------------------------------------
    def OnCallExpressionParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnCallExpressionParserInfo_Arguments(
        self,
        parser_info: FuncArgumentsParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  CharacterExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnCharacterExpressionParserInfo(
        self,
        parser_info: CharacterExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = CharacterExpressionParserInfo.Create(
                    regions=[{self_region}],
                    value='{value}',
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=chr(parser_info.value),
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncOrTypeExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncOrTypeExpressionParserInfo.Create(
                    regions=[{self_region}, {is_compile_time_region}, {name_region}],
                    is_compile_time={is_compile_time},
                    name={name},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                is_compile_time_region=self._ToString(parser_info.regions__.is_compile_time),
                name_region=self._ToString(parser_info.regions__.name),
                is_compile_time=self._ToString(parser_info.is_compile_time or False),
                name=self._ToString(parser_info.name),
            ),
        )

    # ----------------------------------------------------------------------
    # |  IntegerExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnIntegerExpressionParserInfo(
        self,
        parser_info: IntegerExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IntegerExpressionParserInfo.Create(
                    regions=[{self_region}],
                    value={value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=parser_info.value,
            ),
        )

    # ----------------------------------------------------------------------
    # |  NoneExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnNoneExpressionParserInfo(
        self,
        parser_info: NoneExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = NoneExpressionParserInfo.Create(
                    regions=[{self_region}],
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
            ),
        )

    # ----------------------------------------------------------------------
    # |  NumberExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnNumberExpressionParserInfo(
        self,
        parser_info: NumberExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = NumberExpressionParserInfo.Create(
                    regions=[{self_region}],
                    value={value},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=parser_info.value,
            ),
        )

    # ----------------------------------------------------------------------
    # |  StringExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnStringExpressionParserInfo(
        self,
        parser_info: StringExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = StringExpressionParserInfo.Create(
                    regions=[{self_region}],
                    value="{value}",
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=parser_info.value.replace("\n", "\\n"),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TernaryExpressionParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTernaryExpressionParserInfo(
        parser_info: TernaryExpressionParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TernaryExpressionParserInfo.Create(
                    regions=[{self_region}],
                    condition_expression={condition_expression},
                    true_expression={true_expression},
                    false_expression={false_expression},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                condition_expression=self._ToString(parser_info.condition_expression),
                true_expression=self._ToString(parser_info.true_expression),
                false_expression=self._ToString(parser_info.false_expression),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTernaryExpressionParserInfo_ConditionExpression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTernaryExpressionParserInfo_TrueExpression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTernaryExpressionParserInfo_FalseExpression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  TypeCheckExpressionParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTypeCheckExpressionParserInfo(
        parser_info: TypeCheckExpressionParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTypeCheckExpressionParserInfo(
        self,
        parser_info: TypeCheckExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo, OperatorType as TypeCheckExpressionParserInfoOperatorType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TypeCheckExpressionParserInfo.Create(
                    regions=[{self_region}, {operator_region}],
                    operator={operator},
                    expression={expression},
                    type={type},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                operator_region=self._ToString(parser_info.regions__.operator),
                operator="TypeCheckExpressionParserInfoOperatorType.{}".format(parser_info.operator.name),
                expression=self._ToString(parser_info.expression),
                type=self._ToString(parser_info.type),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTypeCheckExpressionParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnTypeCheckExpressionParserInfo_Type(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  UnaryExpressionParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterUnaryExpressionParserInfo(
        parser_info: UnaryExpressionParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitUnaryExpressionParserInfo(
        self,
        parser_info: UnaryExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo, OperatorType as UnaryExpressionParserInfoOperatorType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = UnaryExpressionParserInfo.Create(
                    regions=[{self_region}, {operator_region}],
                    operator={operator},
                    expression={expression},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                operator_region=self._ToString(parser_info.regions__.operator),
                operator="UnaryExpressionParserInfoOperatorType.{}".format(parser_info.operator.name),
                expression=self._ToString(parser_info.expression),
            ),
        )

    # ----------------------------------------------------------------------
    def OnUnaryExpressionParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  VariableExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnVariableExpressionParserInfo(
        self,
        parser_info: VariableExpressionParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = VariableExpressionParserInfo.Create(
                    regions=[{self_region}, {is_compile_time_region}, {name_region}],
                    is_compile_time={is_compile_time},
                    name={name},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                is_compile_time_region=self._ToString(parser_info.regions__.is_compile_time),
                name_region=self._ToString(parser_info.regions__.name),
                is_compile_time=self._ToString(parser_info.is_compile_time or False),
                name=self._ToString(parser_info.name),
            ),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # |  ClassStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterClassStatementParserInfo(
        parser_info: ClassStatementParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ClassStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {class_modifier_region}, {name_region}, {documentation_region}, {extends_region}, {implements_region}, {uses_region}, {statements_region}, {constructor_visibility_region}, {is_abstract_region}, {is_final_region}],
                    class_capabilities={class_capabilities},
                    visibility_param={visibility},
                    class_modifier_param={class_modifier},
                    name={name},
                    documentation={documentation},
                    templates={templates},
                    constraints={constraints},
                    extends={extends},
                    implements={implements},
                    uses={uses},
                    statements={statements},
                    constructor_visibility_param={constructor_visibility},
                    is_abstract={is_abstract},
                    is_final={is_final},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                class_modifier_region=self._ToString(parser_info.regions__.class_modifier),
                name_region=self._ToString(parser_info.regions__.name),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                extends_region=self._ToString(parser_info.regions__.extends),
                implements_region=self._ToString(parser_info.regions__.implements),
                uses_region=self._ToString(parser_info.regions__.uses),
                statements_region=self._ToString(parser_info.regions__.statements),
                constructor_visibility_region=self._ToString(parser_info.regions__.constructor_visibility),
                is_abstract_region=self._ToString(parser_info.regions__.is_abstract),
                is_final_region=self._ToString(parser_info.regions__.is_final),
                class_capabilities="{}Capabilities".format(parser_info.class_capabilities.name),
                visibility=self._ToString(parser_info.visibility),
                class_modifier=self._ToString(parser_info.class_modifier),
                name=self._ToString(parser_info.name),
                documentation=self._ToString(parser_info.documentation),
                templates=self._ToString(parser_info.templates),
                constraints=self._ToString(parser_info.constraints),
                extends=self._ToString(parser_info.extends),                # type: ignore
                implements=self._ToString(parser_info.implements),          # type: ignore
                uses=self._ToString(parser_info.uses),                      # type: ignore
                statements=self._ToString(parser_info.statements),          # type: ignore
                constructor_visibility=self._ToString(parser_info.constructor_visibility),
                is_abstract=self._ToString(parser_info.is_abstract),
                is_final=self._ToString(parser_info.is_final),
            ),
        )

    # ----------------------------------------------------------------------
    def OnClassStatementParserInfo_Templates(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnClassStatementParserInfo_Constraints(
        self,
        parser_info: ConstraintParametersParserInfo,
    ):
        parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnClassStatementParserInfo_Extends(
        self,
        parser_infos: List[ClassStatementDependencyParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnClassStatementParserInfo_Implements(
        self,
        parser_infos: List[ClassStatementDependencyParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnClassStatementParserInfo_Uses(
        self,
        parser_infos: List[ClassStatementDependencyParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterClassStatementDependencyParserInfo(
        parser_info: ClassStatementDependencyParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitClassStatementDependencyParserInfo(
        self,
        parser_info: ClassStatementDependencyParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.ClassStatementParserInfo import ClassStatementDependencyParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ClassStatementDependencyParserInfo.Create(
                    regions=[{self_region}, {visibility_region}],
                    visibility={visibility},
                    type={type},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                visibility=self._ToString(parser_info.visibility),
                type=self._ToString(parser_info.type),
            ),
        )

    # ----------------------------------------------------------------------
    def OnClassStatementDependencyParserInfo_Type(
        self,
        parser_info: StandardTypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  FuncDefinitionStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterFuncDefinitionStatementParserInfo(
        parser_info: FuncDefinitionStatementParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitFuncDefinitionStatementParserInfo(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo, OperatorType as FuncDefinitionStatementParserInfoOperatorType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncDefinitionStatementParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {visibility_region}, {mutability_region}, {method_modifier_region}, {name_region}, {documentation_region}, {captured_variables_region}, {parameters_region}, {statements_region}, {is_deferred_region}, {is_exceptional_region}, {is_generator_region}, {is_reentrant_region}, {is_scoped_region}, {is_static_region}],
                    class_capabilities={class_capabilities},
                    visibility_param={visibility},
                    mutability_param={mutability},
                    method_modifier_param={method_modifier},
                    return_type={return_type},
                    name={name},
                    documentation={documentation},
                    templates={templates},
                    captured_variables={captured_variables},
                    parameters={parameters},
                    statements={statements},
                    is_deferred={is_deferred},
                    is_exceptional={is_exceptional},
                    is_generator={is_generator},
                    is_reentrant={is_reentrant},
                    is_scoped={is_scoped},
                    is_static={is_static},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                parser_info_type=str(parser_info.parser_info_type__),  # type: ignore
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                mutability_region=self._ToString(parser_info.regions__.mutability),
                method_modifier_region=self._ToString(parser_info.regions__.method_modifier),
                name_region=self._ToString(parser_info.regions__.name),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                captured_variables_region=self._ToString(parser_info.regions__.captured_variables),
                parameters_region=self._ToString(parser_info.regions__.parameters),
                statements_region=self._ToString(parser_info.regions__.statements),
                is_deferred_region=self._ToString(parser_info.regions__.is_deferred),
                is_exceptional_region=self._ToString(parser_info.regions__.is_exceptional),
                is_generator_region=self._ToString(parser_info.regions__.is_generator),
                is_reentrant_region=self._ToString(parser_info.regions__.is_reentrant),
                is_scoped_region=self._ToString(parser_info.regions__.is_scoped),
                is_static_region=self._ToString(parser_info.regions__.is_static),
                class_capabilities="None" if parser_info.class_capabilities is None else "{}Capabilities".format(parser_info.class_capabilities.name),
                visibility=self._ToString(parser_info.visibility),
                mutability=self._ToString(parser_info.mutability),
                method_modifier=self._ToString(parser_info.method_modifier),
                return_type=self._ToString(parser_info.return_type),
                name=self._ToString(parser_info.name) if isinstance(parser_info.name, str) else "FuncDefinitionStatementParserInfoOperatorType.{}".format(parser_info.name.name),
                documentation=self._ToString(parser_info.documentation),
                templates=self._ToString(parser_info.templates),
                captured_variables=self._ToString(parser_info.captured_variables),    # type: ignore
                parameters=self._ToString(parser_info.parameters),
                statements=self._ToString(parser_info.statements),                    # type: ignore
                is_deferred=self._ToString(parser_info.is_deferred),
                is_exceptional=self._ToString(parser_info.is_exceptional),
                is_generator=self._ToString(parser_info.is_generator),
                is_reentrant=self._ToString(parser_info.is_reentrant),
                is_scoped=self._ToString(parser_info.is_scoped),
                is_static=self._ToString(parser_info.is_static),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncDefinitionStatementParserInfo_CapturedVariables(
        self,
        parser_infos: List[VariableNameParserInfo],
    ):
        for item in parser_infos:
            item.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncDefinitionStatementParserInfo_Parameters(
        self,
        parser_info: FuncParametersParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncDefinitionStatementParserInfo_ReturnType(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnFuncDefinitionStatementParserInfo_Templates(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  IfStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterIfStatementParserInfo(
        parser_info: IfStatementParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ) -> None:
        self._imports.add("from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IfStatementParserInfo.Create(
                    regions=[{self_region}, {else_statements_region}, {else_documentation_region}],
                    clauses={clauses},
                    else_statements={else_statements},
                    else_documentation={else_documentation},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                else_statements_region=self._ToString(parser_info.regions__.else_statements),
                else_documentation_region=self._ToString(parser_info.regions__.else_documentation),
                clauses=self._ToString(parser_info.clauses),                    # type: ignore
                else_statements=self._ToString(parser_info.else_statements),    # type: ignore
                else_documentation=self._ToString(parser_info.else_documentation),
            ),
        )

    # ----------------------------------------------------------------------
    def OnIfStatementParserInfo_Clauses(
        self,
        parser_infos: List[IfStatementClauseParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnIfStatementParserInfo_ElseStatements(
        self,
        parser_infos: List[StatementParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterIfStatementClauseParserInfo(
        parser_info: IfStatementClauseParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitIfStatementClauseParserInfo(
        self,
        parser_info: IfStatementClauseParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.IfStatementParserInfo import IfStatementClauseParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = IfStatementClauseParserInfo.Create(
                    regions=[{self_region}, {statements_region}, {documentation_region}],
                    expression={expression},
                    statements={statements},
                    documentation={documentation},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                statements_region=self._ToString(parser_info.regions__.statements),
                documentation_region=self._ToString(parser_info.regions__.documentation),
                expression=self._ToString(parser_info.expression),
                statements=self._ToString(parser_info.statements),  # type: ignore
                documentation=self._ToString(parser_info.documentation),
            ),
        )

    # ----------------------------------------------------------------------
    def OnIfStatementClauseParserInfo_Expression(
        self,
        parser_info: ExpressionParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnIfStatementClauseParserInfo_Statements(
        self,
        parser_infos: List[StatementParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  ImportStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterImportStatementParserInfo(
        parser_info: ImportStatementParserInfo,  # pylint: disable=unused-argument,
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ) -> None:
        self._imports.add("from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType as ImportStatementParserInfoImportType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ImportStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {source_filename_region}],
                    visibility_param={visibility},
                    source_filename={source_filename},
                    import_items={import_items},
                    import_type={import_type},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                source_filename_region=self._ToString(parser_info.regions__.source_filename),
                visibility=self._ToString(parser_info.visibility),
                source_filename=self._ToString(parser_info.source_filename),
                import_items=self._ToString(parser_info.import_items),  # type: ignore
                import_type="ImportStatementParserInfoImportType.{}".format(parser_info.import_type.name),
            ),
        )

    # ----------------------------------------------------------------------
    def OnImportStatementParserInfo_ImportItems(
        self,
        parser_infos: List[ImportStatementItemParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnImportStatementItemParserInfo(
        self,
        parser_info: ImportStatementItemParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.ImportStatementParserInfo import ImportStatementItemParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = ImportStatementItemParserInfo.Create(
                    regions=[{self_region}, {name_region}, {alias_region}],
                    name={name},
                    alias={alias},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                alias_region=self._ToString(parser_info.regions__.alias),
                name=self._ToString(parser_info.name),
                alias=self._ToString(parser_info.alias),
            ),
        )

    # ----------------------------------------------------------------------
    # |  PassStatementParserInfo
    # ----------------------------------------------------------------------
    def OnPassStatementParserInfo(
        self,
        parser_info: PassStatementParserInfo,  # pylint: disable=unused-argument
    ) -> None:
        self._imports.add("from v1.Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = PassStatementParserInfo.Create([{self_region}])
                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
            ),
        )

    # ----------------------------------------------------------------------
    # |  SpecialMethodStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterSpecialMethodStatementParserInfo(
        parser_info: SpecialMethodStatementParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.Continue

    # ----------------------------------------------------------------------
    def OnExitSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = SpecialMethodStatementParserInfo.Create(
                    regions=[{self_region}, {type_region}, {statements_region}],
                    class_capabilities={class_capabilities},
                    the_type={type},
                    statements={statements},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                type_region=self._ToString(parser_info.regions__.type),
                statements_region=self._ToString(parser_info.regions__.statements),
                class_capabilities="{}Capabilities".format(parser_info.class_capabilities.name),
                type="SpecialMethodType.{}".format(parser_info.type.name),
                statements=self._ToString(cast(List[ParserInfo], parser_info.statements)),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TypeAliasStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTypeAliasStatementParserInfo(
        parser_info: TypeAliasStatementParserInfo,
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TypeAliasStatementParserInfo.Create(
                    regions=[{self_region}, {visibility_region}, {name_region}],
                    visibility_param={visibility},
                    name={name},
                    type={type},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                visibility_region=self._ToString(parser_info.regions__.visibility),
                name_region=self._ToString(parser_info.regions__.name),
                visibility=self._ToString(parser_info.visibility),
                name=self._ToString(parser_info.name),
                type=self._ToString(parser_info.type),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTypeAliasStatementParserInfo_Type(
        self,
        parser_info: TypeParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # |  StandardTypeParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterStandardTypeParserInfo(
        parser_info: StandardTypeParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitStandardTypeParserInfo(
        self,
        parser_info: StandardTypeParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Types.StandardTypeParserInfo import StandardTypeParserInfo, StandardTypeItemParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = StandardTypeParserInfo.Create(
                    regions=[{self_region}, {mutability_modifier_region}, {items_region}],
                    mutability_modifier={mutability_modifier},
                    items={items},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                mutability_modifier_region=self._ToString(parser_info.regions__.mutability_modifier),
                mutability_modifier=self._ToString(parser_info.mutability_modifier),
                items_region=self._ToString(parser_info.regions__.items),
                items=self._ToString(cast(List[ParserInfo], parser_info.items)),
            ),
        )

        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnStandardTypeParserInfo_Items(
        self,
        parser_infos: List[StandardTypeItemParserInfo],
    ):
        for item in parser_infos:
            item.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterStandardTypeItemParserInfo(
        parser_info: StandardTypeItemParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitStandardTypeItemParserInfo(
        self,
        parser_info: StandardTypeItemParserInfo,
    ):
        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = StandardTypeItemParserInfo.Create(
                    regions=[{self_region}, {name_region}],
                    name={name},
                    templates={templates},
                    constraints={constraints},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                name=self._ToString(parser_info.name),
                templates=self._ToString(parser_info.templates),
                constraints=self._ToString(parser_info.constraints),
            ),
        )

    # ----------------------------------------------------------------------
    def OnStandardTypeItemParserInfo_Templates(
        self,
        parser_info: TemplateArgumentsParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    def OnStandardTypeItemParserInfo_Constraints(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        return parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  TupleTypeParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterTupleTypeParserInfo(
        parser_info: TupleTypeParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitTupleTypeParserInfo(
        self,
        parser_info: TupleTypeParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Types.TupleTypeParserInfo import TupleTypeParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TupleTypeParserInfo.Create(
                    regions=[{self_region}, {mutability_modifier_region}, {types_region}],
                    mutability_modifier={mutability_modifier},
                    types={types},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                mutability_modifier_region=self._ToString(parser_info.regions__.mutability_modifier),
                types_region=self._ToString(parser_info.regions__.types),
                mutability_modifier=self._ToString(parser_info.mutability_modifier),
                types=self._ToString(cast(List[ParserInfo], parser_info.types)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTupleTypeParserInfo_Types(
        self,
        parser_infos: List[TypeParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # |  VariantTypeParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterVariantTypeParserInfo(
        parser_info: VariantTypeParserInfo,  # pylint: disable=unused-argument
    ):
        return VisitControl.ContinueWithDetail

    # ----------------------------------------------------------------------
    def OnExitVariantTypeParserInfo(
        self,
        parser_info: VariantTypeParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Types.VariantTypeParserInfo import VariantTypeParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = VariantTypeParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {mutability_modifier_region}, {types_region}],
                    mutability_modifier={mutability_modifier},
                    types={types},
                )

                """,
            ).format(
                statement_name=self.__class__._CreateStatementName(parser_info),
                parser_info_type=str(parser_info.parser_info_type__),  # type: ignore
                self_region=self._ToString(parser_info.regions__.self__),
                mutability_modifier_region=self._ToString(parser_info.regions__.mutability_modifier),
                types_region=self._ToString(parser_info.regions__.types),
                mutability_modifier=self._ToString(parser_info.mutability_modifier),
                types=self._ToString(cast(List[ParserInfo], parser_info.types)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnVariantTypeParserInfo_Types(
        self,
        parser_infos: List[TypeParserInfo],
    ):
        for parser_info in parser_infos:
            parser_info.Accept(self)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateStatementName(
        parser_info: ParserInfo,
    ) -> str:
        return "statement{line_begin:0>4}{column_begin:0>4}_{line_end:0>4}{column_end:0>4}".format(
            line_begin=parser_info.regions__.self__.begin.line,
            column_begin=parser_info.regions__.self__.begin.column,
            line_end=parser_info.regions__.self__.end.line,
            column_end=parser_info.regions__.self__.end.column,
        )

    # ----------------------------------------------------------------------
    def _ToString(
        self,
        value: Union[
            None,
            str,
            bool,
            ClassModifier,
            MethodModifier,
            MutabilityModifier,
            VisibilityModifier,
            Location,
            Region,
            ParserInfo,
            List[ParserInfo],
        ],
    ) -> str:
        if value is None:
            return "None"
        elif isinstance(value, str):
            return '"{}"'.format(value)
        elif isinstance(value, bool):
            return str(value)
        elif isinstance(value, ClassModifier):
            return "ClassModifier.{}".format(value.name)
        elif isinstance(value, MethodModifier):
            return "MethodModifier.{}".format(value.name)
        elif isinstance(value, MutabilityModifier):
            return "MutabilityModifier.{}".format(value.name)
        elif isinstance(value, VisibilityModifier):
            return "VisibilityModifier.{}".format(value.name)
        elif isinstance(value, Location):
            return "Location(line={}, column={})".format(value.line, value.column)
        elif isinstance(value, Region):
            return "Region(begin={}, end={})".format(self._ToString(value.begin), self._ToString(value.end))
        elif isinstance(value, ParserInfo):
            return self.__class__._CreateStatementName(value)
        elif isinstance(value, list):
            return "[{}, ]".format(", ".join(self._ToString(item) for item in value))

        assert False, value
        return None
