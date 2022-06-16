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

from typing import Any, Callable, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
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
        parser_info: ParserInfo
        translation_unit_region: TranslationUnitRegion

        # ----------------------------------------------------------------------
        def __post_init__(self):
            ObjectReprImplBase.__init__(
                self,
                parser_info=lambda value: value.__class__.__name__,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

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
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsType(self) -> Optional[bool]:
        # Most expressions are not types.
        return False

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def InitializeAsType(
        self,
        parser_info_type: ParserInfoType,               # pylint: disable=unused-argument
        *,
        is_instantiated_type: Optional[bool]=True,      # pylint: disable=unused-argument
    ) -> None:
        # Most expressions are not types.

        raise ErrorException(
            InvalidTypeError.Create(
                region=self.regions__.self__,
            ),
        )

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def InitializeAsExpression(self) -> None:
        # Most expressions are expressions
        pass
