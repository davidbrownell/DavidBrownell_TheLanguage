# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 15:19:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncDefinitionStatement.py"""

import os
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
    from ..FuncDefinitionStatement import *
    from ...Common.AutomatedTests import Execute

    from ...Common.ParametersPhraseItem import (
        NewStyleParameterGroupDuplicateError,
        TraditionalDelimiterDuplicatePositionalError,
        TraditionalDelimiterDuplicateKeywordError,
        TraditionalDelimiterKeywordError,
        TraditionalDelimiterOrderError,
        TraditionalDelimiterPositionalError,
    )

    from ...Common.VisibilityModifier import InvalidVisibilityModifierError

    from ...Names.VariableName import InvalidVariableNameError
    from ...Types.StandardType import InvalidTypeError


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func1():
                    pass

                Int var Func2():
                    pass
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_SingleArg():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func1(Bool b):
                    pass

                Int var Func2(Bool view b):
                    pass
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_MultipleArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func1(Bool b, Char c, Double d):
                    pass

                Int var Func2(Bool var b, Char view c, Double val d):
                    pass
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_MultipleStatements():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func():
                    pass
                    pass

                    pass
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_WithVisibility():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                public Int Func1():
                    pass

                protected Bool Func2():
                    pass

                private Char Func3():
                    pass
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_InvalidVisibilityModifier():
    with pytest.raises(InvalidVisibilityModifierError) as ex:
        Execute(
            textwrap.dedent(
                """\
                probably Int Func():
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The visibility modifier 'probably' is not valid; values may be 'private', 'protected', 'public'."
    assert ex.Name == "probably"
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_InvalidFuncName():
    with pytest.raises(InvalidFuncNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int func():
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'func' is not a valid function name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "func"
    assert ex.Line == 1
    assert ex.Column == 5
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

# ----------------------------------------------------------------------
def test_InvalidParameterTypeName():
    with pytest.raises(InvalidTypeError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(
                    invalid name,
                ):
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'invalid' is not a valid type name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "invalid"
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

# ----------------------------------------------------------------------
def test_InvalidParameterName():
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(
                    Bool INVALID,
                ):
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'INVALID' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "INVALID"
    assert ex.Line == 2
    assert ex.Column == 10
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
class TestTraditionalFlags(object):
    # ----------------------------------------------------------------------
    def test_Positional(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, Int b, /, Int c):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_Keyword(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, *, Int b, Int c):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_PositionalAndKeyword(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, /, Int b, Int c, *, Int d, Int e):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_OrderError(self):
        with pytest.raises(TraditionalDelimiterOrderError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, *, Int b, /, Int c):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') must appear before the keyword delimiter ('*')."
        assert ex.Line == 1
        assert ex.Column == 27
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 28

    # ----------------------------------------------------------------------
    def test_DuplicatePositionalError(self):
        with pytest.raises(TraditionalDelimiterDuplicatePositionalError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, /, Int b, /, Int c):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') may only appear once in a list of parameters."
        assert ex.Line == 1
        assert ex.Column == 27
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 28

    # ----------------------------------------------------------------------
    def test_DuplicateKeywordError(self):
        with pytest.raises(TraditionalDelimiterDuplicateKeywordError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, *, Int b, *, Int c):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The keyword delimiter ('*') may only appear once in a list of parameters."
        assert ex.Line == 1
        assert ex.Column == 27
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 28

    # ----------------------------------------------------------------------
    def test_InvalidPositionalPlacementError(self):
        with pytest.raises(TraditionalDelimiterPositionalError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(/, Int a, Int b, Int c):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') must appear after at least 1 parameter."
        assert ex.Line == 1
        assert ex.Column == 10
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 11

    # ----------------------------------------------------------------------
    def test_InvalidKeywordPlacementError(self):
        with pytest.raises(TraditionalDelimiterKeywordError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, Int b, Int c, *):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The keyword delimiter ('*') must appear before at least 1 parameter."
        assert ex.Line == 1
        assert ex.Column == 31
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 32


# ----------------------------------------------------------------------
class TestNewStyleFlags(object):

    # ----------------------------------------------------------------------
    def test_Positional(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(pos: Int a, Int b, Int c):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_Any(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        any:
                            Int a,
                            Int b,
                            Int c,
                    ):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_Keyword(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        key:
                            Int a,
                                Int b,
                                    Int c,
                    ):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_PositionalAndKeyword(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        pos: Int a,
                        key:
                            Int b,
                            Int c,
                    ):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_KeywordAndAny(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        key:
                            Int a,
                                Int b
                        any:
                            Int c, Int var d
                    ):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_All(self):
        CompareResultsFromFile(
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        key:
                            Int a,
                                Int b
                        any:
                            Int c, Int var d
                        pos:
                            Char e
                    ):
                        pass
                    """,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    def test_DuplicateError(self):
        with pytest.raises(NewStyleParameterGroupDuplicateError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(
                        pos: Int a, Int b,
                        key: Int c
                        pos: Int d
                    ):
                        pass
                    """,
                )
            )

        ex = ex.value

        assert str(ex) == "The parameter group 'pos' has already been specified."
        assert ex.Line == 4
        assert ex.Column == 5
        assert ex.LineEnd == 4
        assert ex.ColumnEnd == 8
