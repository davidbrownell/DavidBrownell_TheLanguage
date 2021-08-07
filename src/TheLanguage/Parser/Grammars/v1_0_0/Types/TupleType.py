# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-06 18:41:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import GrammarDSL
    from ..Common.TupleBase import TupleBase
    from ...GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class TupleType(TupleBase):
    """\
    Creates a tuple that can be used as a type.

    '(' <content> ')'

    Examples:
        var = value as (Foo, Bar)
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TupleType, self).__init__(
            GrammarStatement.Type.Type,
            "Tuple Type",
            GrammarDSL.DynamicStatementsType.Types,
            additional_sequence_suffix_items=[],
        )
