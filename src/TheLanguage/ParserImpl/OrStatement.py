# ----------------------------------------------------------------------
# |
# |  OrStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-15 16:25:16
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

from typing import List, Optional

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
@read_only_properties("Items")
class OrStatement(Statement):
    """\
    Statement that returns a match on the first matching contained statement.

    Note that this behavior will match short-circuit semantics, so the earliest
    match will always be returned, even if a later match is longer (which is normally
    considered to be a "better" match).
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        items: List[Statement],
    ):
        assert items

        self.Items                          = items

    # ----------------------------------------------------------------------
    @Interface.override
    def Parse(
        self,
        normalized_iter: NormalizedIterator,
        observer: Statement.Observer,
    ) -> Optional[Statement.ParseResult]:
        return self.ParseMultiple(
            self.Items,
            normalized_iter,
            observer,
            sort_results=False,
        )
