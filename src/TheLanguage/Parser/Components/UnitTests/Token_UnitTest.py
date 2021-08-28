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
    iter = NormalizedIterator(
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
    iter = NormalizedIterator(Normalize("\n\n    \nlast_line  \n\n"))

    token = NewlineToken()

    assert token.Name == "Newline+"
    assert token.CaptureMany

    assert token.Match(iter) == NewlineToken.MatchResult(0, 7)                    # Line 1 - 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.Offset == 16

    assert token.Match(iter) is None
    iter.SkipSuffix()
    assert token.Match(iter) == NewlineToken.MatchResult(18, 20)

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NonGreedyNewline():
    iter = NormalizedIterator(
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
    iter = NormalizedIterator(
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
    iter.SkipPrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("five"))
    iter.Advance(1)

    # Skip the dedent line
    assert iter.AtEnd() == False
    assert iter.HasTrailingDedents()
    iter.Advance(0)

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Dedent():
    iter = NormalizedIterator(
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
    iter.SkipPrefix()
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("three"))
    iter.Advance(1)

    # Line 4
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("four"))
    iter.Advance(1)

    # Line 5
    assert token.Match(iter) == DedentToken.MatchResult()
    assert token.Match(iter) == DedentToken.MatchResult()
    iter.Advance(len("five"))
    iter.Advance(1)

    # Line 6
    assert token.Match(iter) is None
    iter.SkipPrefix()
    iter.Advance(len("six"))
    iter.Advance(1)

    # Line 7
    assert token.Match(iter) is None
    iter.SkipPrefix()
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
    iter = NormalizedIterator(Normalize("aaabbb bb b ccc"))

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
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                '''\
                """
                one
                two
                """after
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
@pytest.mark.skip("TODO: MultilineRegex may not be necessary")
def test_MultilineRegexTokenSingleDelimiter():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                if True:
                    # Line 1
                    # Line 2

                    # Line 3

                    <end>
                """,
            ),
        ),
    )

    token = MultilineRegexToken(
        "This Token",
        re.compile(r"[ \t]+<end>"),
    )

    assert token.Name == "This Token"

    result = token.Match(iter)

    assert result is not None
    assert result.Match.group("value") == textwrap.dedent(
        """\
        if True:
            # Line 1
            # Line 2

            # Line 3

        """,
    )

    assert result.Match.start() == 0
    assert result.Match.end() == 50

    assert iter.Offset == 50

# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: MultilineRegex may not be necessary")
def test_MultilineRegexTokenMultipleDelimiterFirstMatch():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                if True:
                    # Line 1
                    # Line 2

                    # Line 3

                    <end>
                """,
            ),
        ),
    )

    result = MultilineRegexToken(
        "Token",
        re.compile(r"[ \t]+<end>"),
        re.compile(r"this_will_never_match"),
    ).Match(iter)

    assert result is not None
    assert result.Match.group("value") == textwrap.dedent(
        """\
        if True:
            # Line 1
            # Line 2

            # Line 3

        """,
    )

    assert result.Match.start() == 0
    assert result.Match.end() == 50

    assert iter.Offset == 50

# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: MultilineRegex may not be necessary")
def test_MultilineRegexTokenMultipleDelimiterSecondMatch():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                if True:
                    # Line 1
                    # Line 2

                    # Line 3

                    <end>
                """,
            ),
        ),
    )

    result = MultilineRegexToken(
        "Token",
        re.compile(r"[ \t]+<end>"),
        re.compile(r"# Line 3"),
    ).Match(iter)

    assert result is not None
    assert result.Match.group("value") == "if True:\n    # Line 1\n    # Line 2\n\n    "
    assert result.Match.start() == 0
    assert result.Match.end() == 40

    assert iter.Offset == 40

# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: MultilineRegex may not be necessary")
def test_MultilineRegexNoMatch():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                one
                two
                three
                """,
            ),
        ),
    )

    result = MultilineRegexToken(
        "Token",
        re.compile(r"This will never match"),
    ).Match(iter)

    assert result is None

# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: MultilineRegex may not be necessary")
def test_MultilineRegexCustomGroup():
    iter = NormalizedIterator(
        Normalize(
            textwrap.dedent(
                """\
                orange
                green
                blue
                """,
            ),
        ),
    )

    result = MultilineRegexToken(
        "Token",
        re.compile(r"green"),
        regex_match_group_name="custom_name",
    ).Match(iter)

    assert result is not None
    assert result.Match.group("custom_name") == "orange\n"
    assert result.Match.start() == 0
    assert result.Match.end() == 7

    assert iter.Offset == 7

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
        NormalizedIterator(
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
        NormalizedIterator(
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
    iter = NormalizedIterator(
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
        NormalizedIterator(
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
