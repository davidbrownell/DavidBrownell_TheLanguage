# ----------------------------------------------------------------------
# |
# |  OrStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-25 15:28:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the OrStatement object"""

import asyncio
import os

from typing import Any, cast, List, Optional, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement


# ----------------------------------------------------------------------
class OrStatement(Statement):
    """Parsing attempts to match one of the provided statements"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *statements: Statement,
        sort_results=True,
        name: str=None,
        unique_id: Optional[List[Any]]=None,
    ):
        name = name or "Or: [{}]".format(", ".join([item.Name for item in statements]))

        super(OrStatement, self).__init__(
            name,
            unique_id=unique_id,
        )

        self.Statements                                                     = list(statements)
        self.SortResults                                                    = sort_results

        self._working_statements: Optional[List[Statement]]                  = None

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[Any],
    ) -> Statement:
        return self.__class__(
            *self.Statements,
            sort_results=self.SortResults,
            name=self.Name,
            unique_id=unique_id,
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
        if self._working_statements is None:
            self._working_statements = [
                statement.Clone(self.UniqueId + ["Or: {} [{}]".format(statement.Name, statement_index)])
                for statement_index, statement in enumerate(self.Statements)
            ]

        best_result: Optional[Statement.ParseResult] = None

        observer.StartStatement(self.UniqueId)
        with CallOnExit(lambda: observer.EndStatement(
                self.UniqueId,
                best_result is not None and best_result.Success,
            ),
        ):
            use_async = not single_threaded and len(self._working_statements) > 1

            # ----------------------------------------------------------------------
            async def ExecuteAsync(statement):
                return await statement.ParseAsync(
                    normalized_iter.Clone(),
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

            # ----------------------------------------------------------------------

            results: List[Statement.ParseResult] = []

            if use_async:
                gathered_results = await asyncio.gather(
                    *[
                        ExecuteAsync(statement)
                        for statement in self._working_statements
                    ],
                )

                if any(result is None for result in gathered_results):
                    return None

                results = cast(List[Statement.ParseResult], gathered_results)

            else:
                for statement in self._working_statements:
                    result = await ExecuteAsync(statement)
                    if result is None:
                        return None

                    results.append(result)

                    if not self.SortResults and result.Success:
                        break

            assert results

            best_index: Optional[int] = None

            if self.SortResults:
                # Stable sort according to the criteria:
                #   - Success
                #   - Longest matched content

                sort_data = [
                    (
                        index,
                        1 if result.Success else 0,
                        result.Iter.Offset,
                    )
                    for index, result in enumerate(results)
                ]

                sort_data.sort(
                    key=lambda value: value[1:],
                    reverse=True,
                )

                best_index = sort_data[0][0]

            else:
                for index, result in enumerate(results):
                    if result.Success:
                        best_index = index
                        break

                if best_index is None:
                    best_index = 0

            assert best_index is not None
            best_result = results[best_index]

            if best_result.Success:
                data = Statement.StandardParseResultData(
                    self._working_statements[best_index],
                    best_result.Data,
                )

                if not await observer.OnInternalStatementAsync(
                    self.UniqueId,
                    self,
                    data,
                    normalized_iter,
                    best_result.Iter,
                ):
                    return None

                return Statement.ParseResult(True, best_result.Iter, data)

            # Gather the failure information
            data_items: List[Statement.StandardParseResultData] = []
            max_iter: Optional[Statement.NormalizedIterator] = None

            for statement, result in zip(self._working_statements, results):
                assert not result.Success

                data_items.append(
                    Statement.StandardParseResultData(
                        statement,
                        result.Data,
                    ),
                )

                if max_iter is None or result.Iter.Offset > max_iter.Offset:
                    max_iter = result.Iter

            return Statement.ParseResult(
                False,
                cast(Statement.NormalizedIterator, max_iter),
                Statement.MultipleStandardParseResultData(data_items),
            )
