# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:12:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionStatement object"""

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
    from ..Common import FuncParametersFragment
    from ..Common import MutabilityModifier
    from ..Common import StatementsFragment
    from ..Common import TemplateParametersFragment
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Common.Impl import ModifierImpl

    from ...Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ...Parser.Parser import CreateRegion, CreateRegions, Error, GetPhrase
    from ...Parser.Phrases.Common.MethodModifier import MethodModifier
    from ...Parser.Phrases.Statements import FuncDefinitionStatement as FuncDefinitionStatementModule


# ----------------------------------------------------------------------
class FuncDefinitionStatement(GrammarPhrase):
    PHRASE_NAME                             = "Func Definition Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncDefinitionStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>?
                    OptionalPhraseItem(
                        AttributesFragment.Create(),
                    ),

                    # <visibility>?
                    OptionalPhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <method_type_modifier>?
                    OptionalPhraseItem(
                        name="Method Modifier",
                        item=CreateMethodModifierPhraseItem(),
                    ),

                    # <return_type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.RuntimeFuncName,

                    # Template Parameters, Captures
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <template_parameters>?
                    OptionalPhraseItem(
                        TemplateParametersFragment.Create(),
                    ),

                    # TODO: <captured_variables>?

                    CommonTokens.PopIgnoreWhitespaceControl,

                    # <parameters>
                    FuncParametersFragment.Create(),

                    # <mutability_modifier>?
                    OptionalPhraseItem(
                        name="Mutability Modifier",
                        item=MutabilityModifier.CreatePhraseItem(),
                    ),

                    # Statements or None
                    (
                        StatementsFragment.Create(),
                        CommonTokens.Newline,
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserPhrase(  # pylint: disable=too-many-statements
        cls,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:
        # ----------------------------------------------------------------------
        def Callback():  # pylint: disable=too-many-locals
            nodes = ExtractSequence(node)
            assert len(nodes) == 11 # TODO: 12

            errors: List[Error] = []

            # <attributes>?
            is_deferred_node = None
            is_deferred_info = None

            is_exceptional_node = None
            is_exceptional_info = None

            is_generator_node = None
            is_generator_info = None

            is_reentrant_node = None
            is_reentrant_info = None

            is_scoped_node = None
            is_scoped_info = None

            is_static_node = None
            is_static_info = None

            attributes_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if attributes_node is not None:
                result = AttributesFragment.Extract(attributes_node)

                assert isinstance(result, list)
                assert result

                if isinstance(result[0], Error):
                    errors += cast(List[Error], result)
                else:
                    for attribute in cast(List[AttributesFragment.AttributeData], result):
                        supports_arguments = False

                        if attribute.name == "Deferred":
                            is_deferred_node = attribute.leaf
                            is_deferred_info = True
                        elif attribute.name == "Exceptional":
                            is_exceptional_node = attribute.leaf
                            is_exceptional_info = True
                        elif attribute.name == "Generator":
                            is_generator_node = attribute.leaf
                            is_generator_info = True
                        elif attribute.name == "Reentrant":
                            is_reentrant_node = attribute.leaf
                            is_reentrant_info = True
                        elif attribute.name == "Scoped":
                            is_scoped_node = attribute.leaf
                            is_scoped_info = True
                        elif attribute.name == "Static":
                            is_static_node = attribute.leaf
                            is_static_info = True
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
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <method_type_modifier>?
            method_type_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
            if method_type_modifier_node is None:
                method_type_modifier_info = None
            else:
                method_type_modifier_info = ExtractMethodModifier(method_type_modifier_node)

            # <return_type>
            return_type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            return_type_info = cast(FuncDefinitionStatementModule.TypePhrase, GetPhrase(return_type_node))

            # <name>
            name_leaf = cast(AST.Leaf, nodes[4])
            name_info = ExtractToken(name_leaf)

            # <template_parameters>?
            template_parameters_info = None

            template_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[6])))
            if template_parameters_node is not None:
                result = TemplateParametersFragment.Extract(template_parameters_node)

                if isinstance(result, list):
                    errors += result
                else:
                    template_parameters_info = result

            # TODO: <captured_variables>?
            captured_variables_node = None
            captured_variables_info = None

            # <parameters>
            parameters_node = cast(AST.Node, nodes[8])
            parameters_info = FuncParametersFragment.Extract(parameters_node)

            if isinstance(parameters_info, list):
                errors += parameters_info

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[9])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            # Statements or None
            statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[10])))
            statements_info = None

            docstring_leaf = None
            docstring_info = None

            if isinstance(statements_node, AST.Leaf):
                statements_node = None
            else:
                result = StatementsFragment.Extract(statements_node)

                if isinstance(result, list):
                    errors += result
                else:
                    statements_info, docstring_info = result

                    if docstring_info is not None:
                        docstring_leaf, docstring_info = docstring_info

            if errors:
                return errors

            return FuncDefinitionStatementModule.FuncDefinitionStatement.Create(
                CreateRegions(
                    node,
                    visibility_node,
                    mutability_modifier_node,
                    method_type_modifier_node,
                    return_type_node,
                    name_leaf,
                    docstring_leaf,
                    template_parameters_node,
                    captured_variables_node,
                    parameters_node,
                    statements_node,
                    is_deferred_node,
                    is_exceptional_node,
                    is_generator_node,
                    is_reentrant_node,
                    is_scoped_node,
                    is_static_node,
                ),
                ClassStatement.GetParentClassCapabilities(node, cls),
                visibility_info,
                mutability_modifier_info,
                method_type_modifier_info,
                return_type_info,
                name_info,
                docstring_info,
                template_parameters_info,
                captured_variables_info,
                parameters_info,
                statements_info,
                is_deferred_info,
                is_exceptional_info,
                is_generator_info,
                is_reentrant_info,
                is_scoped_info,
                is_static_info,
            )

        # ----------------------------------------------------------------------

        return Callback  # type: ignore


# ----------------------------------------------------------------------
CreateMethodModifierPhraseItem              = ModifierImpl.StandardCreatePhraseItemFuncFactory(MethodModifier)
ExtractMethodModifier                       = ModifierImpl.StandardExtractFuncFactory(MethodModifier)
