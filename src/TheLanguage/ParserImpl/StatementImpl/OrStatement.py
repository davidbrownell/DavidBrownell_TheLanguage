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

import os

from typing import cast, Generator, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
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
    def Parse(
        self,
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        use_futures = not single_threaded and len(self.Items) > 1

        queue_command_observers: List[Statement.QueueCommandObserver] = []

        # ----------------------------------------------------------------------
        def Parse(statement):
            queue_command_observers.append(Statement.QueueCommandObserver(observer))

            return statement.Parse(
                normalized_iter.Clone(),
                queue_command_observers[-1],
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

        # ----------------------------------------------------------------------

        results: List[Statement.ParseResult] = []

        if use_futures:
            futures = observer.Enqueue(
                [
                    lambda statement=statement: Parse(statement)
                    for statement in self.Items
                ],
            )

            for future in futures:
                result = future.result()
                if result is None:
                    return result

                results.append(result)

        else:
            for statement in self.Items:
                result = Parse(statement)
                if result is None:
                    return result

                results.append(result)

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
            best_observer = queue_command_observers[best_index]
            best_statement = self.Items[best_index]

            result = best_observer.Replay()
            assert result, "This should always be True as it is a result from Statement.QueueCommandObserver"

            if not observer.OnInternalStatement(
                best_statement,
                best_result.Data,
                normalized_iter,
                best_result.Iter,
            ):
                return None

            return Statement.ParseResult(
                True,
                best_result.Iter,
                Statement.StandardParseResultData(
                    best_statement,
                    best_result.Data,
                ),
            )

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
