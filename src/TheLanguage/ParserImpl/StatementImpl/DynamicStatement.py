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

from typing import Callable, List, Union

import CommonEnvironment
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
        get_dynamic_statements_func: Callable[[Statement.Observer], List[Statement]],
        name: str = None,
    ):
        name = name or "Dynamic Statements"

        super(DynamicStatement, self).__init__(name)

        self._get_dynamic_statements_func   = get_dynamic_statements_func

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
        or_statement = OrStatement(
            *self._get_dynamic_statements_func(observer),
            sort_results=False,
        )

        return or_statement.Parse(
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )
