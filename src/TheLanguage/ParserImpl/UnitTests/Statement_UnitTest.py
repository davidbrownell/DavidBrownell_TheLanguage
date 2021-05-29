# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-10 09:47:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Statement.py"""

import os

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Statement import *
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator
    from ..Token import *


# BugBug: Test name
#   Valid
#   assertion
# BugBug: Test ignore_whitespace

# ----------------------------------------------------------------------
class MyStatement(Statement):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        index: int,
        matches: bool,
        extent: int,
    ):
        self._index                         = index
        self._matches                       = matches
        self._extent                        = extent

        self.Name                           = "{}, {}, {}".format(self._index, self._matches, self._extent)

    # ----------------------------------------------------------------------
    @Interface.override
    def Parse(self, normalized_iter, observer):
        normalized_iter.Advance(self._extent)
        return Statement.ParseResult(self._matches, [], normalized_iter)


# ----------------------------------------------------------------------
class TestStandard(object):
    executor                                = ThreadPoolExecutor()

    mock                                    = Mock()
    mock.Enqueue                            = lambda funcs: [TestStandard.executor.submit(func) for func in funcs]

    # ----------------------------------------------------------------------
    def test_FirstMatch(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, True, 10),
                MyStatement(1, True, 5),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success
        assert result.Iter.Offset == 10
        assert len(result.Results) == 1
        assert result.Results[0].Statement.Name == "0, True, 10"

    # ----------------------------------------------------------------------
    def test_SecondMatch(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, True, 5),
                MyStatement(1, True, 10),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success
        assert result.Iter.Offset == 10
        assert len(result.Results) == 1
        assert result.Results[0].Statement.Name == "1, True, 10"

    # ----------------------------------------------------------------------
    def test_SecondMatchNoSort(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, True, 5),
                MyStatement(1, True, 10),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
            sort_results=False,
        )

        assert result.Success
        assert result.Iter.Offset == 5
        assert len(result.Results) == 1
        assert result.Results[0].Statement.Name == "0, True, 5"

    # ----------------------------------------------------------------------
    def test_LastMatch(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, False, 10),
                MyStatement(1, False, 5),
                MyStatement(2, True, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success
        assert result.Iter.Offset == 2
        assert len(result.Results) == 1
        assert result.Results[0].Statement.Name == "2, True, 2"

    # ----------------------------------------------------------------------
    def test_MultiMatch(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, False, 10),
                MyStatement(1, True, 5),
                MyStatement(2, True, 5),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success
        assert result.Iter.Offset == 5
        assert len(result.Results) == 1
        assert result.Results[0].Statement.Name == "1, True, 5"

    # ----------------------------------------------------------------------
    def test_NoMatch1(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, False, 10),
                MyStatement(1, False, 5),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success == False
        assert result.Iter.Offset == 10
        assert len(result.Results) == 3
        assert result.Results[0].Statement.Name == "0, False, 10"
        assert result.Results[1].Statement.Name == "1, False, 5"
        assert result.Results[2].Statement.Name == "2, False, 2"

    # ----------------------------------------------------------------------
    def test_NoMatch2(self):
        result = Statement.ParseMultiple(
            [
                MyStatement(0, False, 2),
                MyStatement(1, False, 5),
                MyStatement(2, False, 10),
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result.Success == False
        assert result.Iter.Offset == 10
        assert len(result.Results) == 3
        assert result.Results[0].Statement.Name == "0, False, 2"
        assert result.Results[1].Statement.Name == "1, False, 5"
        assert result.Results[2].Statement.Name == "2, False, 10"

    # ----------------------------------------------------------------------
    def test_Cancellation(self):
        statement_mock = Mock()
        statement_mock.Parse = Mock(return_value=None)

        result = Statement.ParseMultiple(
            [
                statement_mock,
            ],
            NormalizedIterator(Normalize("0123456789")),
            self.mock,
        )

        assert result is None
