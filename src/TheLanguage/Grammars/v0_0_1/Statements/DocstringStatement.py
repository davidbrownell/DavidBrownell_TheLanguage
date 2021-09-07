# ----------------------------------------------------------------------
# |
# |  DocstringStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 06:25:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DocstringStatement object"""

import os

from typing import Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.MultilineStatementBase import MultilineStatementBase
    from ...GrammarPhrase import GrammarPhrase
    from ....Parser.Phrases.DSL import Leaf, Node


# TODO: The lexer should not have knowledge of this statement; it should be part of the NodeInfo for the associated class/func/etc.

# ----------------------------------------------------------------------
class DocstringStatement(MultilineStatementBase):
    """\
    Documentation for a parent node.

    '<<<'
    <content>
    '>>>'

    Examples:
        <<<
        This is a docstring with one line.
        >>>

        <<<
        This is a
        multi-line
        docstring.
        >>>
    """

    PHRASE_NAME                             = "Docstring Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(DocstringStatement, self).__init__(
            self.PHRASE_NAME,
            "<<<",
            ">>>",
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _ValidateSyntaxImpl(
        self,
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # Persist the info
        object.__setattr__(node, "Info", value)
