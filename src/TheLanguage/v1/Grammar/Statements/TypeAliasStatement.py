# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 12:50:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatement object"""

import os

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import ConstraintParametersFragment
    from ..Common import TemplateParametersFragment
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import (
        CreateRegions,
        Error,
        GetParserInfo,
    )

    from ...Parser.ParserInfos.Statements.TypeAliasStatementParserInfo import (
        TypeAliasStatementParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class TypeAliasStatement(GrammarPhrase):
    PHRASE_NAME                             = "Type Alias Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeAliasStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <visibility>?
                OptionalPhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # <name>
                CommonTokens.TypeName,

                # Template Parameters, Constraints
                CommonTokens.PushIgnoreWhitespaceControl,

                # <template_parameters>?
                OptionalPhraseItem(
                    TemplateParametersFragment.Create(),
                ),

                # <constraint_parameters>?
                OptionalPhraseItem(
                    ConstraintParametersFragment.Create(),
                ),

                CommonTokens.PopIgnoreWhitespaceControl,

                # '='
                "=",

                # <type>
                DynamicPhrasesType.Types,

                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 9

            errors: List[Error] = []

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <name>
            name_leaf = cast(AST.Leaf, nodes[1])
            name_info = CommonTokens.TypeName.Extract(name_leaf)  # type: ignore

            # <template_parameters>?
            templates_info = None

            templates_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))
            if templates_node is not None:
                result = TemplateParametersFragment.Extract(templates_node)

                if isinstance(result, list):
                    errors += result
                else:
                    templates_info = result

            # <constraint_parameters>?
            constraints_info = None

            constraints_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if constraints_node is not None:
                result = ConstraintParametersFragment.Extract(constraints_node)

                if isinstance(result, list):
                    errors += result
                else:
                    constraints_info = result

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[7])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            if errors:
                return errors

            return TypeAliasStatementParserInfo.Create(
                CreateRegions(node, visibility_node, name_leaf),
                visibility_info,
                name_info,
                templates_info,
                constraints_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Callback
