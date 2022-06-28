# ----------------------------------------------------------------------
# |
# |  ExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 08:28:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExpressionParserInfo object"""

import os

from typing import Any, Callable, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import ComparisonOperators
from CommonEnvironment.DoesNotExist import DoesNotExist
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, TranslationUnitRegion
    from ...Error import CreateError, ErrorException

    from ...MiniLanguage.Expressions.Expression import Expression as MiniLanguageExpression

    from ...MiniLanguage.Types.NoneType import NoneType as MiniLanguageNoneType
    from ...MiniLanguage.Types.Type import Type as MiniLanguageType


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "Expression is not a type",
)

InvalidExpressionError                      = CreateError(
    "Type is not an expression",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ExpressionParserInfo(ParserInfo):
    """Abstract base class for all expressions"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class ResolvedType(ObjectReprImplBase):
        # ----------------------------------------------------------------------
        parser_info: ParserInfo

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            ObjectReprImplBase.__init__(
                self,
                parser_info=lambda value: value.__class__.__name__,
            )

        # ----------------------------------------------------------------------
        @Interface.extensionmethod
        def ResolveOne(self) -> "ExpressionParserInfo.ResolvedType":
            return self

        # ----------------------------------------------------------------------
        @Interface.extensionmethod
        def Resolve(self) -> "ExpressionParserInfo.ResolvedType":
            return self

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    _resolved_entity: Union[
        DoesNotExist,

        # Type Values
        MiniLanguageType,                   # Compile-time
        None,                               # Standard

        # Expression Values
        MiniLanguageExpression.EvalResult,  # Compile-time
        ResolvedType,                       # Standard

    ]                                       = field(init=False, default=DoesNotExist.instance)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        super(ExpressionParserInfo, self).__init__(
            parser_info_type,
            regions,
            regionless_attributes,
            validate,
            **{
                **{
                    "resolved_type__": None,
                    "resolved_mini_language_type__": None,
                    "resolved_mini_language_expression_result__": None,
                },
                **custom_display_funcs,
            },
        )

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsType(self) -> Optional[bool]:
        # Most expressions are not types.
        return False

    # ----------------------------------------------------------------------
    def InitializeAsType(
        self,
        parser_info_type: ParserInfoType,               # pylint: disable=unused-argument
        *,
        is_instantiated_type: Optional[bool]=True,      # pylint: disable=unused-argument
    ) -> None:
        is_type_result = self.IsType()

        if is_type_result is False:
            raise ErrorException(
                InvalidTypeError.Create(
                    region=self.regions__.self__,
                ),
            )

        if is_type_result is True:
            self._InitializeAsTypeImpl(
                parser_info_type,
                is_instantiated_type=is_instantiated_type,
            )

    # ----------------------------------------------------------------------
    def InitializeAsExpression(self) -> None:
        is_type_result = self.IsType()

        if is_type_result is True:
            raise ErrorException(
                InvalidExpressionError.Create(
                    region=self.regions__.self__,
                ),
            )

        if is_type_result is False:
            self._InitializeAsExpressionImpl()

    # ----------------------------------------------------------------------
    def SetResolvedEntity(
        self,
        resolved_entity: Union[
            MiniLanguageType,
            None,
            MiniLanguageExpression.EvalResult,
            ResolvedType,
        ],
    ) -> None:
        if self._resolved_entity is not DoesNotExist.instance:
            # None is ambiguous, as it can be used as both a type and an expression
            # and at both compile-time and standard. Allow the caller to do this if
            # the original value is None-like and they are moving towards something
            # that is None-like.

            assert (
                # Moving from compile-time expression to type
                (
                    self.is_compile_time__
                    and isinstance(self._resolved_entity, MiniLanguageExpression.EvalResult)
                    and isinstance(self._resolved_entity.type, MiniLanguageNoneType)
                    and isinstance(resolved_entity, MiniLanguageNoneType)
                )
            ), (self._resolved_entity, resolved_entity)

        object.__setattr__(self, "_resolved_entity", resolved_entity)

    # ----------------------------------------------------------------------
    def HasResolvedEntity(self) -> bool:
        return self._resolved_entity is not DoesNotExist.instance

    # ----------------------------------------------------------------------
    def ResolvedEntityIsNone(self) -> bool:
        return self._resolved_entity is None

    # ----------------------------------------------------------------------
    @property
    def resolved_type__(self) -> "ResolvedType":
        assert isinstance(self._resolved_entity, ExpressionParserInfo.ResolvedType), self._resolved_entity
        return self._resolved_entity

    @property
    def resolved_mini_language_type__(self) -> MiniLanguageType:
        assert isinstance(self._resolved_entity, MiniLanguageType), self._resolved_entity
        return self._resolved_entity

    @property
    def resolved_mini_language_expression_result__(self) -> MiniLanguageExpression.EvalResult:
        assert isinstance(self._resolved_entity, MiniLanguageExpression.EvalResult), self._resolved_entity
        return self._resolved_entity

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        # Nothing to do here by default
        pass

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _InitializeAsExpressionImpl(self) -> None:
        # Nothing to do here by default
        pass
