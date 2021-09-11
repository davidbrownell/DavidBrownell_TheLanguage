# ----------------------------------------------------------------------
# |
# |  LambdaExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 11:10:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LambdaExpression object"""

import os

from typing import cast, Any, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import ParametersPhraseItem
    from ...GrammarPhrase import GrammarPhrase
    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class LambdaExpression(GrammarPhrase):
    """\
    Creates a temporary function.

    'lambda' <parameters_phrase_item> ':' <expr>

    Examples:
        lambda (Int a, Char b): b * a
        lambda (): 10
    """

    PHRASE_NAME                             = "Lambda Expression"

    # TODO: Captures

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(GrammarPhrase.NodeInfo):
        Parameters: Any                     # Defined in ParametersPhraseItem.py
        Expression: Union[Leaf, Node]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(LambdaExpression.NodeInfo, self).__post_init__(
                Expression=lambda expr: expr.Type.Name,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(LambdaExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'lambda'
                    "lambda",

                    # <parameters_phrase_item>
                    ParametersPhraseItem.Create(),

                    # ':'
                    ":",

                    # <expr>
                    DynamicPhrasesType.Expressions,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 4

        # Parameters
        parameters = ParametersPhraseItem.Extract(cast(Node, nodes[1]))

        # Expression
        expression = ExtractDynamic(cast(Node, nodes[3]))

        # Commit the info
        object.__setattr__(
            node,
            "Info",
            cls.NodeInfo(
                {},
                parameters,
                expression,
            ),
        )
