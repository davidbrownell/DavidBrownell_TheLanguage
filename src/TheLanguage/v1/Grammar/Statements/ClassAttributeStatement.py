# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 12:17:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassAttributeStatement object"""

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
    from .ClassStatement import ClassStatement
    from .FuncDefinitionStatement import FuncDefinitionStatement

    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...Common.Diagnostics import CreateError, Diagnostics, Error

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegion, CreateRegions, GetPhrase
    from ...Parser.Statements import ClassAttributeStatement as ParserClassAttributeStatementModule


# ----------------------------------------------------------------------
InvalidClassAttributeError                  = CreateError(
    "'Attributes may only be used in class-like types"
)


# ----------------------------------------------------------------------
class ClassAttributeStatement(GrammarPhrase):
    PHRASE_NAME                             = "Class Attribute Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassAttributeStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # TODO: <attributes>?

                    # <visibility>?
                    OptionalPhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.RuntimeVariableName,

                    # ('=' <expression>)?
                    OptionalPhraseItem(
                        name="Initializer",
                        item=[
                            "=",
                            CommonTokens.PushIgnoreWhitespaceControl,
                            DynamicPhrasesType.Expressions,
                            CommonTokens.PopIgnoreWhitespaceControl,
                        ],
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _ExtractParserPhraseImpl(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5 # TODO: 6

            errors: List[Error] = []

            # TODO: <attributes>?
            keyword_initialization_node = None
            keyword_initialization_info = None

            no_initialization_node = None
            no_initialization_info = None

            no_serialize_node = None
            no_serialize_info = None

            no_compare_node = None
            no_compare_info = None

            is_override_node = None
            is_override_info = None

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            type_info = cast(ParserClassAttributeStatementModule.TypePhrase, GetPhrase(type_node))

            # <name>
            name_node = cast(AST.Leaf, nodes[4])
            name_info = ExtractToken(name_node)

            # ('=' <expression>)?
            initializer_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[3])))
            if initializer_node is None:
                initializer_info = None
            else:
                initializer_nodes = ExtractSequence(initializer_node)
                assert len(initializer_nodes) == 4

                initializer_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, initializer_nodes[2])))
                initializer_info = GetPhrase(initializer_node)

            class_capabilities = ClassStatement.GetParentClassCapabilities(node, FuncDefinitionStatement)

            if class_capabilities is None:
                errors.append(
                    InvalidClassAttributeError.Create(
                        region=CreateRegion(node),
                    ),
                )

            if errors:
                return Diagnostics(
                    errors=errors,
                )

            return ParserClassAttributeStatementModule.ClassAttributeStatement.Create(
                CreateRegions(
                    node,
                    visibility_node,
                    type_node,
                    name_node,
                    None, # documentation
                    initializer_node,
                    keyword_initialization_node,
                    no_initialization_node,
                    no_serialize_node,
                    no_compare_node,
                    is_override_node,
                ),
                class_capabilities,
                visibility_info,
                type_info,
                name_info,
                None, # documentation
                initializer_info,
                keyword_initialization_info,
                no_initialization_info,
                no_serialize_info,
                no_compare_info,
                is_override_info,
            )

        # ----------------------------------------------------------------------

        return Callback  # type: ignore
