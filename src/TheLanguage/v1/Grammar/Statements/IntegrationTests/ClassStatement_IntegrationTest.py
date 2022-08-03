# ----------------------------------------------------------------------
# |
# |  ClassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 10:51:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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
    from ....IntegrationTestHelpers import *
    from ..ClassStatement import *


# ----------------------------------------------------------------------
def test_AllDefaults():
    CompareResultsFromFile(str(ExecuteParserInfo(
        textwrap.dedent(
            """\
            mixin Mixin:
                pass

            interface Interface:
                pass

            class Simple:
                pass

            class WithExtends
                extends Simple
            :
                pass

            class WithUses
                uses Mixin
            :
                pass

            class WithImplements
                implements Interface
            :
                pass
            """,
        ),
        include_fundamental_types=False,
    )))


# ----------------------------------------------------------------------
def test_Visibility():
    CompareResultsFromFile(str(ExecuteParserInfo(
        textwrap.dedent(
            """\
            class Outer:
                public class PublicClass: pass
                protected class InternalClass: pass
                private class PrivateClass: pass
            """,
        ),
        include_fundamental_types=False,
    )))
