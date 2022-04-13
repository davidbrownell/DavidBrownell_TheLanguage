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

from typing import cast, Optional

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

    from ..Common import FuncParametersFragment
    from ..Common import MutabilityModifier
    from ..Common import StatementsFragment
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Common.Impl import ModifierImpl

    from ...Common.Diagnostics import Diagnostics

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

    from ...Parser.Parser import CreateRegions, GetPhrase
    from ...Parser.Common.MethodModifier import MethodModifier
    from ...Parser.Statements import FuncDefinitionStatement as FuncDefinitionStatementModule


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
                    # TODO: <attributes>?

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

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.RuntimeFuncName,

                    # Template Parameters, Captures
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # TODO: <template_parameters>?
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
        diagnostics: Diagnostics,
    ) -> GrammarPhrase.ExtractParserPhraseReturnType:
        # ----------------------------------------------------------------------
        def Callback():  # pylint: disable=too-many-locals
            nodes = ExtractSequence(node)
            assert len(nodes) == 9 # TODO: 12

            # TODO: <attributes>
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

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <method_type_modifier>?
            method_type_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if method_type_modifier_node is None:
                method_type_modifier_info = None
            else:
                method_type_modifier_info = ExtractMethodModifier(method_type_modifier_node)

            # <return_type>
            return_type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            return_type_info = cast(FuncDefinitionStatementModule.TypePhrase, GetPhrase(return_type_node))

            # <name>
            name_leaf = cast(AST.Leaf, nodes[3])
            name_info = ExtractToken(name_leaf)

            # TODO: <template_parameters>?
            # TODO: <captured_variables>?

            # <parameters>
            parameters_node = cast(AST.Node, nodes[6])
            parameters_info = FuncParametersFragment.Extract(parameters_node, diagnostics)

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            # Statements or None
            statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[8])))

            if isinstance(statements_node, AST.Leaf):
                statements_node = None
                statements_info = None

                docstring_leaf = None
                docstring_info = None
            else:
                result = StatementsFragment.Extract(statements_node, diagnostics)
                if result is None:
                    assert diagnostics.errors

                    statements_info = None
                    docstring_info = None
                    docstring_leaf = None
                else:
                    statements_info, docstring_info = result

                    if docstring_info is None:
                        docstring_leaf = None
                    else:
                        docstring_leaf, docstring_info = docstring_info

            return FuncDefinitionStatementModule.FuncDefinitionStatement.Create(
                diagnostics,
                CreateRegions(
                    node,
                    visibility_node,
                    mutability_modifier_node,
                    method_type_modifier_node,
                    return_type_node,
                    name_leaf,
                    docstring_leaf,
                    None, # captured_variables
                    parameters_node,
                    statements_node,
                    is_deferred_node,
                    is_exceptional_node,
                    is_generator_node,
                    is_reentrant_node,
                    is_scoped_node,
                ),
                ClassStatement.GetParentClassCapabilities(node, cls),
                visibility_info,
                mutability_modifier_info,
                method_type_modifier_info,
                return_type_info,
                name_info,
                docstring_info,
                None, # captured_variables
                parameters_info,
                statements_info,
                is_deferred_info,
                is_exceptional_info,
                is_generator_info,
                is_reentrant_info,
                is_scoped_info,
            )

        # ----------------------------------------------------------------------

        return Callback  # type: ignore


# ----------------------------------------------------------------------
CreateMethodModifierPhraseItem              = ModifierImpl.StandardCreatePhraseItemFuncFactory(MethodModifier)
ExtractMethodModifier                       = ModifierImpl.StandardExtractFuncFactory(MethodModifier)
