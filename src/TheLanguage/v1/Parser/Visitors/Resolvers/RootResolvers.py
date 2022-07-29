# ----------------------------------------------------------------------
# |
# |  RootResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 15:37:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootResolver object"""

import os

from typing import Dict, Generator, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.ConcreteTypeResolver import ConcreteTypeResolver

    from ..Namespaces import ImportNamespace, Namespace, ParsedNamespace

    from ...ParserInfos.ParserInfo import CompileTimeInfo

    from ...ParserInfos.Types.GenericTypes import GenericStatementType


# ----------------------------------------------------------------------
class RootConcreteTypeResolver(ConcreteTypeResolver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        namespace: ParsedNamespace,
        fundamental_namespace: Optional[Namespace],
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ):
        super(RootConcreteTypeResolver, self).__init__(
            parent=None,
            namespace=namespace,
            fundamental_namespace=fundamental_namespace,
            compile_time_info=compile_time_info,
            root_type_resolvers=None,
        )

    # ----------------------------------------------------------------------
    def EnumGenericTypes(self) -> Generator[GenericStatementType, None, None]:
        assert self.is_finalized

        for namespace_or_namespaces in self.namespace.EnumChildren():
            if isinstance(namespace_or_namespaces, list):
                namespaces = namespace_or_namespaces
            else:
                namespaces = [namespace_or_namespaces, ]

            for namespace in namespaces:
                if isinstance(namespace, ImportNamespace):
                    continue

                assert isinstance(namespace, ParsedNamespace), namespace
                yield self.GetOrCreateNestedGenericTypeViaNamespace(namespace)
