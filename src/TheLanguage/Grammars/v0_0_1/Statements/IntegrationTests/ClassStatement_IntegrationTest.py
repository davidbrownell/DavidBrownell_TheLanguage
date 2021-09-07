# ----------------------------------------------------------------------
# |
# |  ClassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 09:22:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ClassStatement.py"""

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
    from ..ClassStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_NoBases():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                public class PublicClass():
                    pass

                protected class ProtectedClass():
                    pass

                private class PrivateClass():
                    pass

                class DefaultClass():
                    pass

                # ----------------------------------------------------------------------
                public exception PublicException():
                    pass

                exception DefaultException():
                    pass

                # ----------------------------------------------------------------------
                public enum PublicEnum():
                    pass

                protected interface ProtectedInterface():
                    pass

                private mixin PrivateMixin():
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
                public class PublicClass():
                    pass
                    pass
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithBase():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1(public Base1):
                    pass

                class Class2(Base2):
                    pass

                class Class3(
                    protected
                    Base3,
                ):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithInterface():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1() implements Interface1:
                    pass

                class Class2() implements Interface2,:
                    pass

                class Class3()
                    implements Interface3
                :
                    pass

                class Class4()
                    implements Interface4,
                :
                    pass

                class Class5()
                    implements public Interface5
                :
                    pass

                class Class6() implements (Interface6):
                    pass

                class Class7()
                    implements (
                        Interface7,
                    )
                :
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithInterfaces():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1() implements Interface1A, Interface1B:
                    pass

                class Class2() implements Interface2A, Interface2B,:
                    pass

                class Class3() implements (Interface3A, Interface3B):
                    pass

                class Class4() implements (Interface4A, Interface4B,):
                    pass

                class Class5() implements (
                    Interface5A,
                    Interface5B
                ):
                    pass

                class Class6() implements (
                    protected Interface6A,
                    public Interface6B,
                ):
                    pass

                class Class7() implements(
                    Interface7A, Interface7B,
                        Interface7C,
                            Interface7D,
                    Interface7E,
                ):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithMixin():
    # Mixins are similar to interfaces, so we don't have to go through a comprehensive set of tests
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1() uses Mixin1:
                    pass

                class Class2() uses Mixin2,:
                    pass

                class Class3() uses (
                    Mixin3,
                ):
                    pass

                class Class4() uses (
                    public Mixin4,
                ):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithMixins():
    # Mixins are similar to interfaces, so we don't have to go through a comprehensive set of tests
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1() uses Mixin1A, Mixin1B:
                    pass

                class Class2() uses Mixin2A, Mixin2B,:
                    pass

                class Class3() uses (Mixin3A, Mixin3B):
                    pass

                class Class4() uses (Mixin4A, Mixin4B,):
                    pass

                class Class5() uses (
                    Mixin5A,
                    Mixin5B
                ):
                    pass

                class Class6() uses (
                    protected Mixin6A,
                    public Mixin6B,
                ):
                    pass

                class Class7() uses(
                    Mixin7A, Mixin7B,
                        Mixin7C,
                            Mixin7D,
                    Mixin7E,
                ):
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Complex():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Class1(Base1) implements Interface1:
                    pass

                class Class2(Base2) uses Mixin2:
                    pass

                class Class3(Base3) implements Interface3, uses Mixin3:
                    pass

                class Class4(Base4) uses Mixin4, implements Interface4A, Interface4B,:
                    pass

                protected immutable class Class5(Base5)
                    implements (
                        Interface5A,
                        Interface5B,
                    )
                    uses (
                        public Mixin5A,
                        protected Mixin5B,
                        private Mixin5C,
                    )
                :
                    pass
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_DuplicateInterfacesTypeError():
    with pytest.raises(DuplicateInterfacesTypeError) as ex:
        Execute(
            textwrap.dedent(
                """\
                class Class(Base1) uses Mixin1, uses Mixin2:
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The base type indicator 'uses' may only appear once."
    assert ex.Type == "uses"
    assert ex.Line == 1
    assert ex.Column == 33
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Type)


# ----------------------------------------------------------------------
def test_MultipleBasesError():
    with pytest.raises(MultipleBasesError) as ex:
        Execute(
            textwrap.dedent(
                """\
                class BadClass(Base1, Base2):
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Classes can have only one base class; consider using mixins and interfaces instead."
    assert ex.Line == 1
    assert ex.Column == 16
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == 28
