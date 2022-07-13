# ----------------------------------------------------------------------
# |
# |  EntityResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-06 16:19:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EntityResolver object"""

import os

from typing import Callable, Optional, TYPE_CHECKING, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Types import Type

    from .Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..Common import MiniLanguageHelpers

    if TYPE_CHECKING:
        from .Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo  # pylint: disable=unused-import

        from .Statements.ClassStatementParserInfo import ClassStatementParserInfo  # pylint: disable=unused-import
        from .Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class EntityResolver(Interface.Interface):
    """Abstract interface for object that is able to resolve entities"""

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ResolveMiniLanguageType(
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ResolveMiniLanguageExpression(
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ResolveType(
        parser_info: ExpressionParserInfo,
        *,
        resolve_aliases: bool=False,
    ) -> Type:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateConcreteTypeFactory(
        parser_info: Union["ClassStatementParserInfo", "TypeAliasStatementParserInfo"],
    ) -> Callable[
        [
            Optional["TemplateArgumentsParserInfo"]
        ],
        Type
    ]:
        raise Exception("Abstract method")  # pragma: no cover
