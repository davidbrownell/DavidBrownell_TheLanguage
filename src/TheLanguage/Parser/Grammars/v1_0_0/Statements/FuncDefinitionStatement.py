# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 15:04:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionStatement object"""

import os
import re

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidFuncError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid function name; names must start with an uppercase letter and be at least 2 characters.")


# ----------------------------------------------------------------------
class FuncDefinitionStatement(GrammarPhrase):
    """\
    Defines a function.

    <visibility>? <type> <name> '(' (<type> <name> (<type> <name> ',')* ','?)* ')' ':'
        <statement>+

    Examples:
        Int Foo():
            pass

        public Char var Foo(Int a, Char b):
            pass
    """

    NODE_NAME                               = "Func Definition Statement"
    VALIDATION_EXPRESSION                   = re.compile(r"^_?[A-Z][a-zA-Z0-9_\.]+(?!<__)$")

    # ----------------------------------------------------------------------
    def __init__(self):
        parameter_item = PhraseItem(
            name="Parameter",
            item=[
                DynamicPhrasesType.Types,
                DynamicPhrasesType.Names,
            ],
        )

        super(FuncDefinitionStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <type> (return)
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.GenericName,

                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # (<type> <name> (',' <type> <name>)* ','?)*
                    PhraseItem(
                        name="Parameters",
                        item=[
                            # <type> <name>
                            parameter_item,

                            # (',' <type> <name>)*
                            PhraseItem(
                                name="Comma and Element",
                                item=[
                                    ",",
                                    parameter_item,
                                ],
                                arity="*",
                            ),

                            # ','?
                            PhraseItem(
                                name="Trailing Comma",
                                item=",",
                                arity="?",
                            ),
                        ],
                        arity="?",
                    ),

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",

                    # ':'
                    ":",
                    CommonTokens.Newline,
                    CommonTokens.Indent,

                    # <statement>+
                    PhraseItem(
                        name="Statements",
                        item=DynamicPhrasesType.Statements,
                        arity="+",
                    ),

                    # End
                    CommonTokens.Dedent,
                ],
            ),
        )


    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        nodes = ExtractSequence(node)
        assert len(nodes) == 13

        name, leaf = nodes[2]  # type: ignore

        if not cls.VALIDATION_EXPRESSION.match(name):
            raise InvalidFuncError.FromNode(leaf, name)