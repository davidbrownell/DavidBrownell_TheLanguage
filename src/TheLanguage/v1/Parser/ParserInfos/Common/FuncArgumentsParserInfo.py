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
        super(FuncArgumentParserInfo, self).__init__(
            ParserInfoType.Standard,
            regions,
            regionless_attributes=["expression", ],
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncArgumentsParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

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
    def __post_init__(self, regions):
        result = self.__class__._GetDominantExpressionType(*self.arguments)  # pylint: disable=protected-access

        if isinstance(result, list):
            raise ErrorException(*result)

        parser_info_type = result

        super(FuncArgumentsParserInfo, self).__init__(parser_info_type, regions)

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
