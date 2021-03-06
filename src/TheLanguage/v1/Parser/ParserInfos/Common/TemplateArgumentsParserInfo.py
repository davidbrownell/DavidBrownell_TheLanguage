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

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, Region

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException

# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The keyword template argument '{name}' has already been provided",
    name=str,
    prev_region=Region,
)

InvalidTemplateTypeError                    = CreateError(
    "Template type arguments must be compile-time types",
)

InvalidTemplateExpressionError              = CreateError(
    "Template decorator arguments must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    type: ExpressionParserInfo
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
        super(TemplateTypeArgumentParserInfo, self).__init__(
            ParserInfoType.TypeCustomization,
            *args,
            **kwargs,
            regionless_attributes=["type", ],
        )

        # Validate
        errors: List[Error] = []

        try:
            self.type.ValidateAsType(self.parser_info_type__)

            if self.type.parser_info_type__ != self.parser_info_type__:
                errors.append(
                    InvalidTemplateTypeError(
                        region=self.type.regions__.self__,
                    ),
                )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("type", self.type),
            ],
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
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
    def __post_init__(self, *args, **kwargs):
        expression_parser_info_type = self.expression.parser_info_type__

        super(TemplateDecoratorArgumentParserInfo, self).__init__(
            expression_parser_info_type,
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

        # Validate
        errors: List[Error] = []

        try:
            self.expression.ValidateAsExpression()

            if not ParserInfoType.IsCompileTime(expression_parser_info_type):
                errors.append(
                    InvalidTemplateExpressionError.Create(
                        region=self.expression.regions__.self__,
                    ),
                )
        except ErrorException as ex:
            errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("expression", self.expression),
            ],
            children=None,
        )


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
    def __post_init__(self, regions, *args, **kwargs):
        super(TemplateArgumentsParserInfo, self).__init__(
            ParserInfoType.GetDominantType(*self.arguments),
            regions,
            *args,
            **kwargs,
        )

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

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("arguments", self.arguments),
            ],  # type: ignore
            children=None,
        )
