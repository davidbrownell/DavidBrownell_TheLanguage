# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-18 14:08:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Statement.py"""

import os

from unittest.mock import Mock

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Coroutine import Execute
    from ..Statement import *
    from ..NormalizedIterator import NormalizedIterator
    from ..Normalize import Normalize
    from ..Token import *

# ----------------------------------------------------------------------
class MyStatement(Statement):
    # ----------------------------------------------------------------------
    def __init__(self, index, matches, extent):
        self._index                         = index
        self._matches                       = matches
        self._extent                        = extent

        self._name                          = "{}, {}, {}".format(self._index, self._matches, self._extent)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def ParseCoroutine(
        self,
        normalized_iter: NormalizedIterator,
        observer: Statement.Observer,
    ) -> Generator[
        None,
        Coroutine.Status,
        Optional[Statement.ParseResult],
    ]:
        yield
        yield
        yield

        normalized_iter.Advance(self._extent)

        return Statement.ParseResult(
            self._matches,
            [],
            normalized_iter,
        )

# ----------------------------------------------------------------------
def test_FirstMatch():
    result = Execute(
        Statement.ParseMultipleCoroutine(
            [
                MyStatement(0, True, 10),
                MyStatement(1, True, 5),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            Mock(),
        ),
    )[0]

    assert result.Success
    assert result.Iter.Offset == 10
    assert len(result.Results) == 1
    assert result.Results[0].Statement.Name == "0, True, 10"

# ----------------------------------------------------------------------
def test_SecondMatch():
    result = Execute(
        Statement.ParseMultipleCoroutine(
            [
                MyStatement(0, True, 5),
                MyStatement(1, True, 10),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            Mock(),
        ),
    )[0]

    assert result.Success
    assert result.Iter.Offset == 10
    assert len(result.Results) == 1
    assert result.Results[0].Statement.Name == "1, True, 10"

# ----------------------------------------------------------------------
def test_EndMatch():
    result = Execute(
        Statement.ParseMultipleCoroutine(
            [
                MyStatement(0, False, 5),
                MyStatement(1, False, 10),
                MyStatement(2, True, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            Mock(),
        ),
    )[0]

    assert result.Success
    assert result.Iter.Offset == 2
    assert len(result.Results) == 1
    assert result.Results[0].Statement.Name == "2, True, 2"

# ----------------------------------------------------------------------
def test_NoMatch1():
    result = Execute(
        Statement.ParseMultipleCoroutine(
            [
                MyStatement(0, False, 10),
                MyStatement(1, False, 5),
                MyStatement(2, False, 2),
            ],
            NormalizedIterator(Normalize("0123456789")),
            Mock(),
        ),
    )[0]

    assert result.Success == False
    assert len(result.Results) == 3
    assert result.Results[0].Statement.Name == "0, False, 10"
    assert result.Results[1].Statement.Name == "1, False, 5"
    assert result.Results[2].Statement.Name == "2, False, 2"

# ----------------------------------------------------------------------
def test_NoMatch2():
    result = Execute(
        Statement.ParseMultipleCoroutine(
            [
                MyStatement(0, False, 2),
                MyStatement(1, False, 5),
                MyStatement(2, False, 10),
            ],
            NormalizedIterator(Normalize("0123456789")),
            Mock(),
        ),
    )[0]

    assert result.Success == False
    assert len(result.Results) == 3
    assert result.Results[0].Statement.Name == "0, False, 2"
    assert result.Results[1].Statement.Name == "1, False, 5"
    assert result.Results[2].Statement.Name == "2, False, 10"
