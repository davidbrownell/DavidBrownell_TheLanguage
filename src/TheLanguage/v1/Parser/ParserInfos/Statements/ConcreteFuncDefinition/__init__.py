# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-13 13:22:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteFuncDefinition object"""

import os

from typing import List, Optional, TYPE_CHECKING, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...EntityResolver import EntityResolver
    from ...Types import ClassType, FuncDefinitionType, Type

    from ...Common.FuncParametersParserInfo import FuncParametersParserInfo

    if TYPE_CHECKING:
        from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ConcreteFuncDefinition(object):
    # ----------------------------------------------------------------------
    return_type: Optional[Type]
    parameters: Optional[List[Type]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        func_parser_info: "FuncDefinitionStatementParserInfo",
        entity_resolver: EntityResolver,
    ):
        if func_parser_info.return_type is None:
            return_type = None
        else:
            return_type = entity_resolver.ResolveType(func_parser_info.return_type)

        if isinstance(func_parser_info.parameters, FuncParametersParserInfo):
            parameters = [
                entity_resolver.ResolveType(parameter_parser_info.type)
                for parameter_parser_info in func_parser_info.parameters.EnumParameters()
            ]
        else:
            parameters = None

        # TODO: Error when visibility of types/parameters < visibility of method

        return cls(return_type, parameters)

    # ----------------------------------------------------------------------
    def Finalize(
        self,
        func_definition_type: FuncDefinitionType,
    ) -> None:
        # Nothing to to finalize
        pass
