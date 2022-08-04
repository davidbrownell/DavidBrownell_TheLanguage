# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 11:53:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassAttributeStatementParserInfo object"""

import os

from typing import Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, ParserInfoType, ScopeFlag, StatementParserInfo, TranslationUnitRegion

    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Traits.NamedTrait import NamedTrait

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassAttributeStatementParserInfo(
    NamedTrait,
    StatementParserInfo,
):
    """Attribute of a class"""

    # ----------------------------------------------------------------------
    class_capabilities: ClassCapabilities

    type: ExpressionParserInfo

    documentation: Optional[str]

    initialized_value: Optional[ExpressionParserInfo]

    keyword_initialization: Optional[bool]
    no_initialization: Optional[bool]
    no_serialize: Optional[bool]
    no_compare: Optional[bool]

    # TODO: If 'is_override', but be covariant

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            **{
                **{
                    **NamedTrait.ObjectReprImplBaseInitKwargs(),
                    **{
                        "class_capabilities": lambda value: value.name,
                    },
                },
                **{
                    "regionless_attributes": [
                        "class_capabilities",
                        "type",
                        "initialized_value",
                    ]
                        + NamedTrait.RegionlessAttributesArgs()
                    ,
                    "finalize": False,
                },
            },
        )

        # Set defaults
        if visibility_param is None and self.class_capabilities.default_attribute_visibility is not None:
            visibility_param = self.class_capabilities.default_attribute_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self._Finalize()

        # Validate
        errors: List[Error] = []

        for func in [
            lambda: self.class_capabilities.ValidateClassAttributeStatementCapabilities(self),
            lambda: self.type.InitializeAsType(self.parser_info_type__),
            self.initialized_value.InitializeAsExpression if self.initialized_value is not None else lambda: None,
        ]:
            try:
                func()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Standard: ScopeFlag.Class,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:  # pylint: disable=unused-argument
        return False

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "type", self.type

        if self.initialized_value is not None:
            yield "initialized_value", self.initialized_value
