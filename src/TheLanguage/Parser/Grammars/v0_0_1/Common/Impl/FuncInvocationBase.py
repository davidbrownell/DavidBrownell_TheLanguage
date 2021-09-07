# ----------------------------------------------------------------------
# |
# |  FuncInvocationBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:45:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationBase object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import ArgumentsPhraseItem
    from .. import Tokens as CommonTokens

    from ....GrammarPhrase import GrammarPhrase

    from .....Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class FuncInvocationBase(GrammarPhrase):
    """\
    Base class for function invocations.

    <generic_name> <<Arguments>> <function_name> <function_args>

    Examples:
        Func1()
        Func2(a,)
        Func3(a, b, c)
        Func4(a, b, c=foo)
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        grammar_phrase_type: GrammarPhrase.Type,
    ):
        phrase_items = [
            # <generic_name>
            CommonTokens.GenericName,

            ArgumentsPhraseItem.Create(),
        ]

        if grammar_phrase_type == GrammarPhrase.Type.Statement:
            phrase_items.append(CommonTokens.Newline)

        super(FuncInvocationBase, self).__init__(
            grammar_phrase_type,
            CreatePhrase(
                name=phrase_name,
                item=phrase_items,
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ValidateSyntax(
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        nodes = ExtractSequence(node)
        assert len(nodes) in [2, 3], nodes

        # Func Name
        leaf = cast(Leaf, nodes[0])
        name = cast(str, ExtractToken(leaf))

        # Arguments
        arguments = ArgumentsPhraseItem.Extract(cast(Node, nodes[1]))
