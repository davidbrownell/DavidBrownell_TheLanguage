# ----------------------------------------------------------------------
# |
# |  FuncTypeLexerInfo_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 09:13:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for FuncTypeLexerInfo.py"""

import os

from dataclasses import fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..FuncTypeLexerInfo import *
    from ..StandardTypeLexerInfo import *

    from ...Common.AutomatedTests import CreateRegion


# ----------------------------------------------------------------------
class TestStandard(object):
    _standard_type                          = StandardTypeLexerInfo(
        [
            CreateRegion(1, 2, 300, 400),
            CreateRegion(1, 2, 3, 4),
            None,
        ],
        "TheType",
        None,
    )

    # ----------------------------------------------------------------------
    def test_NoParameters(self):
        info = FuncTypeLexerInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(5, 6, 7, 8),
                None,
            ],
            self._standard_type,
            None,
        )

        assert info.ReturnType == self._standard_type
        assert info.Parameters is None

    # ----------------------------------------------------------------------
    def test_WithParameters(self):
        info = FuncTypeLexerInfo(
            [
                CreateRegion(1, 2, 3000, 4000),
                CreateRegion(5, 6, 7, 8),
                CreateRegion(9, 10, 11, 12),
            ],
            self._standard_type,
            [self._standard_type, self._standard_type],
        )

        assert info.ReturnType == self._standard_type
        assert info.Parameters == [self._standard_type, self._standard_type]
