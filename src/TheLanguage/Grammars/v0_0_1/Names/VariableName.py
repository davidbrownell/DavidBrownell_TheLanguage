# ----------------------------------------------------------------------
# |
# |  VariableName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:12:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableName object"""

import os

from typing import cast, Dict, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.ParserInterfaces.Names.VariableNameLexerInfo import VariableNameLexerInfo

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class VariableName(GrammarPhrase):
    """\
    A variable name

    <name>

    Examples:
        foo
        bar
    """

    PHRASE_NAME                             = "Variable Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableName, self).__init__(
            GrammarPhrase.Type.Name,
            CreatePhrase(
                name=self.PHRASE_NAME,

                # Note that this needs to be a sequence rather than just the name as this is the only
                # way to ensure that the validation below is invoked. If just the name, there would
                # be nothing to tie the token to this phrase.
                item=[CommonTokens.GenericName],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        token_lookup: Dict[str, Union[Leaf, Node]] = {
            "self": node,
        }

        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        name_leaf = cast(Leaf, nodes[0])
        name = cast(str, ExtractToken(name_leaf))
        token_lookup["Name"] = name_leaf

        # Commit the data
        object.__setattr__(
            node,
            "Info",
            # pylint: disable=too-many-function-args
            VariableNameLexerInfo(
                token_lookup,
                name,
            ),
        )
