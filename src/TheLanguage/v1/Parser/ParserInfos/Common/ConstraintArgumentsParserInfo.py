# ----------------------------------------------------------------------
# |
# |  ConstraintArgumentsParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 10:15:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about a constraint argument"""

import os

from typing import Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

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
    "The constraint keyword argument '{name}' has already been provided",
    name=str,
    prev_region=Region,
)

InvalidConstraintExpressionError            = CreateError(
    "Constraint arguments must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintArgumentParserInfo(ParserInfo):
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
        super(ConstraintArgumentParserInfo, self).__init__(
            ParserInfoType.CompileTime,
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

        # Validate
        errors: List[Error] = []

        if self.expression.parser_info_type__.value > ParserInfoType.CompileTime.value:  # type: ignore
            errors.append(
                InvalidConstraintExpressionError.Create(
                    region=self.expression.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintArgumentsParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    arguments: List[ConstraintArgumentParserInfo]

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
        super(ConstraintArgumentsParserInfo, self).__init__(ParserInfoType.CompileTime, *args, **kwargs)

        # Validate
        errors: List[Error] = []

        keyword_lookup: Dict[str, ConstraintArgumentParserInfo] = {}

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
