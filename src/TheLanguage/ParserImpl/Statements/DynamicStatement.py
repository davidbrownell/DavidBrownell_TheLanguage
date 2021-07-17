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

from typing import Callable, List, Optional, Tuple, Union

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
                List[str],
                Statement.Observer,
            ],
            Union[
                List[Statement],
                Tuple[str, List[Statement]],
            ]
        ],
        name: str=None,
    ):
        assert get_dynamic_statements_func

        name = name or "Dynamic Statements"

        super(DynamicStatement, self).__init__(name)

        self._get_dynamic_statements_func   = get_dynamic_statements_func

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
        result: Optional[Statement.ParseResult] = None

        observer.StartStatement(unique_id, [self])
        with CallOnExit(
            lambda: observer.EndStatement(
                unique_id,
                [
                    (
                        self,
                        result is not None and result.Success,
                    ),
                ],
            ),
        ):
            dynamic_statements = self._get_dynamic_statements_func(unique_id, observer)
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

            result = await or_statement.ParseAsync(
                unique_id + [or_statement.Name],
                normalized_iter,
                Statement.ObserverDecorator(
                    self,
                    unique_id,
                    observer,
                    [result],
                    lambda result: result.Data,
                ),
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            data = Statement.StandardParseResultData(self, result.Data, unique_id)

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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    ) -> bool:
        # Nothing to do here
        return False
