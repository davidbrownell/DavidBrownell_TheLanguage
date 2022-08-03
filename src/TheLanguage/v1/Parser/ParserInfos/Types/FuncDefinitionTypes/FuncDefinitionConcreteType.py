# ----------------------------------------------------------------------
# |
# |  FuncDefinitionConcreteType.py
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

from typing import Callable, List, Optional, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .FuncDefinitionConstrainedType import FuncDefinitionConstrainedType

    from ..ConcreteType import ConcreteType
    from ..ConstrainedType import ConstrainedType
    from ..TypeResolver import TypeResolver

    from ...Common.MutabilityModifier import MutabilityModifier
    from ...Common.FuncParametersParserInfo import FuncParameterParserInfo

    from ...Expressions.FuncOrTypeExpressionParserInfo import ExpressionParserInfo, FuncOrTypeExpressionParserInfo
    from ...Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo

    from ....Error import CreateError, Error, ErrorException
    from ....TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
MismatchedParameterNameError                = CreateError(
    "The parameter name '{this_name}' does not match the parameter name '{that_name}'",
    this_name=str,
    that_name=str,
    that_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class FuncDefinitionConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        super(FuncDefinitionConcreteType, self).__init__(
            parser_info,
            is_default_initializable=True,
        )

        errors: List[Error] = []

        # Return type
        return_type_info: Optional[Tuple[ConcreteType, Optional[MutabilityModifier]]] = None

        if parser_info.return_type is not None:
            try:
                return_type_info = type_resolver.EvalConcreteType(parser_info.return_type)
            except ErrorException as ex:
                errors += ex.errors

        # Parameters
        parameter_infos: Optional[List[Tuple[ConcreteType, Optional[MutabilityModifier]]]] = None

        if not isinstance(parser_info.parameters, bool):
            parameter_infos = []

            for parameter in parser_info.parameters.EnumParameters():
                try:
                    parameter_infos.append(type_resolver.EvalConcreteType(parameter.type))
                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        self._type_resolver                 = type_resolver

        self.return_type_info               = return_type_info
        self.parameter_infos                = parameter_infos

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> FuncDefinitionStatementParserInfo:
        assert isinstance(self._parser_info, FuncDefinitionStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsMatch(
        self,
        other: ConcreteType,
    ) -> bool:
        return self._MatchImpl(
            other,
            lambda this, that: this.IsMatch(that),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: ConcreteType,
    ) -> bool:
        return self._MatchImpl(
            other,
            lambda this, that: this.IsCovariant(that),
        )

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
    def _CreateConstrainedTypeImpl(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> ConstrainedType:
        assert isinstance(expression_parser_info, FuncOrTypeExpressionParserInfo), expression_parser_info
        assert expression_parser_info.constraints is None

        return self._CreateDefaultConstrainedTypeImpl()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConstrainedTypeImpl(self) -> ConstrainedType:
        return FuncDefinitionConstrainedType(self)

    # ----------------------------------------------------------------------
    def _FinalizeImpl(
        self,
        finalize_func: Callable[[ConcreteType], None],
    ) -> None:
        errors: List[Error] = []

        if self.return_type_info is not None:
            try:
                finalize_func(self.return_type_info[0])
            except ErrorException as ex:
                errors += ex.errors

        for concrete_parameter in (self.parameter_infos or []):
            try:
                finalize_func(concrete_parameter[0])
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    def _MatchImpl(
        self,
        other: ConcreteType,
        match_func: Callable[[ConcreteType, ConcreteType], bool],
    ) -> bool:
        if not isinstance(other, FuncDefinitionConcreteType):
            return False

        if self.parser_info.id != other.parser_info.id:
            return False

        # Return Type
        if self.return_type_info is not None or other.return_type_info is not None:
            if self.return_type_info is None or other.return_type_info is None:
                return False

            if self.return_type_info[1] != other.return_type_info[1]:
                return False

            if not match_func(self.return_type_info[0], other.return_type_info[0]):
                return False

        # Parameters
        if self.parameter_infos is not None or other.parameter_infos is not None:
            if self.parameter_infos is None or other.parameter_infos is None:
                return False

            assert not isinstance(self.parser_info.parameters, bool)
            assert not isinstance(other.parser_info.parameters, bool)

            this_parameter_info_iter = iter(self.parameter_infos)
            that_parameter_info_iter = iter(other.parameter_infos)

            name_mismatches: List[Tuple[FuncParameterParserInfo, FuncParameterParserInfo]] = []

            for attribute_name, require_name_match in [
                ("positional", False),
                ("any", True),
                ("keyword", True),
            ]:
                this_parser_infos = getattr(self.parser_info.parameters, attribute_name) or []
                that_parser_infos = getattr(other.parser_info.parameters, attribute_name) or []

                if len(this_parser_infos) != len(that_parser_infos):
                    return False

                if require_name_match:
                    # ----------------------------------------------------------------------
                    def OnNameMismatch(
                        this_parser_info: FuncParameterParserInfo,
                        that_parser_info: FuncParameterParserInfo,
                    ):
                        name_mismatches.append((this_parser_info, that_parser_info))

                    # ----------------------------------------------------------------------

                    on_name_mismatch_func = OnNameMismatch
                else:
                    on_name_mismatch_func = lambda *args: None

                for this_parser_info, that_parser_info in zip(this_parser_infos, that_parser_infos):
                    if this_parser_info.name != that_parser_info.name:
                        on_name_mismatch_func(this_parser_info, that_parser_info)

                    this_parameter_info = next(this_parameter_info_iter)
                    that_parameter_info = next(that_parameter_info_iter)

                    if this_parameter_info[1] != that_parameter_info[1]:
                        return False

                    if not match_func(this_parameter_info[0], that_parameter_info[0]):
                        return False

                # If here, all the types match. If we have name mismatches, raise an error as this
                # is a programming error (names need to be consistent because they can be used when
                # invoking the function).
                if name_mismatches:
                    raise ErrorException(
                        *[
                            MismatchedParameterNameError.Create(
                                region=this_parameter.regions__.name,
                                this_name=this_parameter.name,
                                that_name=that_parameter.name,
                                that_region=that_parameter.regions__.name,
                            )
                            for this_parameter, that_parameter in name_mismatches
                        ],
                    )

        return True
