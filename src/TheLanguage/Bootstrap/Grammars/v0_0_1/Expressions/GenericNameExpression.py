# ----------------------------------------------------------------------
# |
# |  FuncNameExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 12:58:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncNameExpression object"""

import os

from typing import Callable, cast, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common import ConstraintArgumentsPhraseItem
    from ..Common import TemplateArgumentsPhraseItem

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions
    from ....Parser.Expressions.GenericNameExpressionParserInfo import GenericNameExpressionParserInfo


# ----------------------------------------------------------------------
class GenericNameExpression(GrammarPhrase):
    """\
    A generic name.
    """

    PHRASE_NAME                             = "Generic Name Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GenericNameExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <name>
                    CommonTokens.GenericName,

                    # <template_arguments>?
                    OptionalPhraseItem.Create(
                        name="Template Arguments",
                        item=TemplateArgumentsPhraseItem.Create(),
                    ),

                    # <constraint arguments>?
                    OptionalPhraseItem.Create(
                        name="Constraint Arguments",
                        item=ConstraintArgumentsPhraseItem.Create(),
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        # <func_name>
        func_name_leaf = cast(AST.Leaf, nodes[0])
        func_name_info = cast(str, ExtractToken(func_name_leaf))

        # <template_arguments>?
        template_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
        if template_arguments_node is None:
            template_arguments_info = None
        else:
            template_arguments_info = TemplateArgumentsPhraseItem.ExtractParserInfo(template_arguments_node)

        # <constraint_arguments>?
        constraint_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if constraint_arguments_node is None:
            constraint_arguments_info = None
        else:
            constraint_arguments_info = ConstraintArgumentsPhraseItem.ExtractParserInfo(constraint_arguments_node)

        return GenericNameExpressionParserInfo(
            CreateParserRegions(
                node,
                func_name_leaf,
                template_arguments_node,
                constraint_arguments_node,
            ),  # type: ignore
            func_name_info,
            template_arguments_info,
            constraint_arguments_info,
        )
