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
    from ..Statement import Statement
    from ..StatementsParser import DynamicStatementInfo
    from ..Syntax import *


# ----------------------------------------------------------------------
class TestStandard(object):

    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _upper_statement                        = Statement("Upper Statement", _upper_token, NewlineToken())
    _lower_statement                        = Statement("Lower Statement", _lower_token, NewlineToken())
    _number_statement                       = Statement("Number Statement", _number_token, NewlineToken())

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

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    2.0.0 Grammar
                        Upper Statement
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='UPPER'>>> ws:None [1, 1 -> 1, 6]
                            Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                    2.0.0 Grammar
                        Lower Statement
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='lower'>>> ws:None [2, 1 -> 2, 6]
                            Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                    2.0.0 Grammar
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(12, 16), match='1234'>>> ws:None [3, 1 -> 3, 5]
                            Newline+ <<16, 17>> ws:None [3, 5 -> 4, 1]
                """,
            )

    # ----------------------------------------------------------------------
    def test_V1_NoError(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with_syntax=1.0:
                        BUPPER
                        blower

                    __with_syntax=1.0.0:
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

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    2.0.0 Grammar
                        Upper Statement
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 6), match='AUPPER'>>> ws:None [1, 1 -> 1, 7]
                            Newline+ <<6, 7>> ws:None [1, 7 -> 2, 1]
                    2.0.0 Grammar
                        Lower Statement
                            Lower Token <<Regex: <_sre.SRE_Match object; span=(7, 13), match='alower'>>> ws:None [2, 1 -> 2, 7]
                            Newline+ <<13, 14>> ws:None [2, 7 -> 3, 1]
                    2.0.0 Grammar
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(14, 18), match='1234'>>> ws:None [3, 1 -> 3, 5]
                            Newline+ <<18, 20>> ws:None [3, 5 -> 5, 1]
                    2.0.0 Grammar
                        Set Syntax
                            '__with_syntax' <<Regex: <_sre.SRE_Match object; span=(20, 33), match='__with_syntax'>>> ws:None [5, 1 -> 5, 14]
                            '=' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='='>>> ws:None [5, 14 -> 5, 15]
                            <semantic_version> <<Regex: <_sre.SRE_Match object; span=(34, 37), match='1.0'>>> ws:None [5, 15 -> 5, 18]
                            ':' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=':'>>> ws:None [5, 18 -> 5, 19]
                            Newline+ <<38, 39>> ws:None [5, 19 -> 6, 1]
                            Indent <<39, 43, (4)>> ws:None [6, 1 -> 6, 5]
                            Repeat: (DynamicStatements.Statements, 1, None)
                                DynamicStatements.Statements
                                    1.0.0 Grammar
                                        Upper Statement
                                            Upper Token <<Regex: <_sre.SRE_Match object; span=(43, 49), match='BUPPER'>>> ws:None [6, 5 -> 6, 11]
                                            Newline+ <<49, 50>> ws:None [6, 11 -> 7, 1]
                                DynamicStatements.Statements
                                    1.0.0 Grammar
                                        Lower Statement
                                            Lower Token <<Regex: <_sre.SRE_Match object; span=(54, 60), match='blower'>>> ws:None [7, 5 -> 7, 11]
                                            Newline+ <<60, 62>> ws:None [7, 11 -> 9, 1]
                            Dedent <<>> ws:None [9, 1 -> 9, 1]
                    2.0.0 Grammar
                        Set Syntax
                            '__with_syntax' <<Regex: <_sre.SRE_Match object; span=(62, 75), match='__with_syntax'>>> ws:None [9, 1 -> 9, 14]
                            '=' <<Regex: <_sre.SRE_Match object; span=(75, 76), match='='>>> ws:None [9, 14 -> 9, 15]
                            <semantic_version> <<Regex: <_sre.SRE_Match object; span=(76, 81), match='1.0.0'>>> ws:None [9, 15 -> 9, 20]
                            ':' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=':'>>> ws:None [9, 20 -> 9, 21]
                            Newline+ <<82, 83>> ws:None [9, 21 -> 10, 1]
                            Indent <<83, 87, (4)>> ws:None [10, 1 -> 10, 5]
                            Repeat: (DynamicStatements.Statements, 1, None)
                                DynamicStatements.Statements
                                    1.0.0 Grammar
                                        Lower Statement
                                            Lower Token <<Regex: <_sre.SRE_Match object; span=(87, 93), match='clower'>>> ws:None [10, 5 -> 10, 11]
                                            Newline+ <<93, 95>> ws:None [10, 11 -> 12, 1]
                            Dedent <<>> ws:None [12, 1 -> 12, 1]
                    2.0.0 Grammar
                        Number Statement
                            Number Token <<Regex: <_sre.SRE_Match object; span=(95, 101), match='456789'>>> ws:None [12, 1 -> 12, 7]
                            Newline+ <<101, 102>> ws:None [12, 7 -> 13, 1]
                """,
            )

    # ----------------------------------------------------------------------
    def test_V1_Error(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with_syntax=1.0:
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

            assert len(result.PotentialStatements) == 1
            key = tuple(observer.Syntaxes[observer.DefaultVersion].statements)
            assert key in result.PotentialStatements

            potentials = result.PotentialStatements[key]
            assert len(potentials) == 4

            assert str(potentials[0]) == textwrap.dedent(
                """\
                Set Syntax
                    '__with_syntax' <<Regex: <_sre.SRE_Match object; span=(20, 33), match='__with_syntax'>>> ws:None [5, 1 -> 5, 14]
                    '=' <<Regex: <_sre.SRE_Match object; span=(33, 34), match='='>>> ws:None [5, 14 -> 5, 15]
                    <semantic_version> <<Regex: <_sre.SRE_Match object; span=(34, 37), match='1.0'>>> ws:None [5, 15 -> 5, 18]
                    ':' <<Regex: <_sre.SRE_Match object; span=(37, 38), match=':'>>> ws:None [5, 18 -> 5, 19]
                    Newline+ <<38, 39>> ws:None [5, 19 -> 6, 1]
                    Indent <<39, 43, (4)>> ws:None [6, 1 -> 6, 5]
                    Repeat: (DynamicStatements.Statements, 1, None)
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Upper Statement
                                    Upper Token <<Regex: <_sre.SRE_Match object; span=(43, 49), match='BUPPER'>>> ws:None [6, 5 -> 6, 11]
                                    Newline+ <<49, 50>> ws:None [6, 11 -> 7, 1]
                        DynamicStatements.Statements
                            1.0.0 Grammar
                                Lower Statement
                                    Lower Token <<Regex: <_sre.SRE_Match object; span=(54, 60), match='blower'>>> ws:None [7, 5 -> 7, 11]
                                    Newline+ <<60, 61>> ws:None [7, 11 -> 8, 1]
                """,
            )

            assert str(potentials[1]) == textwrap.dedent(
                """\
                Upper Statement
                    <No results>
                """,
            )

            assert str(potentials[2]) == textwrap.dedent(
                """\
                Lower Statement
                    <No results>
                """,
            )

            assert str(potentials[3]) == textwrap.dedent(
                """\
                Number Statement
                    <No results>
                """,
            )

    # ----------------------------------------------------------------------
    def test_InvalidVersion1(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with_syntax=4.5.6:
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
            assert result.Column == 15

    # ----------------------------------------------------------------------
    def test_InvalidVersion2(self):
        with self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with_syntax = 4.5:
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
            assert result.Column == 17
