# ----------------------------------------------------------------------
# |
# |  FuncArgumentPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 13:21:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about a function argument"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionPhrase import ExpressionPhrase
    from ..Phrase import Phrase, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncArgumentPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    expression: ExpressionPhrase
    keyword: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FuncArgumentPhrase, self).__init__(regions)
