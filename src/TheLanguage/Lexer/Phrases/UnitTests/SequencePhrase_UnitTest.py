# ----------------------------------------------------------------------
# |
# |  SequencePhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 12:57:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for SequencePhrase.py"""

import os
import re
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import DSL
    from ..OrPhrase import OrPhrase
    from ..SequencePhrase import *

    from ..TokenPhrase import (
        NewlineToken,
        RegexToken,
        TokenPhrase,
    )

    from ...Components.UnitTests import (
        CreateIterator,
        parse_mock,
    )


# ----------------------------------------------------------------------
class TestUnusualScenarios(object):
    _lower_phrase                           = TokenPhrase(RegexToken("lower", re.compile(r"(?P<value>[a-z]+[0-9]*)")))
    _upper_phrase                           = TokenPhrase(RegexToken("upper", re.compile(r"(?P<value>[A-Z]+[0-9]*)")))
    _newline_phrase                         = TokenPhrase(NewlineToken())

    _phrase                                 = OrPhrase(
        [
            # Note that we are using 2 SequencePhrases to tease out potential ambiguity issues when
            # both phrases match the same content.
            SequencePhrase(DSL.DefaultCommentToken, [_lower_phrase, _newline_phrase]),
            SequencePhrase(DSL.DefaultCommentToken, [_upper_phrase, _newline_phrase]),
        ],
    )

    _indent_phrase                          = SequencePhrase(
        DSL.DefaultCommentToken,
        [
            _lower_phrase,
            _newline_phrase,
            TokenPhrase(IndentToken()),
            _upper_phrase,
            _newline_phrase,
            TokenPhrase(DedentToken()),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InitialWhitespace(self, parse_mock):
        at_end, result = await self._GetResults(
            parse_mock,
            textwrap.dedent(
                """\


                lower1
                lower2
                """,
            ),
        )

        CompareResultsFromFile(
            result,
        )

        assert at_end

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InternalComments(self, parse_mock):
        at_end, result = await self._GetResults(
            parse_mock,
            textwrap.dedent(
                """\
                lower1 # Comment2
                lower2
                # Comment3
                lower3



                    # Comment4
                # Comment5


                lower4
                """,
            ),
        )

        CompareResultsFromFile(
            result,
        )

        assert at_end

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LineTrailingWhitespace(self, parse_mock):
        at_end, result = await self._GetResults(
            parse_mock,
            "lower1    \nlower2\t\t",
        )

        CompareResultsFromFile(
            result,
        )

        assert at_end

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_CommentAndIndent(self, parse_mock):
        at_end, result = await self._GetResults(
            parse_mock,
            textwrap.dedent(
                """\
                lower1
                    UPPER1

                lower2
                    # This is a comment; it should not interfere with the indent
                    UPPER2
                """,
            ),
            phrase=self._indent_phrase,
        )

        CompareResultsFromFile(
            result,
        )

        assert at_end

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    async def _GetResults(
        self,
        parse_mock,
        content: str,
        phrase=None,
        single_threaded=None,
    ) -> Tuple[bool, str]:
        iter = CreateIterator(content)

        results = []

        while not iter.AtEnd():
            result = await (phrase or self._phrase).LexAsync(
                ("root", str(len(results))),
                iter,
                parse_mock,
                single_threaded=single_threaded,
            )
            assert result is not None

            results.append(str(result))

            if not result.Success:
                break

            iter = result.IterEnd

        return iter.AtEnd(), "\n".join(results)
