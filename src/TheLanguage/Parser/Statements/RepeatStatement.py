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

from typing import cast, List, Optional, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .RecursivePlaceholderStatement import RecursivePlaceholderStatement
    from ..Components.Statement import Statement


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
        _name_is_default: Optional[bool]=None,
    ):
        assert statement
        assert min_matches >= 0, min_matches
        assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

        if name is None:
            name = self._CreateDefaultName(statement, min_matches, max_matches)
            _name_is_default = True
        elif _name_is_default is None:
            _name_is_default = False

        super(RepeatStatement, self).__init__(name)

        self.Statement                      = statement
        self.MinMatches                     = min_matches
        self.MaxMatches                     = max_matches
        self._name_is_default               = _name_is_default

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        unique_id: List[str],
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        success = False

        observer.StartStatement(unique_id, [self])
        with CallOnExit(lambda: observer.EndStatement(unique_id, [(self, success)])):
            original_normalized_iter = normalized_iter.Clone()

            results: List[Statement.ParseResult] = []
            error_result: Optional[Statement.ParseResult] = None

            while not normalized_iter.AtEnd():
                result = await self.Statement.ParseAsync(
                    unique_id + ["Repeat: {} [{}]".format(self.Statement.Name, len(results))],
                    normalized_iter.Clone(),
                    Statement.ObserverDecorator(
                        self,
                        unique_id,
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
                    Statement.MultipleStandardParseResultData(
                        [result.Data for result in results],
                        True,
                    ),
                    unique_id,
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
                    Statement.MultipleStandardParseResultData(cast(List[Optional[Statement.ParseResultData]], result_data), True),
                    unique_id,
                ),
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    ) -> bool:
        replaced_statement = False

        if isinstance(self.Statement, RecursivePlaceholderStatement):
            self.Statement = new_statement
            replaced_statement = True

        else:
            replaced_statement = self.Statement.PopulateRecursiveImpl(new_statement) or replaced_statement

        if replaced_statement and self._name_is_default:
            self.Name = self._CreateDefaultName(self.Statement, self.MinMatches, self.MaxMatches)

        return replaced_statement

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        statement: Statement,
        min_matches: int,
        max_matches: Optional[int],
    ) -> str:
        return "Repeat: ({}, {}, {})".format(statement.Name, min_matches, max_matches)
