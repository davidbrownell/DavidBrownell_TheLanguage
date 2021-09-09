# ----------------------------------------------------------------------
# |
# |  MatchTypeExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 15:47:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchTypeExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.MatchExpressionBase import MatchExpressionBase
    from ....Parser.Phrases.DSL import DynamicPhrasesType


# ----------------------------------------------------------------------
class MatchTypeExpression(MatchExpressionBase):
    """\
    Typed version of a match expression.

    Examples:
        match type Add(1, 2):
            case Int: match_value
            case String: ConvertToInt(match_value)
            default: raise UnexpectedType(match_type)
    """

    PHRASE_NAME                             = "Match Type Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(MatchTypeExpression, self).__init__(DynamicPhrasesType.Types, self.PHRASE_NAME)
