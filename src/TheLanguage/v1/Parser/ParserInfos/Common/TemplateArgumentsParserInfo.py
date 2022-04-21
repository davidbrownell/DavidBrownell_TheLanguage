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

from typing import Dict, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, Region

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo

    from ...Error import CreateError, Error, ErrorException

# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The keyword template argument '{name}' has already been provided",
    name=str,
    prev_region=Region,
)

InvalidTemplateExpressionError              = CreateError(
    "Template decorator arguments must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    regions: InitVar[List[Optional[Region]]]

    type: TypeParserInfo
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
    def __post_init__(self, regions):
        super(TemplateTypeArgumentParserInfo, self).__init__(
            ParserInfoType.CompileTime,
            regions,
            regionless_attributes=["type", ],
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    regions: InitVar[List[Optional[Region]]]

    expression: ExpressionParserInfo
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
    def __post_init__(self, regions):
        super(TemplateDecoratorArgumentParserInfo, self).__init__(
            ParserInfoType.CompileTime,
            regions,
            regionless_attributes=["expression", ],
        )

        # Validate
        errors: List[Error] = []

        if self.expression.parser_info_type__.value > ParserInfoType.CompileTime.value:  # type: ignore
            errors.append(
                InvalidTemplateExpressionError.Create(
                    region=self.expression.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateArgumentsParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    # |  Public Types
    ArgumentType                            = Union[
        TemplateTypeArgumentParserInfo,
        TemplateDecoratorArgumentParserInfo,
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    parser_info_type__: ParserInfoType      = field(init=False)

    regions: InitVar[List[Optional[Region]]]

    arguments: List["TemplateArgumentsParserInfo.ArgumentType"]

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
    def __post_init__(self, regions):
        super(TemplateArgumentsParserInfo, self).__init__(ParserInfoType.CompileTime, regions)

        # Validate
        errors: List[Error] = []

        keyword_lookup: Dict[str, TemplateArgumentsParserInfo.ArgumentType] = {}

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
