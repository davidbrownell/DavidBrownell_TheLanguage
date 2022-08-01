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

from typing import Callable, List, Optional

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
    from ..TypeResolver import TypeResolver

    from ...Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo

    from ....Error import Error, ErrorException


# ----------------------------------------------------------------------
class ConcreteFuncDefinitionType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        super(ConcreteFuncDefinitionType, self).__init__(parser_info)

        concrete_return_type: Optional[ConcreteType] = None
        concrete_parameters: List[ConcreteType] = []

        if parser_info.return_type is not None:
            concrete_return_type = type_resolver.EvalConcreteType(parser_info.return_type)

        if not isinstance(parser_info.parameters, bool):
            for parameter in parser_info.parameters.EnumParameters():
                concrete_parameters.append(type_resolver.EvalConcreteType(parameter.type))

        self._type_resolver                 = type_resolver

        self._concrete_return_type          = concrete_return_type
        self._concrete_parameters           = concrete_parameters

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
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass1))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass2))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass3Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass3))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass4Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass4))

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> ConstrainedType:
        pass # BugBug

    # ----------------------------------------------------------------------
    def _FinalizeImpl(
        self,
        finalize_func: Callable[[ConcreteType], None],
    ) -> None:
        errors: List[Error] = []

        if self._concrete_return_type is not None:
            try:
                finalize_func(self._concrete_return_type)
            except ErrorException as ex:
                errors += ex.errors

        for concrete_parameter in self._concrete_parameters:
            try:
                finalize_func(concrete_parameter)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)
