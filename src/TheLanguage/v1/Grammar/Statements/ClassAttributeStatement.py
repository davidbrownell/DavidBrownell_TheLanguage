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

    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import AttributesFragment
    from ..Common import MutabilityModifier
    from ..Common.Errors import InvalidCompileTimeNameError
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
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        ErrorException,
        GetParserInfo,
    )

    from ...Parser.ParserInfos.Statements.ClassAttributeStatementParserInfo import (
        ClassAttributeStatementParserInfo,
        ExpressionParserInfo,
    )


# ----------------------------------------------------------------------
InvalidClassAttributeError                  = CreateError(
    "Attributes may only be used in class-like types",
)


# ----------------------------------------------------------------------
class ClassAttributeStatement(GrammarPhrase):
    PHRASE_NAME                             = "Class Attribute Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassAttributeStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <attributes>?
                OptionalPhraseItem(
                    AttributesFragment.Create(),
                ),

                # <visibility>?
                OptionalPhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # <type>
                DynamicPhrasesType.Expressions,

                # <name>
                CommonTokens.VariableName,

                # <mutability_modifier>?
                OptionalPhraseItem(
                    name="Mutability Modifier",
                    item=MutabilityModifier.CreatePhraseItem(),
                ),

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
            assert len(nodes) == 7

            errors: List[Error] = []

            # <attributes>?
            keyword_initialization_node = None
            keyword_initialization_info = None

            no_initialization_node = None
            no_initialization_info = None

            no_serialize_node = None
            no_serialize_info = None

            no_compare_node = None
            no_compare_info = None

            attributes_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if attributes_node is not None:
                for attribute in AttributesFragment.Extract(attributes_node):
                    supports_arguments = False

                    if attribute.name == "KeywordInit":
                        keyword_initialization_node = attribute.leaf
                        keyword_initialization_info = True
                    elif attribute.name == "NoInit":
                        no_initialization_node = attribute.leaf
                        no_initialization_info = True
                    elif attribute.name == "NoSerialize":
                        no_serialize_node = attribute.leaf
                        no_serialize_info = True
                    elif attribute.name == "NoCompare":
                        no_compare_node = attribute.leaf
                        no_compare_info = True
                    else:
                        errors.append(
                            AttributesFragment.UnsupportedAttributeError.Create(
                                region=CreateRegion(attribute.leaf),
                                name=attribute.name,
                            ),
                        )

                        continue

                    if not supports_arguments and attribute.arguments_node is not None:
                        errors.append(
                            AttributesFragment.UnsupportedArgumentsError.Create(
                                region=CreateRegion(attribute.arguments_node),
                                name=attribute.name,
                            ),
                        )

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[1])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            type_info = cast(ExpressionParserInfo, GetParserInfo(type_node))

            # <name>
            name_node = cast(AST.Leaf, nodes[3])
            name_info = CommonTokens.VariableName.Extract(name_node)  # type: ignore

            if CommonTokens.VariableName.IsCompileTime(name_info):  # type: ignore  # pylint: disable=not-callable
                raise ErrorException(
                    InvalidCompileTimeNameError.Create(
                        region=CreateRegion(name_node),
                        name=name_info,
                        type="attribute",
                    ),
                )

            # TODO: Get visibility information from name

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[10])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            # ('=' <expression>)?
            initializer_node = cast(Optional[AST.Node], ExtractOptional(cast(AST.Node, nodes[5])))
            if initializer_node is None:
                initializer_info = None
            else:
                initializer_nodes = ExtractSequence(initializer_node)
                assert len(initializer_nodes) == 4

                initializer_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, initializer_nodes[2])))
                initializer_info = GetParserInfo(initializer_node)

            class_capabilities = ClassStatement.GetParentClassCapabilities(node)

            if class_capabilities is None:
                errors.append(
                    InvalidClassAttributeError.Create(
                        region=CreateRegion(node),
                    ),
                )

            if errors:
                raise ErrorException(*errors)

            return ClassAttributeStatementParserInfo.Create(
                CreateRegions(
                    node,
                    name_node,
                    visibility_node,
                    None, # documentation
                    mutability_modifier_node,
                    keyword_initialization_node,
                    no_initialization_node,
                    no_serialize_node,
                    no_compare_node,
                ),
                name_info,
                visibility_info,
                class_capabilities,
                type_info,
                None, # documentation
                initializer_info,
                mutability_modifier_info,
                keyword_initialization_info,
                no_initialization_info,
                no_serialize_info,
                no_compare_info,
            )

        # ----------------------------------------------------------------------

        return Callback
