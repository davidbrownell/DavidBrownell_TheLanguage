# ----------------------------------------------------------------------
# |
# |  Token_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-11 20:06:33
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
    from Token import *
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

    assert token.Name == "Newline+"
    assert token.CaptureMany

    assert token.Match(iter) == NewlineToken.MatchResult(0, 3)                    # Lines 1-3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.Offset == 12
    assert token.Match(iter) == NewlineToken.MatchResult(12, 14)

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NewlineTokenWithWhitespace():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("\n\n    \nlast_line  \n\n"))

    token = NewlineToken()

    assert token.Name == "Newline+"
    assert token.CaptureMany

    assert token.Match(iter) == NewlineToken.MatchResult(0, 7)                    # Line 1 - 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.Offset == 16

    assert token.Match(iter) is None
    iter.SkipWhitespaceSuffix()
    assert token.Match(iter) == NewlineToken.MatchResult(18, 20)

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

    assert token.Name == "Newline"
    assert token.CaptureMany == False

    # Line 1
    assert iter.Line == 1
    assert iter.Column == 1
    assert iter.Offset == 0
    assert token.Match(iter) == NewlineToken.MatchResult(0, 1)

    # Line 2
    assert iter.Line == 2
    assert iter.Column == 1
    assert iter.Offset == 1
    assert token.Match(iter) == NewlineToken.MatchResult(1, 2)

    # Line 3
    assert iter.Line == 3
    assert iter.Column == 1
    assert iter.Offset == 2
    assert token.Match(iter) == NewlineToken.MatchResult(2, 3)

    # Line 4
    assert iter.Line == 4
    assert iter.Column == 1
    assert iter.Offset == 3
    assert token.Match(iter) is None

    iter.Advance(len("last_line"))
    assert iter.Offset == 12
    assert token.Match(iter) == NewlineToken.MatchResult(12, 13)

    # Line 5
    assert iter.AtEnd() == False

    assert iter.Line == 5
    assert iter.Column == 1
    assert iter.Offset == 13
    assert token.Match(iter) == NewlineToken.MatchResult(13, 14)

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

    assert token.Name == "Indent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    assert token.Match(iter) == IndentToken.MatchResult(4, 8, 4)
    assert token.Match(iter) is None
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    assert token.Match(iter) == IndentToken.MatchResult(12, 18, 6)
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
    assert iter.HasEndOfFileDedents()
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

    assert token.Name == "Dedent"

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
    assert token.Match(iter) == DedentToken.MatchResult()
    assert token.Match(iter) == DedentToken.MatchResult()
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
    assert token.Match(iter) == DedentToken.MatchResult()
    iter.Advance(len("eight"))
    iter.Advance(1)

    # Final dedent line
    assert iter.AtEnd() == False
    assert token.Match(iter) == DedentToken.MatchResult()
    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Regex():
    iter = NormalizedIterator.FromNormalizedContent(Normalize("aaabbb bb b ccc"))

    token = RegexToken("test", re.compile("(?P<value>b+)"))

    assert token.Name == "test"

    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)
    assert token.Match(iter) is None
    iter.Advance(1)

    assert token.Match(iter).Match.group("value") == "bbb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).Match.group("value") == "bb"
    iter.Advance(1)                         # Move past the space
    assert token.Match(iter).Match.group("value") == "b"
    iter.Advance(1)                         # Move past the space

    assert token.Match(iter) is None

# ----------------------------------------------------------------------
def test_RegexErrors():
    with pytest.raises(AssertionError):
        RegexToken(None, "doesn't matter")

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

    # The match should fail when multiline is not set
    assert RegexToken("Should not match", regex).Match(iter) is None

    # The match should succeed when multiline is set
    result = RegexToken(
        "Should match",
        regex,
        is_multiline=True,
    ).Match(iter)

    assert result is not None
    assert result.Match.group("content") == "\none\ntwo\n"
    assert result.Match.start() == 0
    assert result.Match.end() == 15

    assert iter.Offset == 15


# ----------------------------------------------------------------------
def test_ControlTokens():
    assert NewlineToken().IsControlToken == False

    # ----------------------------------------------------------------------
    @Interface.staticderived
    class MyControlToken(ControlTokenBase):
        Name                                = Interface.DerivedProperty("MyControlToken")

    # ----------------------------------------------------------------------

    assert MyControlToken.IsControlToken

    with pytest.raises(Exception):
        MyControlToken.Match(None)

# ----------------------------------------------------------------------
def test_PushIgnoreWhitespaceControlToken():
    token = PushIgnoreWhitespaceControlToken()

    assert token.IsControlToken
    assert token.Name == "PushIgnoreWhitespaceControl"

# ----------------------------------------------------------------------
def test_PopIgnoreWhitespaceControlToken():
    token = PopIgnoreWhitespaceControlToken()

    assert token.IsControlToken
    assert token.Name == "PopIgnoreWhitespaceControl"

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

    assert str(result) == textwrap.dedent(
        """\
        # <class 'Token.NewlineToken.MatchResult'>
        End: 2
        Start: 0
        """,
    )

# ----------------------------------------------------------------------
def test_IndentMatch():
    result = IndentToken().Match(
        NormalizedIterator.FromNormalizedContent(
            Normalize(
                "    foo",
            ),
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        # <class 'Token.IndentToken.MatchResult'>
        End: 4
        Start: 0
        Value: 4
        """,
    )

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

    assert str(result) == textwrap.dedent(
        """\
        # <class 'Token.DedentToken.MatchResult'>
        {}
        """,
    )

# ----------------------------------------------------------------------
def test_RegexMatch():
    result = RegexToken("Token", re.compile("foo")).Match(
        NormalizedIterator.FromNormalizedContent(
            Normalize(
                "foo",
            ),
        ),
    )

    assert str(result) == textwrap.dedent(
        """\
        # <class 'Token.RegexToken.MatchResult'>
        Match: "<_sre.SRE_Match object; span=(0, 3), match='foo'>"
        """,
    )

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
def test_InvalidNonMultilineToken():
    with pytest.raises(AssertionError) as ex:
        RegexToken("Invalid", re.compile(r"---"))

    ex = ex.value

    assert str(ex) == "('---', 'The regex must not match a multiline phrase token')"
