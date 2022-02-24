# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 12:35:24
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..FuncDefinitionStatement import *


# ----------------------------------------------------------------------
def test_FuncNoParameters():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Func1():
                pass

            Int var Func2(): pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncSingleParameter():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Func1(Bool b1):
                pass

            Int var Func2(Bool view b2): pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncMultipleParameters():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Func1(Bool b1, Char c1, Double d1):
                pass

            Int var Func2(
                key:
                    Bool b2,
                    Char c2,
                    Double d2,
            ): pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncMultipleStatements():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Func():
                <<<
                Functions may
                    be
                decorated with
                    docstrings!
                >>>

                pass
                pass

                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncVisibility():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_FuncAsync():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Char FuncAsync():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncGenerator():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Char Func...():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncExceptional():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Char Func?():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FuncFullDecorations():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Char Func1Async...(): pass
            Char Func2Async?(): pass
            Char Func3...?(): pass
            Char Func4Async...?(): pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
class TestNewStyleFlags(object):
    # ----------------------------------------------------------------------
    def test_Positional(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(pos: Int a, Int b, Int c):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_Keyword(self):
        CompareResultsFromFile(str(Execute(
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
        )))

    # ----------------------------------------------------------------------
    def test_Any(self):
        CompareResultsFromFile(str(Execute(
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
        )))

    # ----------------------------------------------------------------------
    def test_All(self):
        CompareResultsFromFile(str(Execute(
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
        )))

    # ----------------------------------------------------------------------
    def test_PositionalAndKeyword(self):
        CompareResultsFromFile(str(Execute(
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
        )))

    # ----------------------------------------------------------------------
    def test_KeywordAndAny(self):
        CompareResultsFromFile(str(Execute(
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
        )))

    # ----------------------------------------------------------------------
    def test_DefaultValues(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(Int a, Bool b=False, Char c=value):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_ParameterGroupDuplicateError(self):
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
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The parameter group 'pos' has already been specified."
        assert ex.Region.Begin.Line == 4
        assert ex.Region.Begin.Column == 5
        assert ex.Region.End.Line == 4
        assert ex.Region.End.Column == 8


# ----------------------------------------------------------------------
class TestTraditionalParameterFlags(object):
    # ----------------------------------------------------------------------
    def test_Positional(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(Int a, Int b, /, Int c):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_Keyword(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(Int a, *, Int b, Int c):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_PositionalAndKeyword(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(Int a, /, Int b, Int c, *, Int d, Int e):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_DefaultValues(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                Int Func(Int a, *, Int b=value1, Int c=value2):
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_DelimiterOrderError(self):
        with pytest.raises(TraditionalDelimiterOrderError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, *, Int b, /, Int c):
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') must appear before the keyword delimiter ('*')."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 27
        assert ex.Region.End.Line == 1
        assert ex.Region.End.Column == 28

    # ----------------------------------------------------------------------
    def test_DuplicatePositionalError(self):
        with pytest.raises(TraditionalDelimiterDuplicatePositionalError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, /, Int b, /, Int c):
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') may only appear once in a list of parameters."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 27
        assert ex.Region.End.Line == 1
        assert ex.Region.End.Column == 28

    # ----------------------------------------------------------------------
    def test_DuplicateKeywordError(self):
        with pytest.raises(TraditionalDelimiterDuplicateKeywordError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, *, Int b, *, Int c):
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The keyword delimiter ('*') may only appear once in a list of parameters."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 27
        assert ex.Region.End.Line == 1
        assert ex.Region.End.Column == 28

    # ----------------------------------------------------------------------
    def test_DelimiterPositionalError(self):
        with pytest.raises(TraditionalDelimiterPositionalError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(/, Int a, Int b, Int c):
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The positional delimiter ('/') must appear after at least 1 parameter."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 10
        assert ex.Region.End.Line == 1
        assert ex.Region.End.Column == 11

    # ----------------------------------------------------------------------
    def test_DelimiterKeywordError(self):
        with pytest.raises(TraditionalDelimiterKeywordError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    Int Func(Int a, Int b, Int c, *):
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "The keyword delimiter ('*') must appear before at least 1 parameter."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 31
        assert ex.Region.End.Line == 1
        assert ex.Region.End.Column == 32


# ----------------------------------------------------------------------
def test_RequiredParameterAfterDefaultError():
    with pytest.raises(RequiredParameterAfterDefaultError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(Int a=one, Bool bee):
                    pass
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "A required parameter may not appear after a parameter with a default value."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 21
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 29


# ----------------------------------------------------------------------
def test_MethodNoParameters():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                Int Method1():
                    pass

                Int var Method2():
                    pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MethodSingleParameter():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                Int Method1(Bool b1):
                    pass

                Int var Method2(Bool view b2):
                    pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MethodMultipleParameters():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                Int Method1(Bool b1, Char c1, Double d1):
                    pass

                Int var Method2(Bool var b2, Char view c2, Double val d2):
                    pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MethodMultipleStatements():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                Int Method():
                    <<<
                    A method may
                    have docstrings!
                    >>>

                    pass

                    pass
                    pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MethodWithVisibility():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_MethodType():
    CompareResultsFromFile(str(Execute(
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

            # TODO: No support for deferred yet
            # primitive Bar():
            #     Int DeferredMethod()
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_ClassModifier():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_Abstract():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                public abstract Int PublicAbstractMethod()
                protected abstract Bool ProtectedAbstractMethod()
                private abstract Char PrivateAbstractMethod()

                private abstract Char PrivateAbstractMethodWithDocstring():
                    <<<
                    An abstract method can have a docstring, but cannot have statements.
                    >>>
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Operators():
    CompareResultsFromFile(str(Execute(
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
                abstract Int __LessOrEqual__()
                abstract Int __Greater__()
                abstract Int __GreaterOrEqual__()

                abstract Int __And__()
                abstract Int __Or__()
                abstract Int __Not__()

                abstract Int __Add__()
                abstract Int __Subtract__()
                abstract Int __Multiply__()
                abstract Int __Divide__()
                abstract Int __DivideFloor__()
                abstract Int __Power__()
                abstract Int __Modulo__()
                abstract Int __Positive__()
                abstract Int __Negative__()

                abstract Int __AddInplace__()
                abstract Int __SubtractInplace__()
                abstract Int __MultiplyInplace__()
                abstract Int __DivideInplace__()
                abstract Int __DivideFloorInplace__()
                abstract Int __PowerInplace__()
                abstract Int __ModuloInplace__()

                abstract Int __BitShiftLeft__()
                abstract Int __BitShiftRight__()
                abstract Int __BitAnd__()
                abstract Int __BitOr__()
                abstract Int __BitXor__()
                abstract Int __BitFlip__()

                abstract Int __BitShiftLeftInplace__()
                abstract Int __BitShiftRightInplace__()
                abstract Int __BitAndInplace__()
                abstract Int __BitOrInplace__()
                abstract Int __BitXorInplace__()
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FunctionWithinFunction():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Outer():
                Int Inner():
                    pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_FunctionWithinMethod():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            class Foo():
                Int Outer():
                    Int Inner():
                        pass
            """,
        ),
    )))


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
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "'__InvalidOperatorName__' is not a valid operator name."
    assert ex.Name == "__InvalidOperatorName__"
    assert ex.Region.Begin.Line == 2
    assert ex.Region.Begin.Column == 9
    assert ex.Region.End.Line == 2
    assert ex.Region.End.Column == ex.Region.Begin.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_NoneReturnType():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            None StandardFunc():
                pass

            class Foo():
                None StandardMethod():
                    pass
            """,
        ),
    )))
