# ----------------------------------------------------------------------
# |
# |  RootTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 09:48:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootTypeResolver"""

import os

from typing import Dict, List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...StatementTypeResolver import CompileTimeInfo, StatementTypeResolver

    from .....ParserInfos.Types.ConcreteType import ConcreteType


# ----------------------------------------------------------------------
class RootTypeResolver(StatementTypeResolver):
    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ) -> "RootTypeResolver":
        return RootTypeResolver(
            self.namespace,
            self.fundamental_namespace,
            compile_time_info,
            self.root_resolvers,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateConcreteTypeImpl(*args, **kwargs) -> ConcreteType:
        raise Exception("This method should never be invoked on RootTypeResolver types")
