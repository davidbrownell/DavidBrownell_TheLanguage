# ----------------------------------------------------------------------
# |
# |  RepeatStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-25 16:17:23
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
import textwrap

from typing import Any, cast, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement


# ----------------------------------------------------------------------
class RepeatStatement(Statement):
    """Matches content that repeats the provided statement N times"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Statement,
        min_matches: int,
        max_matches: Optional[int],
        name: str=None,
        unique_id: Optional[List[Any]]=None,
        type_id: Optional[int]=None,
    ):
        assert statement
        assert min_matches >= 0, min_matches
        assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

        name = name or "Repeat: ({}, {}, {})".format(statement.Name, min_matches, max_matches)

        super(RepeatStatement, self).__init__(
            name,
            unique_id=unique_id,
            type_id=type_id,
        )

        self.Statement                      = statement
        self.MinMatches                     = min_matches
        self.MaxMatches                     = max_matches

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[Any],
    ):
        return self.__class__(
            self.Statement,
            self.MinMatches,
            self.MaxMatches,
            name=self.Name,
            unique_id=unique_id,
            type_id=self.TypeId,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        success = False

        observer.StartStatement([self])
        with CallOnExit(lambda: observer.EndStatement([(self, success)])):
            original_normalized_iter = normalized_iter.Clone()

            results: List[Statement.ParseResult] = []
            error_result: Optional[Statement.ParseResult] = None

            while not normalized_iter.AtEnd():
                statement = self.Statement.Clone(self.UniqueId + ["Rpt: {} [{}]".format(self.Statement.Name, len(results))])

                result = await statement.ParseAsync(
                    normalized_iter.Clone(),
                    Statement.ObserverDecorator(
                        self,
                        observer,
                        results,
                        lambda result: result.Data,
                    ),
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                if result is None:
                    return None

                if not result.Success:
                    error_result = result
                    break

                results.append(result)
                normalized_iter = result.Iter.Clone()

                if self.MaxMatches is not None and len(results) == self.MaxMatches:
                    break

            results = cast(List[Statement.ParseResult], results)

            success = (
                len(results) >= self.MinMatches
                and (
                    self.MaxMatches is None
                    or self.MaxMatches >= len(results)
                )
            )

            if success:
                data = Statement.StandardParseResultData(
                    self,
                    Statement.StandardParseResultData(
                        self.Statement,
                        Statement.MultipleStandardParseResultData(
                            [result.Data for result in results],
                            True,
                        ),
                    ),
                )

                if not await observer.OnInternalStatementAsync(
                    [data],
                    original_normalized_iter,
                    normalized_iter,
                ):
                    return None

                return Statement.ParseResult(True, normalized_iter, data)

            # Gather the failure information
            result_data = [result.Data for result in results]

            if error_result:
                result_data.append(error_result.Data)
                end_iter = error_result.Iter
            else:
                end_iter = normalized_iter

            return Statement.ParseResult(
                False,
                end_iter,
                Statement.StandardParseResultData(
                    self,
                    Statement.StandardParseResultData(
                        self.Statement,
                        Statement.MultipleStandardParseResultData(result_data, True),
                    ),
                ),
            )
