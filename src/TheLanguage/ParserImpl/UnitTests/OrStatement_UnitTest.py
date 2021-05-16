# ----------------------------------------------------------------------
# |
# |  OrStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-15 16:37:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for OrStatement.py"""

import os
import re
import textwrap

from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator
    from ..OrStatement import *
    from ..StandardStatement import StandardStatement

    from ..Token import (
        RegexToken,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _short_token                            = RegexToken("Short Token", re.compile(r"(?P<value>[a-z]{3})"))
    _long_token                             = RegexToken("Long Token", re.compile(r"(?P<value>[a-z]{7})"))

    _short_statement                        = StandardStatement("Short Statement", [_short_token])
    _long_statement                         = StandardStatement("Long Statement", [_long_token])

    _or_statement                           = OrStatement("Or Statement", [_short_statement, _long_statement])

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def execution_mock():
        mock = Mock()

        mock.executor = ThreadPoolExecutor()
        mock.Enqueue = lambda funcs: [mock.executor.submit(func) for func in funcs]

        return mock

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self._or_statement.Name == "Or Statement"
        assert self._or_statement.Items == [self._short_statement, self._long_statement]

    # ----------------------------------------------------------------------
    def test_Match(self, execution_mock):
        # The first will always match, even if the second is technically better; this is to preserve
        # standard short-circuiting semantics.
        result = self._or_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        abcdefg
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success
        assert result.Iter.Line == 1
        assert result.Iter.Column == 4

        assert len(result.Results) == 1
        assert result.Results[0].Statement == self._short_statement
        assert len(result.Results[0].Results) == 1
        assert result.Results[0].Results[0].Value.Match.group("value") == "abc"

    # ----------------------------------------------------------------------
    def test_NoMatch(self, execution_mock):
        result = self._or_statement.Parse(
            NormalizedIterator(
                Normalize(
                    textwrap.dedent(
                        """\
                        1234567
                        """,
                    ),
                ),
            ),
            execution_mock,
        )

        assert result.Success == False
        assert result.Iter.Line == 1
        assert result.Iter.Column == 1

        assert len(result.Results) == 2

        assert result.Results[0].Statement == self._short_statement
        assert result.Results[0].Results == []

        assert result.Results[1].Statement == self._long_statement
        assert result.Results[1].Results == []
