# ----------------------------------------------------------------------
# |
# |  RepeatStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-15 18:16:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RepeatStatement object"""

import os

from typing import cast, List, Optional

from rop import read_only_properties

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .Statement import Statement


# ----------------------------------------------------------------------
@read_only_properties(
    "Statement",
    "MinMatches",
    "MaxMatches",
)
class RepeatStatement(Statement):
    """Statement that matches the contained statements N times."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Statement,
        min_matches: int,
        max_matches: Optional[int],
    ):
        assert statement
        assert min_matches >= 0, min_matches
        assert max_matches is None or (max_matches >= min_matches), (min_matches, max_matches)

        self.Statement                      = statement
        self.MinMatches                     = min_matches
        self.MaxMatches                     = max_matches

    # ----------------------------------------------------------------------
    @property
    def IsOptional(self):
        return self.MinMatches == 0 and self.MaxMatches == 1

    @property
    def IsOneOrMore(self):
        return self.MinMatches == 1 and self.MaxMatches is None

    @property
    def IsZeroOrMore(self):
        return self.MinMatches == 0 and self.MaxMatches is None

    @property
    def IsCollection(self):
        return self.MaxMatches is None or self.MaxMatches > 1

    # ----------------------------------------------------------------------
    @Interface.override
    def Parse(
        self,
        normalized_iter: NormalizedIterator,
        observer: Statement.Observer,
    ) -> Optional[Statement.ParseResult]:
        results: List[Statement.StatementParseResultItem] = []

        while True:
            result = self.Statement.Parse(normalized_iter, observer)
            if not result.Success:
                break

            results.append(
                Statement.StatementParseResultItem(
                    self.Statement,
                    result.Results,
                ),
            )

            normalized_iter = result.Iter.Clone()

            if self.MaxMatches is not None and len(results) == self.MaxMatches:
                break

        if self.IsOptional:
            success = len(results) in [0, 1]
        else:
            success = (
                len(results) >= self.MinMatches
                and (
                    self.MaxMatches is None
                    or len(results) == self.MaxMatches
                )
            )

        return Statement.ParseResult(
            success,
            cast(Statement.ParseResultItemsType, results),
            normalized_iter,
        )
