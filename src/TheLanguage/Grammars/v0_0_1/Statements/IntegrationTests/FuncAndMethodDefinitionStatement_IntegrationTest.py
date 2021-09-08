# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-01 10:09:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for FuncAndMethodDefinitionStatement.py"""

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
    from ..FuncAndMethodDefinitionStatement import *
    from ...Common.AutomatedTests import Execute

    from ...Common.ParametersPhraseItem import (
        NewStyleParameterGroupDuplicateError,
        TraditionalDelimiterDuplicatePositionalError,
        TraditionalDelimiterDuplicateKeywordError,
        TraditionalDelimiterKeywordError,
        TraditionalDelimiterOrderError,
        TraditionalDelimiterPositionalError,
        RequiredParameterAfterDefaultError,
    )


# ----------------------------------------------------------------------
def test_FunctionNoArgs():
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
def test_FunctionSingleArg():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func1(Bool b1):
                    pass

                Int var Func2(Bool view b2):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FunctionMultipleArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Func1(Bool b1, Char c1, Double d1):
                    pass

                Int var Func2(Bool var b2, Char view c2, Double val d2):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FunctionMultipleStatements():
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
def test_FunctionWithVisibility():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                public Int PublicFunc():
                    pass

                protected Bool ProtectedFunc():
                    pass

                private Char PrivateFunc():
                    pass

                Double DefaultFunc():
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodNoArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int Method1():
                        pass

                    Int var Method2():
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodSingleArg():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int Method1(Bool b1):
                        pass

                    Int var Method2(Bool view b2):
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodMultipleArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int Method1(Bool b1, Char c1, Double d1):
                        pass

                    Int var Method2(Bool var b2, Char view c2, Double val d2):
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodMultipleStatements():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int Method():
                        pass

                        pass
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodWithVisibility():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    public Int PublicFunc():
                        pass

                    protected Bool ProtectedFunc():
                        pass

                    private Char PrivateFunc():
                        pass

                    Double DefaultFunc():
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MethodType():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    standard Int StandardMethod():
                        pass

                    static Int StaticMethod():
                        pass

                    abstract Int AbstractMethod()

                    virtual Int VirtualMethod():
                        pass

                    override Int OverrideMethod():
                        pass

                    final Int FinalMethod():
                        pass

                    Int DefaultMethod():
                        pass

                primitive Bar():
                    deferred Int DeferredMethod()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_ClassModifier():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                mutable class Foo():
                    Int ImmutableMethod() immutable:
                        pass

                    Int MutableMethod() mutable:
                        pass

                    Int DefaultMethod():
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Abstract():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    public abstract Int PublicAbstractMethod()
                    protected abstract Bool ProtectedAbstractMethod()
                    private abstract Char PrivateAbstractMethod()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Deferred():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                primitive Foo():
                    public deferred Int PublicDeferredMethod()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Operators():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    abstract Int __ToBool__()
                    abstract Int __ToString__()
                    abstract Int __Repr__()
                    abstract Int __Clone__()
                    abstract Int __Serialize__()

                    abstract Int __Init__()
                    abstract Int __PostInit__()

                    abstract Int __GetAttribute__()
                    abstract Int __Call__()
                    abstract Int __Cast__()
                    abstract Int __Index__()

                    abstract Int __Contains__()
                    abstract Int __Length__()
                    abstract Int __Iter__()
                    abstract Int __AtEnd__()

                    abstract Int __Compare__()
                    abstract Int __Equal__()
                    abstract Int __NotEqual__()
                    abstract Int __Less__()
                    abstract Int __LessEqual__()
                    abstract Int __Greater__()
                    abstract Int __GreaterEqual__()

                    abstract Int __And__()
                    abstract Int __Or__()
                    abstract Int __Not__()

                    abstract Int __Add__()
                    abstract Int __Subtract__()
                    abstract Int __Multiply__()
                    abstract Int __Divide__()
                    abstract Int __DivideFloor__()
                    abstract Int __Power__()
                    abstract Int __Mod__()
                    abstract Int __Positive__()
                    abstract Int __Negative__()

                    abstract Int __AddInplace__()
                    abstract Int __SubtractInplace__()
                    abstract Int __MultiplyInplace__()
                    abstract Int __DivideInplace__()
                    abstract Int __DivideFloorInplace__()
                    abstract Int __PowerInplace__()
                    abstract Int __ModInplace__()

                    abstract Int __ShiftLeft__()
                    abstract Int __ShiftRight__()
                    abstract Int __BitAnd__()
                    abstract Int __BitOr__()
                    abstract Int __BitXor__()
                    abstract Int __BitFlip__()

                    abstract Int __ShiftLeftInplace__()
                    abstract Int __ShiftRightInplace__()
                    abstract Int __BitAndInplace__()
                    abstract Int __BitOrInplace__()
                    abstract Int __BitXorInplace__()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FunctionWithinFunction():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Int Outer():
                    Int Inner():
                        pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FunctionWithinMethod():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int Outer():
                        Int Inner():
                            pass
                """,
            ),
        ),
    )


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
    def test_NewStyleParameterGroupDuplicateError(self):
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


# ----------------------------------------------------------------------
class TestTraditionalParameterFlags(object):
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
    def test_TraditionalDelimiterOrderError(self):
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
    def test_TraditionalDelimiterDuplicatePositionalError(self):
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
    def test_TraditionalDelimiterDuplicateKeywordError(self):
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
    def test_TraditionalDelimiterPositionalError(self):
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
    def test_TraditionalDelimiterKeywordError(self):
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
def test_InvalidOperatorNameError():
    with pytest.raises(InvalidOperatorNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int __InvalidOperatorName__():
                        pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "'__InvalidOperatorName__' is not a valid operator name."
    assert ex.Name == "__InvalidOperatorName__"
    assert ex.Line == 2
    assert ex.Column == 9
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_RequiredParameterAfterDefaultError():
    with pytest.raises(RequiredParameterAfterDefaultError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(Int a=1, Bool bee):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "A required parameter may not appear after a parameter with a default value."
    assert ex.Line == 1
    assert ex.Column == 19
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == 27
