# ----------------------------------------------------------------------
# |
# |  DynamicStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-25 18:07:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DynamicStatement object"""

import os

from typing import Any, Callable, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .OrStatement import OrStatement
    from .Statement import Statement


# ----------------------------------------------------------------------
class DynamicStatement(Statement):
    """Collects dynamic statements and parses them"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        get_dynamic_statements_func: Callable[
            [
                List[Any],
                Statement.Observer,
            ],
            Union[
                Tuple[str, List[Statement]],
                List[Statement],
            ]
        ],
        name: str=None,
        unique_id: Optional[List[Any]]=None,
        type_id: Optional[int]=None,
    ):
        assert get_dynamic_statements_func

        name = name or "Dynamic Statements"

        super(DynamicStatement, self).__init__(
            name,
            unique_id=unique_id,
            type_id=type_id,
        )

        self._get_dynamic_statements_func   = get_dynamic_statements_func

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[Any],
    ):
        return self.__class__(
            self._get_dynamic_statements_func,
            name=self.Name,
            unique_id=unique_id,
            type_id=self.TypeId,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def PopulateRecursive(
        self,
        new_statement: Statement,
        type_to_replace: Any,
    ):
        # Nothing to do here
        pass

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
        result: Optional[Statement.ParseResult] = None

        observer.StartStatement([self])
        with CallOnExit(
            lambda: observer.EndStatement(
                [
                    (
                        self,
                        result is not None and result.Success,
                    ),
                ],
            ),
        ):
            dynamic_statements = self._get_dynamic_statements_func(self.UniqueId, observer)
            if isinstance(dynamic_statements, tuple):
                name = dynamic_statements[0]
                dynamic_statements = dynamic_statements[1]
            else:
                name = None

            # Use the logic in the OrStatement constructor to create a pretty name; then use that
            # name when creating the unique_id when cloning the new OrStatement.
            or_statement = OrStatement(
                *dynamic_statements,
                name=name,
            )

            or_statement = or_statement.Clone(self.UniqueId + [or_statement.Name])

            result = await or_statement.ParseAsync(
                normalized_iter,
                Statement.ObserverDecorator(
                    self,
                    observer,
                    [result],
                    lambda result: result.Data,
                ),
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            data = Statement.StandardParseResultData(self, result.Data)

            if (
                result.Success
                and not await observer.OnInternalStatementAsync(
                    [data],
                    normalized_iter,
                    result.Iter,
                )
            ):
                return None

            return Statement.ParseResult(result.Success, result.Iter, data)
