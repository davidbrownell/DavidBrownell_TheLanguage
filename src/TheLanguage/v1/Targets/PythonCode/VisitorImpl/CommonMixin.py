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

from contextlib import contextmanager
from typing import cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.ParserInfos.ParserInfo import ParserInfo

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
    @contextmanager
    def OnCapturedVariablesParserInfo(
        self,
        parser_info: CapturedVariablesParserInfo,
    ):
        yield

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
    @contextmanager
    def OnConstraintArgumentsParserInfo(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        yield

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
    @contextmanager
    def OnConstraintArgumentParserInfo(
        self,
        parser_info: ConstraintArgumentParserInfo,
    ):
        yield

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
    @contextmanager
    def OnConstraintParametersParserInfo(
        self,
        parser_info: ConstraintParametersParserInfo,
    ):
        yield

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
    @contextmanager
    def OnConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        yield

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
    @contextmanager
    def OnFuncArgumentsParserInfo(
        self,
        parser_info: FuncArgumentsParserInfo,
    ):
        yield

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
    @contextmanager
    def OnFuncArgumentParserInfo(
        self,
        parser_info: FuncArgumentParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncArgumentParserInfo.Create(
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
    # |  FuncParametersParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncParametersParserInfo(
        self,
        parser_info: FuncParametersParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncParametersParserInfo.Create(
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
    @contextmanager
    def OnFuncParameterParserInfo(
        self,
        parser_info: FuncParameterParserInfo,
    ):
        yield

        self._imports.add("from v1.Parser.ParserInfos.ParserInfo import ParserInfoType")
        self._imports.add("from v1.Parser.ParserInfos.Common.FuncParametersParserInfo import FuncParameterParserInfo")

        self._stream.write(
            textwrap.dedent(
                """\
                {statement_name} = FuncParameterParserInfo.Create(
                    parser_info_type={parser_info_type},
                    regions=[{self_region}, {is_variadic_region}, {name_region}],  # type: ignore
                    type={type},
                    is_variadic={is_variadic},
                    name={name},
                    default_value={default_value},
                )

                """,
            ).format(
                statement_name=self._CreateStatementName(parser_info),
                parser_info_type=parser_info.parser_info_type__,
                self_region=self._ToString(parser_info.regions__.self__),
                is_variadic_region=self._ToString(parser_info.regions__.is_variadic),
                name_region=self._ToString(parser_info.regions__.name),
                type=self._ToString(parser_info.type),
                is_variadic=self._ToString(parser_info.is_variadic),
                name=self._ToString(parser_info.name),
                default_value=self._ToString(parser_info.default_value),
            ),
        )

    # ----------------------------------------------------------------------
    # |  TemplateArgumentsParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateArgumentsParserInfo(
        self,
        parser_info: TemplateArgumentsParserInfo,
    ):
        yield

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
    @contextmanager
    def OnTemplateDecoratorArgumentParserInfo(
        self,
        parser_info: TemplateDecoratorArgumentParserInfo,
    ):
        yield

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
    @contextmanager
    def OnTemplateTypeArgumentParserInfo(
        self,
        parser_info: TemplateTypeArgumentParserInfo,
    ):
        yield

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
    @contextmanager
    def OnTemplateParametersParserInfo(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        yield

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
    @contextmanager
    def OnTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        yield

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
    @contextmanager
    def OnTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        yield

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
