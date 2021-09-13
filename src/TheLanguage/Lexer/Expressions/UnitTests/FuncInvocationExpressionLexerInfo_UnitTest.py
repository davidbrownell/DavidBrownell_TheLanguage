# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpressionLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-12 15:57:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for FuncInvicationExpressionLexerInfo_UnitTest.py"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..FuncInvocationExpressionLexerInfo import *


# ----------------------------------------------------------------------
def test_Fields():
    regions_fields = set(field.name for field in fields(FuncInvocationExpressionLexerRegions))

    assert regions_fields == set(["Self__", "Name", "Arguments"])
