# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 14:40:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatement object"""

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
    from ..Common import Tokens as CommonTokens
    from ..Types.StandardType import InvalidTypeError, StandardType
    from ...GrammarPhrase import GrammarPhrase

    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class TypeAliasStatement(GrammarPhrase):
    """\
    Create a new type name.

    'using' <name> '=' <type>

    Examples:
        using PositiveInt = Int<min_value=0>
    """

    PHRASE_NAME                             = "Type Alias Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeAliasStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'using'
                    "using",

                    # <type>
                    CommonTokens.GenericName,

                    # '='
                    "=",

                    # <type>
                    DynamicPhrasesType.Types,

                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ValidateNodeSyntax(
        node: Node,
    ) -> Optional[bool]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # Validate the name
        leaf = cast(Leaf, nodes[1])
        name = cast(str, ExtractToken(leaf))

        if not StandardType.VALIDATION_EXPRESSION.match(name):
            raise InvalidTypeError.FromNode(leaf, name)
