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

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import Error, ErrorException
    from ...GlobalRegion import GlobalRegion

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
    def Execute(
        cls,
        mini_language_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        global_namespace: NamespaceInfo,
        fundamental_types_namespace: Optional[NamespaceInfo],
        names: Tuple[str, str],  # pylint: disable=unused-argument
        root: RootStatementParserInfo,
    ) -> List[Error]:
        return [] # BugBug

        # Get this namespace
        this_namespace = global_namespace.children[names[0]]

        name_parts = os.path.splitext(names[1])[0]
        name_parts = name_parts.split(".")

        for name_part in name_parts:
            this_namespace = this_namespace.children[name_part]

        assert isinstance(this_namespace, ParsedNamespaceInfo)

        visitor = cls(
            mini_language_configuration_values,
            fundamental_types_namespace,
            this_namespace,
        )

        root.Accept(visitor)

        return visitor._errors  # pylint: disable=protected-access
