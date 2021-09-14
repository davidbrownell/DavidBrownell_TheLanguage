# ----------------------------------------------------------------------
# |
# |  MatchTypeExpressionLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-14 08:33:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for MatchTypeExpressionLexerInfo.py"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MatchTypeExpressionLexerInfo import *


# ----------------------------------------------------------------------
def test_Regions():
    regions_fields = set(field.name for field in fields(MatchTypeExpressionLexerRegions))

    assert regions_fields == set(["Self__", "Expression", "CasePhrases", "Default"])
