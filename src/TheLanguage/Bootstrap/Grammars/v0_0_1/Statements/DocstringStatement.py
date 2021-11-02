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
    from ...GrammarInfo import GrammarPhrase
    from ....Lexer.Phrases.DSL import Leaf, Node


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
    @staticmethod
    @Interface.override
    def _GetDynamicContentImpl(
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[GrammarPhrase.GetDynamicContentResult]:
        # Nothing dynamic about the content
        return None
