# ----------------------------------------------------------------------
# |
# |  StringStatements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 15:56:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""String-related statements"""

import os
import re

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarStatement import GrammarStatement

    from ...ParserImpl.MultifileParser import Node
    from ...ParserImpl.Statement import Statement
    from ...ParserImpl.Token import RegexToken


# ----------------------------------------------------------------------
class SimpleStringStatement(GrammarStatement):
    '''"Hello world"'''

    # ----------------------------------------------------------------------
    def __init__(self):
        super(SimpleStringStatement, self).__init__(
            GrammarStatement.Type.Expression,
            Statement(
                "Simple String",
                RegexToken("Simple String Token", re.compile(r'"(?P<value>(?:\\"|[^"])+)"')),
            ),
        )


# ----------------------------------------------------------------------
class TripleStringStatement(GrammarStatement):
    '''\
    """
    Hello
    world
    """
    '''

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TripleStringStatement, self).__init__(
            GrammarStatement.Type.Expression,
            Statement(
                "Triple String",
                RegexToken(
                    "Triple String Token",
                    re.compile(r'"""(?P<value>.+?)"""'),
                    is_multiline=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Lower(
        node: Node,
    ):
        # TODO
        pass


# ----------------------------------------------------------------------
class SimpleFormatStringStatement(GrammarStatement):
    """`Hello {name}`"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(SimpleFormatStringStatement, self).__init__(
            GrammarStatement.Type.Expression,
            Statement(
                "Simple Format String",
                RegexToken("Simple Format String Token", re.compile(r'`(?P<value>(?:\\`|[^`])+)`')),
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Lower(
        node: Node,
    ):
        # TODO
        pass


# ----------------------------------------------------------------------
class TripleFormatStringStatement(GrammarStatement):
    """\
    ```
    Hello
    {name}
    ```
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TripleFormatStringStatement, self).__init__(
            GrammarStatement.Type.Expression,
            Statement(
                "Triple Format String",
                RegexToken(
                    "Triple Format String Token",
                    re.compile(r"```(?P<value>.+?)```"),
                    is_multiline=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Lower(
        node: Node,
    ):
        # TODO
        pass
