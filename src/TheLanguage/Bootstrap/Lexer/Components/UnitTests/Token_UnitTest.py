# ----------------------------------------------------------------------
# |
# |  Token_UnitTest.py
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
    from Token import *
    from Normalize import Normalize
    from NormalizedIterator import NormalizedIterator

# ----------------------------------------------------------------------
def test_Equal():
    assert NewlineToken.Create() == NewlineToken.Create()
    assert NewlineToken.Create() != NewlineToken.Create(False)

# ----------------------------------------------------------------------
def test_NewlineToken():
    iter = NormalizedIterator.Create(
        Normalize(
            textwrap.dedent(
                """\



                last_line

                """,
            ),
        ),
    )

    token = NewlineToken.Create()

    assert token.name == "Newline+"
    assert token.capture_many

    result = token.Match(iter)
    assert result.start == 0
    assert result.end == 3

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.OffsetProper() == 12

    result = token.Match(iter)
    assert result.start == 12
    assert result.end == 14

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NewlineTokenWithWhitespace():
    iter = NormalizedIterator.Create(Normalize("\n\n    \nlast_line  \n\n"))

    token = NewlineToken.Create()

    assert token.name == "Newline+"
    assert token.capture_many == True

    result = token.Match(iter)
    assert result.start == 0
    assert result.end == 7

    # line with 'last_line'
    assert token.Match(iter) is None
    iter.Advance(len("last_line"))
    assert iter.Offset == 16

    assert token.Match(iter) is None
    iter.SkipWhitespaceSuffix()

    result = token.Match(iter)
    assert result.start == 18
    assert result.end == 20

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_NonGreedyNewline():
    iter = NormalizedIterator.Create(
        Normalize(
            textwrap.dedent(
                """\



                last_line

                """,
            ),
        ),
    )

    token = NewlineToken.Create(
        capture_many=False,
    )

    assert token.name == "Newline"
    assert token.capture_many == False

    # Line 1
    assert iter.LineProper() == 1
    assert iter.ColumnProper() == 1
    assert iter.OffsetProper() == 0

    result = token.Match(iter)
    assert result.start == 0
    assert result.end == 1

    # Line 2
    assert iter.Line == 2
    assert iter.Column == 1
    assert iter.Offset == 1

    result = token.Match(iter)
    assert result.start == 1
    assert result.end == 2

    # Line 3
    assert iter.Line == 3
    assert iter.Column == 1
    assert iter.Offset == 2

    result = token.Match(iter)
    assert result.start == 2
    assert result.end == 3

    # Line 4
    assert iter.Line == 4
    assert iter.Column == 1
    assert iter.Offset == 3
    assert token.Match(iter) is None

    iter.Advance(len("last_line"))
    assert iter.Offset == 12

    result = token.Match(iter)
    assert result.start == 12
    assert result.end == 13

    # Line 5
    assert iter.AtEnd() == False

    assert iter.Line == 5
    assert iter.Column == 1
    assert iter.Offset == 13

    result = token.Match(iter)
    assert result.start == 13
    assert result.end == 14

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Indent():
    iter = NormalizedIterator.Create(
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

    token = IndentToken.Create()

    assert token.name == "Indent"

    # Line 1
    assert token.Match(iter) is None
    iter.Advance(len("one"))
    assert token.Match(iter) is None
    iter.Advance(1)

    # Line 2
    result = token.Match(iter)
    assert result.start == 4
    assert result.end == 8
    assert result.indent_value == 4

    assert token.Match(iter) is None
    iter.Advance(len("two"))
    iter.Advance(1)

    # Line 3
    result = token.Match(iter)
    result.start == 12
    result.end == 18
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
    assert iter.HasEndOfFileDedentsProper()
    iter.ConsumeDedent()

    assert iter.AtEnd()

# ----------------------------------------------------------------------
def test_Dedent():
    iter = NormalizedIterator.Create(
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

    token = DedentToken.Create()

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
    iter = NormalizedIterator.Create(Normalize("aaabbb bb b ccc"))

    token = RegexToken.Create("test", re.compile("(?P<value>b+)"))

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
    iter = NormalizedIterator.Create(
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
    result = RegexToken.Create(
        "Should match",
        regex,
        is_multiline=True,
    ).Match(iter)

    assert result is not None
    assert result.match.group("content") == "\none\ntwo\n"
    assert result.match.start() == 0
    assert result.match.end() == 15

    assert iter.Offset == 15

# ----------------------------------------------------------------------
def test_PushIgnoreWhitespaceControlToken():
    token = PushIgnoreWhitespaceControlToken.Create()

    assert token.is_control_token
    assert token.name == "PushIgnoreWhitespaceControl"

# ----------------------------------------------------------------------
def test_PopIgnoreWhitespaceControlToken():
    token = PopIgnoreWhitespaceControlToken.Create()

    assert token.is_control_token
    assert token.name == "PopIgnoreWhitespaceControl"

# ----------------------------------------------------------------------
def test_NewlineMatch():
    result = NewlineToken.Create().Match(
        NormalizedIterator.Create(
            Normalize(
                textwrap.dedent(
                    """\


                    """,
                ),
            ),
        ),
    )

    assert result.start == 0
    assert result.end == 2

# ----------------------------------------------------------------------
def test_IndentMatch():
    result = IndentToken.Create().Match(
        NormalizedIterator.Create(
            Normalize(
                "    foo",
            ),
        ),
    )

    assert result.start == 0
    assert result.end == 4
    assert result.indent_value == 4

# ----------------------------------------------------------------------
def test_DedentMatch():
    iter = NormalizedIterator.Create(
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

    result = DedentToken.Create().Match(iter)
    assert isinstance(result, DedentToken.MatchResult)

# ----------------------------------------------------------------------
def test_RegexMatch():
    result = RegexToken.Create("Token", re.compile("foo")).Match(
        NormalizedIterator.Create(
            Normalize(
                "foo",
            ),
        ),
    )

    # assert str(result) == textwrap.dedent(
    #     """\
    #     # <class 'Token.RegexToken.MatchResult'>
    #     Match: "<_sre.SRE_Match object; span=(0, 3), match='foo'>"
    #     """,
    # )

# ----------------------------------------------------------------------
def test_InvalidMultilineOpeningToken():
    with pytest.raises(AssertionError) as ex:
        RegexToken.Create(
            "Invalid",
            re.compile(r"<<!(?P<value>.+?)>>>", re.DOTALL | re.MULTILINE),
            is_multiline=True,
        )

    ex = ex.value

    assert str(ex) == "('<<!(?P<value>.+?)>>>', 'The opening token must be a multiline phrase token')"

# ----------------------------------------------------------------------
def test_InvalidMultilineClosingToken():
    with pytest.raises(AssertionError) as ex:
        RegexToken.Create(
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
        RegexToken.Create("Invalid", re.compile(r"---"))

    ex = ex.value

    assert str(ex) == "('---', 'The regex must not match a multiline phrase token')"
