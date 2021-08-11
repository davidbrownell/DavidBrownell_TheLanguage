# ----------------------------------------------------------------------
# |
# |  TupleName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:06:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleHeader object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.TupleBase import TupleBase
    from ...GrammarPhrase import GrammarPhrase


# ----------------------------------------------------------------------
class TupleName(TupleBase):
    """\
    Creates a tuple that can be used as a name.

    Example:
        (a, b, (c, d)) = value
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleName, self).__init__(GrammarPhrase.Type.Name)
