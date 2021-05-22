# ----------------------------------------------------------------------
# |
# |  Syntax_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-22 10:18:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Syntax.py"""

import os
import textwrap

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import Mock

from semantic_version import Version as SemVer

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MultifileParser import Parse
    from ..StandardStatement import StandardStatement
    from ..StatementsParser import DynamicStatementInfo
    from ..Syntax import *


# ----------------------------------------------------------------------
class TestStandard(object):

    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = NamedStandardStatement("Upper Statement", [_upper_token, NewlineToken()])
    _lower_statement                        = NamedStandardStatement("Lower Statement", [_lower_token, NewlineToken()])
    _number_statement                       = NamedStandardStatement("Number Statement", [_number_token, NewlineToken()])

    _syntaxes                               = {
        SemVer("1.0.0") : DynamicStatementInfo([_upper_statement, _lower_statement], []),
        SemVer("2.0.0") : DynamicStatementInfo([_upper_statement, _lower_statement, _number_statement], []),
    }

    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    def CreateObserver(
        cls,
        content_dict,
        num_threads=None,
    ):
        with ThreadPoolExecutor(
            max_workers=num_threads,
        ) as executor:
            mock = Mock()

            mock.LoadContent = lambda fully_qualified_name: content_dict[fully_qualified_name]
            mock.Enqueue = lambda funcs: [executor.submit(func) for func in funcs]

            yield Observer(mock, cls._syntaxes)

    # ----------------------------------------------------------------------
    def test_Properties(self):
        with self.CreateObserver({}) as observer:
            assert observer.DefaultVersion == SemVer("2.0.0")

            assert len(observer.Syntaxes) == 2

            # The syntax statement should have been added to each
            assert len(observer.Syntaxes[SemVer("1.0.0")].statements) == 3
            assert len(observer.Syntaxes[SemVer("2.0.0")].statements) == 4

    # ----------------------------------------------------------------------
    def test_Default(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    UPPER
                    lower
                    1234
                    """,
                ),
            },
        ) as observer:
            result = Parse(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

            assert len(result) == 1
            assert "one" in result
            result = result["one"]

            assert len(result.Children) == 3

            assert result.Children[0].Children[0].Value.Match.group("value") == "UPPER"
            assert result.Children[1].Children[0].Value.Match.group("value") == "lower"
            assert result.Children[2].Children[0].Value.Match.group("value") == "1234"

    # ----------------------------------------------------------------------
    def test_V1_NoError(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with __syntax=1.0:
                        BUPPER
                        blower

                    __with __syntax=1.0.0:
                        clower

                    456789
                    """,
                ),
            },
        ) as observer:
            result = Parse(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

            assert len(result) == 1
            assert "one" in result
            result = result["one"]

            assert len(result.Children) == 6

            assert result.Children[0].Children[0].Value.Match.group("value") == "AUPPER"
            assert result.Children[1].Children[0].Value.Match.group("value") == "alower"
            assert result.Children[2].Children[0].Value.Match.group("value") == "1234"

            assert result.Children[3].Type == SetSyntaxStatement
            children = list(SetSyntaxStatement.GenerateContentFromResult(result.Children[3]))

            assert len(children) == 2
            assert children[0].Children[0].Value.Match.group("value") == "BUPPER"
            assert children[1].Children[0].Value.Match.group("value") == "blower"

            assert result.Children[4].Type == SetSyntaxStatement
            children = list(SetSyntaxStatement.GenerateContentFromResult(result.Children[4]))

            assert len(children) == 1
            assert children[0].Children[0].Value.Match.group("value") == "clower"

            assert result.Children[5].Children[0].Value.Match.group("value") == "456789"

    # ----------------------------------------------------------------------
    def test_V1_Error(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with __syntax=1.0:
                        BUPPER
                        blower
                        1235
                    """,
                ),
            },
        ) as observer:
            result = Parse(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

            assert len(result) == 1
            result = result[0]

            assert str(result) == "The syntax is not recognized"
            assert result.FullyQualifiedName == "one"
            assert result.Line == 8
            assert result.Column == 1

            assert len(result.PotentialStatements) == 4

            assert result.PotentialStatements[self._upper_statement] == []
            assert result.PotentialStatements[self._lower_statement] == []
            assert result.PotentialStatements[self._number_statement] == []

            set_syntax_results = result.PotentialStatements[SetSyntaxStatement]

            assert len(set_syntax_results) == 8
            set_syntax_results = set_syntax_results[-1]

            assert isinstance(set_syntax_results.Statement, RepeatStatement)
            assert len(set_syntax_results.Results) == 2

            assert set_syntax_results.Results[0].Results[0].Results[0].Results[0].Value.Match.group("value") == "BUPPER"
            assert set_syntax_results.Results[1].Results[0].Results[0].Results[0].Value.Match.group("value") == "blower"

    # ----------------------------------------------------------------------
    def test_InvalidVersion1(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with __syntax=4.5.6:
                        UPPER
                    """,
                ),
            },
        ) as observer:
            result = Parse(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

            assert len(result) == 1
            result = result[0]

            assert str(result) == "The syntax version '4.5.6' is not valid"
            assert result.FullyQualifiedName == "one"
            assert result.Line == 1
            assert result.Column == 17

    # ----------------------------------------------------------------------
    def test_InvalidVersion2(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with __syntax = 4.5:
                        UPPER
                    """,
                ),
            },
        ) as observer:
            result = Parse(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

            assert len(result) == 1
            result = result[0]

            assert str(result) == "The syntax version '4.5.0' is not valid"
            assert result.FullyQualifiedName == "one"
            assert result.Line == 1
            assert result.Column == 19
