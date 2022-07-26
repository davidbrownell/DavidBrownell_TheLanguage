# ----------------------------------------------------------------------
# |
# |  FuncDefinitionTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 10:25:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionTypeResolver object"""

import os

from typing import Dict, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...StatementTypeResolver import StatementTypeResolver
    from ...TypeResolver import TypeResolver

    from .....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from .....ParserInfos.ParserInfo import CompileTimeInfo

    from .....ParserInfos.Types.ConcreteType import ConcreteType


# ----------------------------------------------------------------------
class FuncDefinitionTypeResolver(StatementTypeResolver):
    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ) -> "FuncDefinitionTypeResolver":
        return FuncDefinitionTypeResolver(
            self.namespace,
            self.fundamental_namespace,
            compile_time_info,
            self.root_resolvers,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(
        self,
        updated_type_resolver: StatementTypeResolver,
    ) -> ConcreteType:
        pass # BugBug
