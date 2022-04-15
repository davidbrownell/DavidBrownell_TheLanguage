# ----------------------------------------------------------------------
# |
# |  ConstraintArgumentsPhrase.py
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
    from ..Error import CreateError, Error, ErrorException
    from ..Phrase import Phrase, Region

    from ..ConstraintExpressions.ConstraintExpressionPhrase import ConstraintExpressionPhrase


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The constraint keyword argument '{name}' has already been provided",
    name=str,
    prev_region=Region,
)


# ----------------------------------------------------------------------
class ConstraintArgumentPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    expression: ConstraintExpressionPhrase
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
        super(ConstraintArgumentPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintArgumentsPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    arguments: List[ConstraintArgumentPhrase]

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
        super(ConstraintArgumentsPhrase, self).__init__(regions)

        # Validate
        errors: List[Error] = []

        keyword_lookup: Dict[str, ConstraintArgumentPhrase] = {}

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
