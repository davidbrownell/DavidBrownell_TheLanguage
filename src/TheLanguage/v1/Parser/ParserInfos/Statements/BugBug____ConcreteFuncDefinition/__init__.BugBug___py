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
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Types import ClassType, FuncDefinitionType, Type

    from ...Common.FuncParametersParserInfo import FuncParametersParserInfo

    from ...Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ....Error import Error, ErrorException

    if TYPE_CHECKING:
        from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo


# ----------------------------------------------------------------------
class TypeResolver(Interface.Interface):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EvalType(
        parser_info: ExpressionParserInfo,
    ) -> Type:
        raise Exception("Abstract method")  # pragma: no cover


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
        type_resolver: TypeResolver,
    ):
        errors: List[Error] = []

        # Process the return type
        return_type: Optional[Type] = None

        if func_parser_info.return_type is not None:
            try:
                return_type = type_resolver.EvalType(func_parser_info.return_type)
            except ErrorException as ex:
                errors += ex.errors

        # Process the parameters
        parameter_types: Optional[List[Type]] = None

        if isinstance(func_parser_info.parameters, FuncParametersParserInfo):
            parameter_types = []

            for parameter_parser_info in func_parser_info.parameters.EnumParameters():
                try:
                    parameter_types.append(type_resolver.EvalType(parameter_parser_info.type))
                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # TODO: Error when visibility of types/parameters < visibility of method

        return cls(return_type, parameter_types)

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass1(
        self,
        func_definition_type: FuncDefinitionType,
    ) -> None:
        assert False, "BugBug1"

        errors: List[Error] = []

        if self.return_type is not None:
            try:
                self.return_type.Finalize()
            except ErrorException as ex:
                errors += ex.errors

        for parameter_type in (self.parameters or []):
            try:
                parameter_type.Finalize()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def FinalizePass2(
        self,
        func_definition_type: FuncDefinitionType,
    ) -> None:
        assert False, "BugBug2"
