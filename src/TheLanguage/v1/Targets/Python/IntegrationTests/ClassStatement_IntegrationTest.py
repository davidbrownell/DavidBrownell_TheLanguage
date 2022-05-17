# ----------------------------------------------------------------------
# |
# |  ClassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 11:37:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for class statements"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....IntegrationTestHelpers import *


# ----------------------------------------------------------------------
def test_Simple():
    CompareResultsFromFile(
        ExecutePythonTarget(
            textwrap.dedent(
                """\
                public class SimpleClass:
                    pass

                public struct SimpleStruct:
                    pass
                """,
            ),
            include_fundamental_types=False,
        ),
        file_ext=".py",
    )


# ----------------------------------------------------------------------
def test_Bases():
    CompareResultsFromFile(
        ExecutePythonTarget(
            textwrap.dedent(
                """\
                public class Base: pass
                public class Derived1 extends Base: pass

                public interface Interface1: pass
                public interface Interface2: pass

                public class Derived2
                    extends Derived1
                    implements Interface1, Interface2
                :
                    pass
                """,
            ),
            include_fundamental_types=False,
        ),
        file_ext=".py",
    )


# ----------------------------------------------------------------------
def test_UnusualOrdering():
    CompareResultsFromFile(
        ExecutePythonTarget(
            textwrap.dedent(
                """\
                # This is valid in the language, but not in Python
                class Derived extends Base:
                    pass

                class Base:
                    pass
                """,
            ),
            include_fundamental_types=False,
        ),
        file_ext=".py",
    )
