# ----------------------------------------------------------------------
# |
# |  NestedTypeExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-21 13:30:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NestedTypeExpressionParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, TranslationUnitRegion

    from .FuncOrTypeExpressionParserInfo import InvalidCompileTimeTypeError

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NestedTypeExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    types: List[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        types: List[ExpressionParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(*types),     # type: ignore
            regions,                                    # type: ignore
            types,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(NestedTypeExpressionParserInfo, self).__post_init__(
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "types",
                    ],
                },
            },
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptChildrenResultType:  # pylint: disable=protected-access
        yield "types", self.types  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_initialized_type: Optional[bool]=True,
    ) -> None:
        errors: List[Error] = []

        if parser_info_type.IsCompileTime():
            errors.append(
                InvalidCompileTimeTypeError.Create(
                    region=self.regions__.self__,
                ),
            )

        elif (
            parser_info_type == ParserInfoType.Standard
            or parser_info_type == ParserInfoType.Unknown
        ):
            for the_type in self.types:
                try:
                    the_type.InitializeAsType(
                        parser_info_type,
                        is_instantiated_type=is_initialized_type,
                    )
                except ErrorException as ex:
                    errors += ex.errors

        else:
            assert False, parser_info_type  # type: ignore

        if errors:
            raise ErrorException(*errors)
