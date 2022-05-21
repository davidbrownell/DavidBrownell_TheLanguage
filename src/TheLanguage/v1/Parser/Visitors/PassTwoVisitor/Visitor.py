# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:19:19
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
import types

from contextlib import contextmanager, ExitStack
from typing import cast, Dict, List, Optional, Union, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CommonMixin import CommonMixin
    from .ExpressionsMixin import ExpressionsMixin
    from .StatementsMixin import StatementsMixin

    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo
    from ..StateMaintainer import StateMaintainer

    from ...Error import Error, ErrorException
    from ...GlobalRegion import GlobalRegion
    from ...Helpers import MiniLanguageHelpers
    from ...MiniLanguage.Types.CustomType import CustomType

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import ParserInfo, RootStatementParserInfo


# ----------------------------------------------------------------------
class Visitor(
    CommonMixin,
    ExpressionsMixin,
    StatementsMixin,
):
    # ----------------------------------------------------------------------
    @classmethod
    def CreateState(
        cls,
        mini_language_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        fundamental_types_namespace: Optional[NamespaceInfo],
    ) -> StateMaintainer[MiniLanguageHelpers.CompileTimeInfo]:
        state = StateMaintainer[MiniLanguageHelpers.CompileTimeInfo](mini_language_configuration_values)

        # Add the fundamental types
        if fundamental_types_namespace is not None:
            # ----------------------------------------------------------------------
            def EnumNamespace(
                namespace: NamespaceInfo,
            ) -> None:
                for namespace_info in namespace.children.values():
                    if not isinstance(namespace_info, ParsedNamespaceInfo):
                        EnumNamespace(namespace_info)
                        continue

                    assert isinstance(namespace_info.parser_info, RootStatementParserInfo), namespace_info.parser_info

                    for type_name, type_namespace_info in namespace_info.children.items():
                        if type_name is None:
                            continue

                        assert isinstance(type_name, str), type_name
                        assert isinstance(type_namespace_info, ParsedNamespaceInfo)

                        state.AddItem(
                            type_name,
                            MiniLanguageHelpers.CompileTimeInfo(
                                CustomType(type_name),
                                type_namespace_info.parser_info,
                                GlobalRegion.Create(
                                    cast(ParserInfo, type_namespace_info.parser_info).regions__.self__.begin,
                                    cast(ParserInfo, type_namespace_info.parser_info).regions__.self__.end,
                                    "__fundamental_types__",
                                    namespace_info.parser_info.name,
                                ),
                            ),
                        )

            # ----------------------------------------------------------------------

            EnumNamespace(fundamental_types_namespace)

        return state

    # ----------------------------------------------------------------------
    @classmethod
    def Execute(
        cls,
        state: StateMaintainer[MiniLanguageHelpers.CompileTimeInfo],
        global_namespace: NamespaceInfo,
        names: Tuple[str, str],  # pylint: disable=unused-argument
        root: RootStatementParserInfo,
    ) -> List[Error]:
        # Get this namespace
        this_namespace = global_namespace.children[names[0]]

        name_parts = os.path.splitext(names[1])[0]
        name_parts = name_parts.split(os.path.sep)

        for name_part in name_parts:
            this_namespace = this_namespace.children[name_part]

        assert isinstance(this_namespace, ParsedNamespaceInfo)

        visitor = cls(state, this_namespace)

        root.Accept(visitor)

        return visitor._errors  # pylint: disable=protected-access
