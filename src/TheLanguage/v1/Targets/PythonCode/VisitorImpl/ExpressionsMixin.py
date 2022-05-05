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

from contextlib import contextmanager
from typing import cast, List

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.MiniLanguage.Types.BooleanType import BooleanType
    from ....Parser.MiniLanguage.Types.CharacterType import CharacterType
    from ....Parser.MiniLanguage.Types.CustomType import CustomType
    from ....Parser.MiniLanguage.Types.IntegerType import IntegerType
    from ....Parser.MiniLanguage.Types.NoneType import NoneType
    from ....Parser.MiniLanguage.Types.NumberType import NumberType
    from ....Parser.MiniLanguage.Types.StringType import StringType
    from ....Parser.MiniLanguage.Types.Type import Type as MiniLanguageType
    from ....Parser.MiniLanguage.Types.VariantType import VariantType

    from ....Parser.ParserInfos.ParserInfo import ParserInfo

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
    from ....Parser.ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.UnaryExpressionParserInfo import UnaryExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ....Parser.ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class ExpressionsMixin(BaseMixin):
    """Implements functionality for ParserInfos/Expressions"""

    # ----------------------------------------------------------------------
    # |  BinaryExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBinaryExpressionParserInfo(
        self,
        parser_info: BinaryExpressionParserInfo,
    ):
        yield

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
                statement_name=self._CreateStatementName(parser_info),
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=self._ToString(parser_info.value),
            ),
        )

    # ----------------------------------------------------------------------
    # |  CallExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnCallExpressionParserInfo(
        self,
        parser_info: CallExpressionParserInfo,
    ):
        yield

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
                statement_name=self._CreateStatementName(parser_info),
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=parser_info.value,
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncOrTypeExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncOrTypeExpressionParserInfo(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.ParserInfo import ParserInfoType")
        self._imports.add("from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo")

        # Get the type name
        value_contents = None

        if isinstance(parser_info.value, BooleanType):
            type_name = "BooleanType"
        elif isinstance(parser_info.value, CharacterType):
            type_name = "CharacterType"
        elif isinstance(parser_info.value, CustomType):
            type_name = "CustomType"
            value_contents = '"{}"'.format(parser_info.value.name)
        elif isinstance(parser_info.value, IntegerType):
            type_name = "IntegerType"
        elif isinstance(parser_info.value, NoneType):
            type_name = "NoneType"
        elif isinstance(parser_info.value, NumberType):
            type_name = "NumberType"
        elif isinstance(parser_info.value, StringType):
            type_name = "StringType"
        else:
            assert False, parser_info.value  # pragma: no cover

        self._imports.add(
            "from v1.Parser.MiniLanguage.Types.{type_name} import {type_name}".format(
                type_name=type_name,
            ),
        )

        value = "{}({})".format(type_name, value_contents or "")

        if parser_info.mutability_modifier is not None:
            self._imports.add("from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncOrTypeExpressionParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {value_region}, {mutability_modifier_region}],
                    value={value},
                    templates={templates},
                    constraints={constraints},
                    mutability_modifier={mutability_modifier},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                parser_info_type=parser_info.parser_info_type__,
                self_region=self._ToString(parser_info.regions__.self__),
                value_region=self._ToString(parser_info.regions__.value),
                mutability_modifier_region=self._ToString(parser_info.regions__.mutability_modifier),
                value=value,
                templates=self._ToString(parser_info.templates),
                constraints=self._ToString(parser_info.constraints),
                mutability_modifier=str(parser_info.mutability_modifier),
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
                statement_name=self._CreateStatementName(parser_info),
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
                statement_name=self._CreateStatementName(parser_info),
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
                statement_name=self._CreateStatementName(parser_info),
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                value=parser_info.value.replace("\n", "\\n"),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TernaryExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTernaryExpressionParserInfo(
        self,
        parser_info: TernaryExpressionParserInfo,
    ):
        yield

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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                condition_expression=self._ToString(parser_info.condition_expression),
                true_expression=self._ToString(parser_info.true_expression),
                false_expression=self._ToString(parser_info.false_expression),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TupleExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleExpressionParserInfo(
        self,
        parser_info: TupleExpressionParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TupleExpressionParserInfo.Create(
                    regions=[{self_region}]
                    types={types},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                types=self._ToString(cast(List[ParserInfo], parser_info.types)),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TypeCheckExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeCheckExpressionParserInfo(
        self,
        parser_info: TypeCheckExpressionParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import TypeCheckExpressionParserInfo, OperatorType as TypeCheckExpressionParserInfoOperatorType")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TypeCheckExpressionParserInfo.Create(
                    regions=[{self_region}, {operator_region}],
                    operator={operator},
                    expression={expression},
                    the_type={type},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
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
    @contextmanager
    def OnUnaryExpressionParserInfo(
        self,
        parser_info: UnaryExpressionParserInfo,
    ):
        yield

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
                statement_name=self._CreateStatementName(parser_info),
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
        self._imports.add("from v1.Parser.ParserInfos.ParserInfo import ParserInfoType")
        self._imports.add("from v1.Parser.ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = VariableExpressionParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {name_region}],
                    name={name},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                parser_info_type=parser_info.parser_info_type__,
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                name=self._ToString(parser_info.name),
            ),
        )

    # ----------------------------------------------------------------------
    # |  VariantExpressionParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantExpressionParserInfo(
        self,
        parser_info: VariantExpressionParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo")

        if parser_info.mutability_modifier is not None:
            self._imports.add("from v1.Parser.ParserInfos.Common.MutabilityModifier import MutabilityModifier")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = VariantExpressionParserInfo.Create(
                    regions=[{self_region}, {mutability_region}],
                    types={types},
                    mutability_modifier={mutability},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                mutability_region=self._ToString(parser_info.regions__.mutability_modifier),
                types=self._ToString(cast(List[ParserInfo], parser_info.types)),
                mutability=str(parser_info.mutability_modifier),
            ),
        )
