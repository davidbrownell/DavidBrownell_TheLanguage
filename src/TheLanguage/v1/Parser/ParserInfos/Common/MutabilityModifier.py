# ----------------------------------------------------------------------
# |
# |  MutabilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 12:26:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MutabilityModifier object"""

import os

from enum import auto, Enum

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType
    from ...Error import CreateError, ErrorException


# ----------------------------------------------------------------------
MutabilityModifierRequiredError             = CreateError(
    "A mutability modifier is required in this context",
)

MutabilityModifierNotAllowedError           = CreateError(
    "A mutability modifier is not allowed in this context",
)

InvalidCompileTimeMutabilityModifierError   = CreateError(
    "Compile-time types may not have a mutability modifier",
)

InvalidNewMutabilityModifierError           = CreateError(
    "The mutability modifier 'new' is not allowed in this context",
)

InvalidImmutableMutabilityModifierError     = CreateError(
    "The mutability modifier 'immutable' is not valid in this context",
)

InvalidMutableMutabilityModifierError       = CreateError(
    "The mutability modifier 'mutable' is not valid in this context",
)

InvalidClassAttributeMutabilityModifierError            = CreateError(
    "The mutability modifier '{modifier}' is not valid for class attributes; supported values are 'immutable', 'mutable'",
)


# ----------------------------------------------------------------------
class MutabilityModifier(Enum):
    #                                                     Mutable   Shared      Finalized   Notes
    #                                                     --------  ----------  ---------   -----------------
    var                                     = auto()    # Yes       No          No
    ref                                     = auto()    # Yes       Yes         No
    view                                    = auto()    # No        No          No
    val                                     = auto()    # No        Yes         Yes
    immutable                               = auto()    # No        Yes | No    Yes | No    view | val

    mutable                                 = auto()    # Only valid in the class attribute context

    new                                     = auto()    # Depends on associated Type; should only be used with method return values
                                                        # in concepts, interfaces, and mixins when the actual type is not known.

    # ----------------------------------------------------------------------
    @classmethod
    def Validate(
        cls,
        parser_info: ParserInfo,
        parser_info_type: ParserInfoType,
        is_instantiated_type: bool,
    ) -> None:
        modifier = parser_info.mutability_modifier  # type: ignore

        from v1.Parser.ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
        from v1.Parser.ParserInfos.Expressions.SelfReferenceExpressionParserInfo import SelfReferenceExpressionParserInfo
        from v1.Parser.ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
        from v1.Parser.ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo
        from v1.Parser.ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
        from v1.Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo

        assert isinstance(
            parser_info,
            (
                FuncOrTypeExpressionParserInfo,
                SelfReferenceExpressionParserInfo,
                TupleExpressionParserInfo,
                VariantExpressionParserInfo,
                ClassAttributeStatementParserInfo,
                FuncDefinitionStatementParserInfo,
            )
        ), parser_info

        if parser_info_type.IsCompileTime():
            if modifier is not None:
                raise ErrorException(
                    InvalidCompileTimeMutabilityModifierError.Create(
                        region=parser_info.regions__.mutability_modifier,
                    ),
                )
        else:
            if is_instantiated_type and modifier is None:
                raise ErrorException(
                    MutabilityModifierRequiredError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )
            elif not is_instantiated_type and modifier is not None:
                raise ErrorException(
                    MutabilityModifierNotAllowedError.Create(
                        region=parser_info.regions__.mutability_modifier,
                    ),
                )

        if isinstance(parser_info, ClassAttributeStatementParserInfo):
            if (
                parser_info.mutability_modifier is not None
                and parser_info.mutability_modifier != cls.immutable
                and parser_info.mutability_modifier != cls.mutable
            ):
                raise ErrorException(
                    InvalidClassAttributeMutabilityModifierError.Create(
                        region=parser_info.regions__.mutability_modifier,
                        modifier=parser_info.mutability_modifier,
                    ),
                )

        # TODO: 'new' is valid only as return value and with concepts or self ref types
        # TODO: 'immutable' is valid with return values, parameters, class attributes

        if (
            modifier == cls.mutable
            and not isinstance(parser_info, ClassAttributeStatementParserInfo)
        ):
            raise ErrorException(
                InvalidMutableMutabilityModifierError.Create(
                    region=parser_info.regions__.mutability_modifier,
                ),
            )

        if (
            modifier == cls.new
            and not isinstance(parser_info, (FuncOrTypeExpressionParserInfo, SelfReferenceExpressionParserInfo))
        ):
            raise ErrorException(
                InvalidNewMutabilityModifierError.Create(
                    region=parser_info.regions__.mutability_modifier,
                ),
            )

    # ----------------------------------------------------------------------
    def IsMutable(self) -> bool:
        return (
            self == MutabilityModifier.var
            or self == MutabilityModifier.ref
            or self == MutabilityModifier.mutable
        )

    # ----------------------------------------------------------------------
    def IsImmutable(self) -> bool:
        return not self.IsMutable()
