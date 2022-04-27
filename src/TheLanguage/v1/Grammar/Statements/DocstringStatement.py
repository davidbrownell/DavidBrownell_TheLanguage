# ----------------------------------------------------------------------
# |
# |  DocstringStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-26 15:33:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DocstringStatement object"""

import os

from typing import cast, Optional, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import Tokens as CommonTokens
    from ..Common.Impl import MultilineFragmentImpl

    from ...Lexer.Phrases.DSL import DynamicPhrasesType, ExtractSequence


# ----------------------------------------------------------------------
class DocstringStatement(GrammarPhrase):
    PHRASE_NAME                             = "Docstring Statement"
    HEADER                                  = "<<<"
    FOOTER                                  = ">>>"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(DocstringStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                MultilineFragmentImpl.Create(self.HEADER, self.FOOTER),
                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @classmethod
    def GetDocstringInfo(
        cls,
        node: AST.Node,
    ) -> Optional[Tuple[AST.Leaf, str]]:
        return getattr(node, cls._DOCSTRING_INFO_ATTRIBUTE_NAME, None)

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        result = MultilineFragmentImpl.Extract(cls.HEADER, cls.FOOTER, cast(AST.Node, nodes[0]))
        if isinstance(result, list):
            return result

        # Associate this information with the node
        object.__setattr__(node, cls._DOCSTRING_INFO_ATTRIBUTE_NAME, result)

        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _DOCSTRING_INFO_ATTRIBUTE_NAME          = "_docstring_info"
