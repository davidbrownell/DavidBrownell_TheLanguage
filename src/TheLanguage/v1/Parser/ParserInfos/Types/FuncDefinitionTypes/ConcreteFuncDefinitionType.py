# ----------------------------------------------------------------------
# |
# |  ConcreteFuncDefinitionType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 15:19:40
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

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ConcreteType import ConcreteType
    from ..ConstrainedType import ConstrainedType

    from ...Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo


# ----------------------------------------------------------------------
class TypeResolver(Interface.Interface):
    pass # BugBug


# ----------------------------------------------------------------------
class ConcreteFuncDefinitionType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
        type_resolver: TypeResolver,
    ):
        super(ConcreteFuncDefinitionType, self).__init__(parser_info)

        self._type_resolver                 = type_resolver

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> FuncDefinitionStatementParserInfo:
        assert isinstance(self._parser_info, FuncDefinitionStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        pass # BugBug

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        pass # BugBug

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> ConstrainedType:
        assert False, "BugBug: CreateConstrainedType (ConcreteFuncDefinition)"
