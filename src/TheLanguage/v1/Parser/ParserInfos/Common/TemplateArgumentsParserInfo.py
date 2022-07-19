# ----------------------------------------------------------------------
# |
# |  TemplateArgumentsParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 09:28:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about a template argument"""

import os

from typing import Dict, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, TranslationUnitRegion

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException

    from ...Common import CallHelpers


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The keyword template argument '{name}' has already been provided",
    name=str,
    prev_region=TranslationUnitRegion,
)

InvalidTemplateTypeError                    = CreateError(
    "Template type arguments must be compile-time types",
)

InvalidTemplateExpressionError              = CreateError(
    "Template decorator arguments must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    type_or_expression: ExpressionParserInfo
    keyword: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TemplateArgumentParserInfo, self).__init__(
            ParserInfoType.TypeCustomization,
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "type_or_expression",
                    ],
                },
            },
        )

        # Validate
        errors: List[Error] = []

        try:
            if self.type_or_expression.IsType():
                self.type_or_expression.InitializeAsType(self.parser_info_type__)
            else:
                self.type_or_expression.InitializeAsExpression()

            if (
                not self.type_or_expression.is_compile_time__
                and self.type_or_expression.parser_info_type__ != ParserInfoType.Unknown
            ):
                errors.append(
                    InvalidTemplateTypeError.Create(
                        region=self.type_or_expression.regions__.self__,
                    ),
                )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "type_or_expression", self.type_or_expression  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateArgumentsParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    arguments: List[TemplateArgumentParserInfo]

    call_helpers_args: List[CallHelpers.ArgumentInfo]                       = field(init=False, default_factory=list)
    call_helpers_kwargs: Dict[str, CallHelpers.ArgumentInfo]                = field(init=False, default_factory=dict)

    # ----------------------------------------------------------------------
    # |  Public Methods
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, *args, **kwargs):
        super(TemplateArgumentsParserInfo, self).__init__(
            ParserInfoType.GetDominantType(*self.arguments),
            regions,
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "call_helpers_args",
                        "call_helpers_kwargs",
                    ],
                    "call_helpers_args": None,
                    "call_helpers_kwargs": None,
                },
            },
        )

        # Validate
        errors: List[Error] = []

        keyword_lookup: Dict[str, TemplateArgumentParserInfo] = {}

        for argument in self.arguments:
            if argument.keyword is not None:
                prev_argument = keyword_lookup.get(argument.keyword, None)
                if prev_argument is not None:
                    errors.append(
                        DuplicateNameError.Create(
                            region=argument.regions__.keyword,
                            name=argument.keyword,
                            prev_region=prev_argument.regions__.keyword,
                        ),
                    )
                else:
                    keyword_lookup[argument.keyword] = argument

        if errors:
            raise ErrorException(*errors)

        # Initialize the call helpers info
        call_helpers_args: List[CallHelpers.ArgumentInfo] = []
        call_helpers_kwargs: Dict[str, CallHelpers.ArgumentInfo] = {}

        for argument in self.arguments:
            if argument.keyword is None:
                call_helpers_args.append(
                    CallHelpers.ArgumentInfo(
                        argument.regions__.self__,
                        context=argument,
                    ),
                )
            else:
                call_helpers_kwargs[argument.keyword] = CallHelpers.ArgumentInfo(
                    argument.regions__.self__,
                    context=argument,
                )

        object.__setattr__(self, "call_helpers_args", call_helpers_args)
        object.__setattr__(self, "call_helpers_kwargs", call_helpers_kwargs)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "arguments", self.arguments  # type: ignore
