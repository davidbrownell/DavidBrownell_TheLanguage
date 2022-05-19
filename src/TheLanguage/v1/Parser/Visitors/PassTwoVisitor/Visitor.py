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
from typing import Dict, List, Optional, Union

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

    from ..NamespaceInfo import ParsedNamespaceInfo
    from ..StateMaintainer import StateMaintainer

    from ...Error import CreateError, Error, ErrorException
    from ...Helpers import MiniLanguageHelpers

    from ...MiniLanguage.Types.CustomType import CustomType

    from ...ParserInfos.ParserInfo import ParserInfo, RootParserInfo, VisitResult
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo


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
        minilanguage_configuration_values: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        fully_qualified_name: str,  # pylint: disable=unused-argument
        root: RootParserInfo,
    ) -> List[Error]:
        visitor = cls(minilanguage_configuration_values)

        root.Accept(visitor)

        return visitor._errors  # pylint: disable=protected-access
