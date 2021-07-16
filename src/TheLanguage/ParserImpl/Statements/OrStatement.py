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

from typing import cast, Iterable, List, Optional, Union

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
        unique_id: Optional[List[str]]=None,
        type_id: Optional[int]=None,
        _name_is_default: Optional[bool]=None,
    ):
        assert statements
        assert all(statement for statement in statements)

        if name is None:
            name = self._CreateDefaultName(statements)
            _name_is_default = True
        elif _name_is_default is None:
            _name_is_default = False

        super(OrStatement, self).__init__(
            name,
            unique_id=unique_id,
            type_id=type_id,
        )

        cloned_statements = [
            statement.Clone(
                unique_id=self.UniqueId + ["Or: {} [{}]".format(statement.Name, statement_index)],
            )
            for statement_index, statement in enumerate(statements)
        ]

        self.Statements                     = cloned_statements
        self.SortResults                    = sort_results
        self._original_statements           = statements
        self._name_is_default               = _name_is_default

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[str],
    ) -> Statement:
        return self.CloneImpl(
            *self._original_statements,
            sort_results=self.SortResults,
            name=self.Name,
            unique_id=unique_id,
            type_id=self.TypeId,
            _name_is_default=self._name_is_default,
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
        best_result: Optional[Statement.ParseResult] = None

        observer.StartStatement([self])
        with CallOnExit(lambda: observer.EndStatement(
                [
                    (
                        self,
                        best_result is not None and best_result.Success,
                    ),
                ],
            ),
        ):
            results: List[Statement.ParseResult] = []

            observer_decorator = Statement.ObserverDecorator(
                self,
                observer,
                results,
                lambda result: result.Data,
            )

            # ----------------------------------------------------------------------
            async def ExecuteAsync(statement):
                return await statement.ParseAsync(
                    normalized_iter.Clone(),
                    observer_decorator,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

            # ----------------------------------------------------------------------

            use_async = not single_threaded and len(self.Statements) > 1

            if use_async:
                gathered_results = await asyncio.gather(
                    *[
                        ExecuteAsync(statement)
                        for statement in self.Statements
                    ],
                )

                if any(result is None for result in gathered_results):
                    return None

                results = cast(List[Statement.ParseResult], gathered_results)

            else:
                for statement in self.Statements:
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
                    self,
                    best_result.Data,
                )

                if not await observer.OnInternalStatementAsync(
                    [data],
                    normalized_iter,
                    best_result.Iter,
                ):
                    return None

                return Statement.ParseResult(True, best_result.Iter, data)

            # Gather the failure information
            data_items: List[Optional[Statement.StandardParseResultData]] = []
            max_iter: Optional[Statement.NormalizedIterator] = None

            for result in results:
                assert not result.Success

                data_items.append(result.Data)

                if max_iter is None or result.Iter.Offset > max_iter.Offset:
                    max_iter = result.Iter

            assert max_iter

            return Statement.ParseResult(
                False,
                max_iter,
                Statement.StandardParseResultData(
                    self,
                    Statement.MultipleStandardParseResultData(cast(List[Optional[Statement.ParseResultData]], data_items), True),
                ),
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    ) -> bool:
        updated_statements = False

        for statement_index, statement in enumerate(self.Statements):
            if isinstance(statement, RecursivePlaceholderStatement):
                self.Statements[statement_index] = new_statement
                updated_statements = True
            else:
                updated_statements = statement.PopulateRecursiveImpl(new_statement) or updated_statements

        if updated_statements and self._name_is_default:
            self.Name = self._CreateDefaultName(self.Statements)

        return updated_statements

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        statements: Iterable[Statement],
    ) -> str:
        return "Or: {{{}}}".format(", ".join([statement.Name for statement in statements]))
