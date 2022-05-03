# ----------------------------------------------------------------------
# |
# |  FuncArgumentsParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 13:21:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about a function argument"""

import os

from typing import Dict, List, Optional

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
    "The keyword argument '{name}' has already been provided",
    name=str,
    prev_region=Region,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncArgumentParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    expression: ExpressionParserInfo
    keyword: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls,
        *args,
        **kwargs,
    ):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncArgumentParserInfo, self).__init__(
            self.expression.parser_info_type__,  # type: ignore
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

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
class FuncArgumentsParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    arguments: List[FuncArgumentParserInfo]

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
        super(FuncArgumentsParserInfo, self).__init__(
            ParserInfoType.GetDominantType(*self.arguments),
            *args,
            **kwargs,
        )

        # Validate
        errors: List[Error] = []

        keyword_lookup: Dict[str, FuncArgumentParserInfo] = {}

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
