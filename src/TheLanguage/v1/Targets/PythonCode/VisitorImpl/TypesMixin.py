# ----------------------------------------------------------------------
# |
# |  TypesMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 09:15:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypesMixin object"""

import os
import textwrap

from typing import cast, List

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ....Parser.ParserInfos.ParserInfo import ParserInfo

    from ....Parser.ParserInfos.Types.StandardTypeParserInfo import StandardTypeParserInfo, StandardTypeItemParserInfo
    from ....Parser.ParserInfos.Types.TupleTypeParserInfo import TupleTypeParserInfo
    from ....Parser.ParserInfos.Types.VariantTypeParserInfo import VariantTypeParserInfo


# ----------------------------------------------------------------------
# pylint: disable=protected-access


# ----------------------------------------------------------------------
class TypesMixin(BaseMixin):
    """Implements functionality for ParserInfos/Types"""

    # ----------------------------------------------------------------------
    # |  StandardTypeParserInfo
    # ----------------------------------------------------------------------
    def OnStandardTypeParserInfo(
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

    # ----------------------------------------------------------------------
    def OnStandardTypeItemParserInfo(
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
    # |  TupleTypeParserInfo
    # ----------------------------------------------------------------------
    def OnTupleTypeParserInfo(
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
    # |  VariantTypeParserInfo
    # ----------------------------------------------------------------------
    def OnVariantTypeParserInfo(
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
