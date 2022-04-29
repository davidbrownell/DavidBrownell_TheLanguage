# ----------------------------------------------------------------------
# |
# |  CommonMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 08:53:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CommonMixin object"""

import os
import textwrap

from typing import cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.ParserInfos.ParserInfo import ParserInfo, VisitControl

    from ....Parser.ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo
    from ....Parser.ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo, ConstraintArgumentParserInfo
    from ....Parser.ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ....Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo, FuncArgumentParserInfo
    from ....Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ....Parser.ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateDecoratorArgumentParserInfo, TemplateTypeArgumentParserInfo
    from ....Parser.ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateTypeParameterParserInfo, TemplateDecoratorParameterParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class CommonMixin(BaseMixin):
    """Implements functionality for ParserInfos/Common"""

    # ----------------------------------------------------------------------
    # |  CapturedVariablesParserInfo
    # ----------------------------------------------------------------------
    def OnCapturedVariablesParserInfo(
        self,
        parser_info: CapturedVariablesParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = CapturedVariablesParserInfo.Create(
                    regions=[{self_region}, {variables_region}],
                    variables={variables},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                variables_region=self._ToString(parser_info.regions__.variables),
                variables=self._ToString(cast(List[ParserInfo], parser_info.variables)),
            ),
        )

    # ----------------------------------------------------------------------
    # |  ConstraintArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnConstraintArgumentsParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                arguments=self._ToString(cast(List[ParserInfo], parser_info.arguments)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnConstraintArgumentParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                expression=self._ToString(parser_info.expression),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    # |  ConstraintParametersParserInfo
    # ----------------------------------------------------------------------
    def OnConstraintParametersParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
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
    def OnConstraintParameterParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                type=self._ToString(parser_info.type),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnFuncArgumentsParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                arguments=self._ToString(cast(List[ParserInfo], parser_info.arguments)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnFuncArgumentParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                parser_info_type=str(parser_info.parser_info_type__),  # type: ignore
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                expression=self._ToString(parser_info.expression),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    # |  FuncParametersParserInfo
    # ----------------------------------------------------------------------
    def OnFuncParametersParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
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
    def OnFuncParameterParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
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
    # |  TemplateArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnTemplateArgumentsParserInfo(
        self,
        parser_info: TemplateArgumentsParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateArgumentsParserInfo.Create(
                    regions=[{self_region}, {arguments_region}],
                    arguments={arguments},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                arguments_region=self._ToString(parser_info.regions__.arguments),
                arguments=self._ToString(cast(List[ParserInfo], parser_info.arguments)),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorArgumentParserInfo(
        self,
        parser_info: TemplateDecoratorArgumentParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateArgumentsParserInfo import TemplateDecoratorArgumentParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateDecoratorArgumentParserInfo.Create(
                    regions=[{self_region}, {keyword_region}],
                    expression={expression},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                expression=self._ToString(parser_info.expression),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTemplateTypeArgumentParserInfo(
        self,
        parser_info: TemplateTypeArgumentParserInfo,
    ):
        self._imports.add("from v1.Parser.ParserInfos.Common.TemplateArgumentsParserInfo import TemplateTypeArgumentParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = TemplateTypeArgumentParserInfo.Create(
                    regions=[{self_region}, {keyword_region}],
                    type={type},
                    keyword={keyword},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                keyword_region=self._ToString(parser_info.regions__.keyword),
                type=self._ToString(parser_info.type),
                keyword=self._ToString(parser_info.keyword),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TemplateParametersParserInfo
    # ----------------------------------------------------------------------
    def OnTemplateParametersParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
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
    def OnTemplateTypeParameterParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                is_variadic_region=self._ToString(parser_info.regions__.is_variadic),
                name=self._ToString(parser_info.name),
                is_variadic=self._ToString(parser_info.is_variadic),
                default_type=self._ToString(parser_info.default_type),
            ),
        )

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorParameterParserInfo(
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
                statement_name=self._CreateStatementName(parser_info),
                self_region=self._ToString(parser_info.regions__.self__),
                name_region=self._ToString(parser_info.regions__.name),
                type=self._ToString(parser_info.type),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )
