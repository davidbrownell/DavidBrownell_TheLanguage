# ----------------------------------------------------------------------
# |
# |  ClassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 12:58:39
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..ClassStatement import *


# ----------------------------------------------------------------------
def test_NoBases():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_MultipleStatements():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            public class PublicClass():
                pass
                pass
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_WithBase():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_WithInterface():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_WithInterfaces():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_WithMixin():
    # Mixins are similar to interfaces, so we don't have to go through a comprehensive set of tests
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_WithMixins():
    # Mixins are similar to interfaces, so we don't have to go through a comprehensive set of tests
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_Complex():
    CompareResultsFromFile(str(Execute(
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
    )))


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
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "Classes can have only one base class; consider using interfaces, mixins, and traits instead."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 16
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 28


# ----------------------------------------------------------------------
def test_DuplicateBaseTypeError():
    with pytest.raises(DuplicateBaseTypeError) as ex:
        Execute(
            textwrap.dedent(
                """\
                class Class(Base1) uses Mixin1, uses Mixin2:
                    pass
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "The base type indicator 'uses' may appear only once."
    assert ex.Type == "uses"
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 33
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == ex.Region.Begin.Column + len(ex.Type)


# ----------------------------------------------------------------------
class TestStatementsPhraseItem(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                class Class():
                    <<<
                    This is the documentation for the class.
                    >>>
                    pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    @pytest.mark.skip("TODO: Depends on Compiler Statements")
    def test_RemovedStatements(self):
        CompareResultsFromFile(str(Execute(
            textwrap.dedent(
                """\
                class Class():
                    <<<
                    Docstrings are removed.
                    >>>

                    <<<!!!
                    Compiler statements are removed
                    !!!>>>

                    @AttributesAreRemoved1
                    @AttributesAreRemoved2
                    private Char PrivateFunc():
                        pass
                """,
            ),
        )))

    # ----------------------------------------------------------------------
    def test_InvalidDocumentation(self):
        with pytest.raises(InvalidDocstringError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    class Class():
                        if Foo:
                            <<<
                            This is not valid here.
                            >>>
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "Docstrings are not supported in this context."
        assert ex.Region.Begin.Line == 3
        assert ex.Region.Begin.Column == 9
        assert ex.Region.End.Line == 5
        assert ex.Region.End.Column == 12

    # ----------------------------------------------------------------------
    def test_MultipleDocstringsError(self):
        with pytest.raises(MultipleDocstringsError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    class Class():
                        <<<
                        This docstring is valid.
                        >>>
                        <<<
                        This docstring is not valid...
                        ...as there can only be one!
                        >>>
                        pass
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "There may only be one docstring within a scope."
        assert ex.Region.Begin.Line == 5
        assert ex.Region.Begin.Column == 5
        assert ex.Region.End.Line == 8
        assert ex.Region.End.Column == 8

    # ----------------------------------------------------------------------
    def test_MisplacedDocstringError1(self):
        with pytest.raises(MisplacedDocstringError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    class Class():
                        pass
                        <<<
                        This docstring is not valid...
                        ...as it is the 2nd statement.
                        >>>

                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "Docstrings must be the 1st statement within a scope; this is the '2nd' statement."
        assert ex.Region.Begin.Line == 3
        assert ex.Region.Begin.Column == 5
        assert ex.Region.End.Line == 6
        assert ex.Region.End.Column == 8

    # ----------------------------------------------------------------------
    def test_MisplacedDocstringError2(self):
        with pytest.raises(MisplacedDocstringError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    class Class():
                        pass

                        pass

                        pass



                        <<<
                        This docstring is not valid...
                        ...as it is the Nth statement.
                        >>>

                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "Docstrings must be the 1st statement within a scope; this is the '4th' statement."
        assert ex.Region.Begin.Line == 10
        assert ex.Region.Begin.Column == 5
        assert ex.Region.End.Line == 13
        assert ex.Region.End.Column == 8

    # ----------------------------------------------------------------------
    def test_ClassStatementsRequiredError(self):
        with pytest.raises(ClassStatementsRequiredError) as ex:
            Execute(
                textwrap.dedent(
                    """\
                    class Invalid():
                        <<<
                        A docstring cannot be the only statement within a class.
                        >>>
                    """,
                ),
                debug_string_on_exceptions=False,
            )

        ex = ex.value

        assert str(ex) == "Classes must have at least one statement."
        assert ex.Region.Begin.Line == 1
        assert ex.Region.Begin.Column == 16
        assert ex.Region.End.Line == 5
        assert ex.Region.End.Column == 1
