# ----------------------------------------------------------------------
# |
# |  MethodDefinitionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 13:47:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for MethodDefinitionStatement.py"""

import os
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            Int Method1() immutable:
                pass

            public Int Method2() mutable:
                pass

            override Int Method3() immutable:
                pass

            protected override Int Method4():
                pass

            private static Char val Method5(
                pos:
                    Int a, Bool b,
                key:
                    Char c, Double d
            ):
                func1()
                func2()
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Abstract():
    assert Execute(
        textwrap.dedent(
            """\
            protected abstract Int Method1()
            abstract Int Method2() mutable

            abstract Int Method3(
                pos:
                    Int a,
                key:
                    Bool b, Char c
            )

            abstract Int Method4(
                pos:
                    Int a,
                key:
                    Bool b, Char c
            ) mutable
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Visibilities():
    assert Execute(
        textwrap.dedent(
            """\
            public abstract Int PublicMethod1()
            protected abstract Int ProtectedMethod2()
            private abstract Int PrivateMethod3()
            abstract Int DefaultMethod()
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_MethodTypes():
    assert Execute(
        textwrap.dedent(
            """\
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

            # The following method would resolve as a function without the trailing 'immutable'
            Int DefaultMethod() immutable:
                pass
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_ClassTypes():
    assert Execute(
        textwrap.dedent(
            """\
            abstract Int MutableMethod() mutable
            abstract Int ImmutableMethod() immutable
            abstract Int DefaultMethod()
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Statements():
    assert Execute(
        textwrap.dedent(
            """\
            virtual Int Method() mutable:
                Func1()
                Func2()
                Func3()
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Operators():
    assert Execute(
        textwrap.dedent(
            """\
            abstract Int __ToBool__()
            abstract Int __ToString__()
            abstract Int __Repr__()
            abstract Int __Clone__()
            abstract Int __Serialize__()

            abstract Int __Init__()
            abstract Int __PreInit__()

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
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_InvalidMethodNameError():
    with pytest.raises(InvalidMethodNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                abstract Int method()
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "'method' is not a valid method name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "method"
    assert ex.Line == 1
    assert ex.Column == 14
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_InvalidOperatorNameError():
    with pytest.raises(InvalidOperatorNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                abstract Int __OperatorDoesNotExist__()
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "'__OperatorDoesNotExist__' is not a valid operator name."
    assert ex.Name == "__OperatorDoesNotExist__"
    assert ex.Line == 1
    assert ex.Column == 14
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_InvalidClassRestrictionError():
    with pytest.raises(InvalidClassRestrictionError) as ex:
        Execute(
            textwrap.dedent(
                """\
                static Int NotValid() immutable:
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Class restrictions may not be applied to methods marked as 'static'."
    assert ex.Line == 1
    assert ex.Column == 23
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len("immutable")


# ----------------------------------------------------------------------
def test_StatementsRequiredError():
    with pytest.raises(StatementsRequiredError) as ex:
        Execute(
            textwrap.dedent(
                """\
                final Int NeedsStatements() immutable
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Statements are required for methods not marked as 'abstract'."
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == 1


# ----------------------------------------------------------------------
def test_StatementsUnexpectedError():
    with pytest.raises(StatementsUnexpectedError) as ex:
        Execute(
            textwrap.dedent(
                """\
                abstract Int ShouldNotHaveStatements() immutable:
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Statements can not be provided for methods marked as 'abstract' (use 'virtual' instead)."
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 3
    assert ex.ColumnEnd == 1
