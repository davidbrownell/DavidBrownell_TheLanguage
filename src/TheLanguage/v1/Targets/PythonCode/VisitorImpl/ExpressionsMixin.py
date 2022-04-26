# ----------------------------------------------------------------------
# |
# |  ExpressionsMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 09:08:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExpressionsMixin object"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.BooleanExpressionParserInfo import BooleanExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.CallExpressionParserInfo import CallExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.CharacterExpressionParserInfo import CharacterExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.IntegerExpressionParserInfo import IntegerExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.NumberExpressionParserInfo import NumberExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.StringExpressionParserInfo import StringExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.TernaryExpressionParserInfo import TernaryExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    """Implements functionality for ParserInfos/Expressions"""

    # ----------------------------------------------------------------------
    # |  BinaryExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnBinaryExpressionParserInfo(
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
    def OnCallExpressionParserInfo(
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
    def OnTernaryExpressionParserInfo(
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
    # |  TypeCheckExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnTypeCheckExpressionParserInfo(
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
    # |  UnaryExpressionParserInfo
    # ----------------------------------------------------------------------
    def OnUnaryExpressionParserInfo(
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
