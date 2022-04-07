# ----------------------------------------------------------------------
# |
# |  Tokens_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:08:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Token.py"""

import os
import re
import sys
import textwrap

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Tokens import *
    from Normalize import Normalize
    from NormalizedIterator import NormalizedIterator

# ----------------------------------------------------------------------
def test_Equal():
    assert NewlineToken() == NewlineToken()
    assert NewlineToken() != NewlineToken(False)

# ----------------------------------------------------------------------
def test_NewlineToken():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\



                last_line

                """,
            ),
        ),
    )

    token = NewlineToken()

    assert token.name == "Newline+"
    assert token.capture_many

    result = token.Match(iter)
    assert result.range.begin == 0
    assert result.range.end == 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.offset == 12

    result = token.Match(iter)
    assert result.range.begin == 12
    assert result.range.end == 14

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NewlineTokenWithWhitespace():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("\n\n    \nlast_line  \n\n"))

    token = NewlineToken()

    assert token.name == "Newline+"
    assert token.capture_many == True

    result = token.Match(iter)
    assert result.range.begin == 0
    assert result.range.end == 7

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.offset == 16

    assert token.Match(iter) is None
    iter.SkipWhitespaceSuffix()

    result = token.Match(iter)
    assert result.range.begin == 18
    assert result.range.end == 20

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NonGreedyNewline():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\



                last_line

                """,
            ),
        ),
    )

    token = NewlineToken(
        capture_many=False,
    )

    assert token.name == "Newline"
    assert token.capture_many == False

    # Line 1
    assert iter.line == 1
    assert iter.column == 1
    assert iter.offset == 0

    result = token.Match(iter)
    assert result.range.begin == 0
    assert result.range.end == 1

    # Line 2
    assert iter.line == 2
    assert iter.column == 1
    assert iter.offset == 1

    result = token.Match(iter)
    assert result.range.begin == 1
    assert result.range.end == 2

    # Line 3
    assert iter.line == 3
    assert iter.column == 1
    assert iter.offset == 2

    result = token.Match(iter)
    assert result.range.begin == 2
    assert result.range.end == 3

    # Line 4
    assert iter.line == 4
    assert iter.column == 1
    assert iter.offset == 3
    assert token.Match(iter) is None

    iter.Advance(len("last_line"))
    assert iter.offset == 12

    result = token.Match(iter)
    assert result.range.begin == 12
    assert result.range.end == 13

    # Line 5
    assert iter.AtEnd() == False

    assert iter.line == 5
    assert iter.column == 1
    assert iter.offset == 13

    result = token.Match(iter)
    assert result.range.begin == 13
    assert result.range.end == 14

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Indent():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                one
                    two
                      three
                      four
                    five
                """,
            ),
        ),
    )

    token = IndentToken()

    assert token.name == "Indent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    result = token.Match(iter)
    assert result.range.begin == 4
    assert result.range.end == 8
    assert result.indent_value == 4

    assert token.Match(iter) is None
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    result = token.Match(iter)
    result.range.begin == 12
    result.range.end == 18
    result.indent_value == 6

    assert token.Match(iter) is None
    iter.Advance(len("three"))
    iter.Advance(1)

    # Line 4
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    iter.ConsumeDedent()
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("five"))
    iter.Advance(1)

    # Skip the dedent line
    assert iter.AtEnd() == False
    assert iter.has_end_of_file_dedents
    iter.ConsumeDedent()

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Dedent():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                one
                    two
                      three
                      four
                five
                    six
                        seven
                    eight
                """,
            ),
        ),
    )

    token = DedentToken()

    assert token.name == "Dedent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("three"))
    iter.Advance(1)

    # Line 4
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    prev_iter = iter.Clone()
    assert isinstance(token.Match(iter), DedentToken.MatchResult)
    assert isinstance(token.Match(iter), DedentToken.MatchResult)
    iter.Advance(len("five"))
    iter.Advance(1)

    # Line 6
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("six"))
    iter.Advance(1)

    # Line 7
    assert token.Match(iter) is None
    iter.SkipWhitespacePrefix()
    iter.Advance(len("seven"))
    iter.Advance(1)

    # Line 8
    assert isinstance(token.Match(iter), DedentToken.MatchResult)
    iter.Advance(len("eight"))
    iter.Advance(1)

    # Final dedent line
    assert iter.AtEnd() == False
    assert isinstance(token.Match(iter), DedentToken.MatchResult)
    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Regex():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("aaabbb bb b ccc"))

    token = RegexToken("test", re.compile("(?P<value>b+)"))

    assert token.name == "test"

    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)

    assert token.Match(iter).match.group("value") == "bbb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).match.group("value") == "bb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).match.group("value") == "b"
    iter.Advance(1)                         # Move past the space

    assert token.Match(iter) is None

# ----------------------------------------------------------------------
def test_MultilineRegex():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                '''\
                """
                one
                two
                """
                after
                ''',
            ),
        ),
    )

    regex = re.compile(r'"""(?P<content>.+?)"""', re.DOTALL | re.MULTILINE)

    # The match should succeed when multiline is set
    result = RegexToken(
        "Should match",
        regex,
        is_multiline=True,
    ).Match(iter)

    assert result is not None
    assert result.match.group("content") == "\none\ntwo\n"
    assert result.match.start() == 0
    assert result.match.end() == 15

    assert iter.offset == 15

# ----------------------------------------------------------------------
def test_PushIgnoreWhitespaceControlToken():
    token = PushIgnoreWhitespaceControlToken()

    assert token.is_control_token
    assert token.name == "PushIgnoreWhitespaceControlToken"

# ----------------------------------------------------------------------
def test_PopIgnoreWhitespaceControlToken():
    token = PopIgnoreWhitespaceControlToken()

    assert token.is_control_token
    assert token.name == "PopIgnoreWhitespaceControlToken"

# ----------------------------------------------------------------------
def test_NewlineMatch():
    result = NewlineToken().Match(
        NormalizedIterator.FromNormalizedContent(
            Normalize(
                textwrap.dedent(
                    """\


                    """,
                ),
            ),
        ),
    )

    assert result.range.begin == 0
    assert result.range.end == 2

# ----------------------------------------------------------------------
def test_IndentMatch():
    result = IndentToken().Match(
        NormalizedIterator.FromNormalizedContent(
            Normalize(
                "    foo",
            ),
        ),
    )

    assert result.range.begin == 0
    assert result.range.end == 4
    assert result.indent_value == 4

# ----------------------------------------------------------------------
def test_DedentMatch():
    iter = NormalizedIterator.FromNormalizedContent(
        Normalize(
            textwrap.dedent(
                """\
                    foo
                bar
                """,
            ),
        ),
    )

    iter.SkipLine()

    result = DedentToken().Match(iter)
    assert isinstance(result, DedentToken.MatchResult)

# ----------------------------------------------------------------------
def test_RegexMatch():
    result = RegexToken("Token", re.compile("foo")).Match(
        NormalizedIterator.FromNormalizedContent(
            Normalize(
                "foo",
            ),
        ),
    )

    # assert str(result) == textwrap.dedent(
    #     """\
    #     # <class 'Token.RegexToken.MatchResult'>
    #     match: "<_sre.SRE_Match object; span=(0, 3), match='foo'>"
    #     """,
    # )

# ----------------------------------------------------------------------
def test_InvalidMultilineOpeningToken():
    with pytest.raises(AssertionError) as ex:
        RegexToken(
            "Invalid",
            re.compile(r"<<!(?P<value>.+?)>>>", re.DOTALL | re.MULTILINE),
            is_multiline=True,
        )

    ex = ex.value

    assert str(ex) == "('<<!(?P<value>.+?)>>>', 'The opening token must be a multiline phrase token')"

# ----------------------------------------------------------------------
def test_InvalidMultilineClosingToken():
    with pytest.raises(AssertionError) as ex:
        RegexToken(
            "Invalid",
            re.compile(r"<<<(?P<value>.+?)a>>", re.DOTALL | re.MULTILINE),
            is_multiline=True,
        )

    ex = ex.value

    assert str(ex) == "('<<<(?P<value>.+?)a>>', 'The closing token must be a multiline phrase token')"

# ----------------------------------------------------------------------
@pytest.mark.skip("It isn't clear if the check for multiline tokens is a good check or not; the check (and this test) have been disabled for now")
def test_InvalidNonMultilineTokenHeader():
    with pytest.raises(AssertionError) as ex:
        RegexToken("Invalid", re.compile(r"---"))

    ex = ex.value

    assert str(ex) == "('---', 'The regex must not match a multiline phrase token')"
