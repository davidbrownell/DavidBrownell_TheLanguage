# ----------------------------------------------------------------------
# |
# |  ClassTypes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 13:14:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that have knowledge of classes"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeResolver import TypeResolver
    from .Impl.GenericTypeImpl import GenericTypeImpl

    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType

    from ...ParserInfos.Types.ClassTypes.ConcreteClassType import ConcreteClassType


# ----------------------------------------------------------------------
class ClassGenericType(GenericTypeImpl[ClassStatementParserInfo]):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateConcreteType(
        updated_resolver: TypeResolver,
        expression_parser_info: ExpressionParserInfo,  # pylint: disable=unused-argument
    ) -> ConcreteType:
        assert isinstance(updated_resolver.namespace.parser_info, ClassStatementParserInfo), updated_resolver.namespace.parser_info
        assert isinstance(expression_parser_info, FuncOrTypeExpressionParserInfo), expression_parser_info

        return ConcreteClassType(
            updated_resolver,
            updated_resolver.namespace.parser_info,
            expression_parser_info,
        )
