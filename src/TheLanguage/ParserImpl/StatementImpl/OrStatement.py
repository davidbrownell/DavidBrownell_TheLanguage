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
        *items: Statement,
        name: str=None,
        sort_results=True,
    ):
        name = name or "Or [{}]".format(", ".join([item.Name for item in items]))

        super(OrStatement, self).__init__(name)

        self.Items                          = list(items)
        self.SortResults                    = sort_results

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
        statement_unique_id: List[Any] = [self.Name]

        observer.StartStatementCandidate(statement_unique_id)
        with CallOnExit(lambda: observer.EndStatementCandidate(statement_unique_id)):
            use_async = not single_threaded and len(self.Items) > 1

            # ----------------------------------------------------------------------
            async def ExecuteAsync(statement_index, statement):
                return await statement.ParseAsync(
                    normalized_iter.Clone(),
                    Statement.SimpleObserverDecorator(statement_unique_id + [statement_index], observer),
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

            # ----------------------------------------------------------------------

            results: List[Statement.ParseResult] = []

            if use_async:
                gathered_results = await asyncio.gather(
                    *[
                        ExecuteAsync(statement_index, statement)
                        for statement_index, statement in enumerate(self.Items)
                    ],
                )

                if any(result is None for result in gathered_results):
                    return None

                results = cast(List[Statement.ParseResult], gathered_results)

            else:
                for statement_index, statement in enumerate(self.Items):
                    result = await ExecuteAsync(statement_index, statement)
                    if result is None:
                        return result

                    results.append(result)

                    if not self.SortResults and result.Success:
                        break

            assert results

            best_index = None

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

            best_result = results[best_index]

            if best_result.Success:
                data = Statement.StandardParseResultData(
                    self.Items[best_index],
                    best_result.Data,
                )

                if not await observer.OnInternalStatementAsync(
                    statement_unique_id,
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

            for statement, result in zip(self.Items, results):
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
