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
    from ..Common import CapturedVariablesFragment
    from ..Common import FuncParametersFragment
    from ..Common import MutabilityModifier
    from ..Common import StatementsFragment
    from ..Common import TemplateParametersFragment
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Common.Impl import ModifierImpl

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
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

    from ...Parser.ParserInfos.Common.MethodModifier import MethodModifier
    from ...Parser.ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...Parser.ParserInfos.Statements.FuncDefinitionStatementParserInfo import (
        ExpressionParserInfo,
        FuncDefinitionStatementParserInfo,
        OperatorType,
    )


# ----------------------------------------------------------------------
InvalidReservedMethodName                   = CreateError(
    "'{name}' is not a valid reserved method name",
    name=str,
)


# ----------------------------------------------------------------------
class FuncDefinitionStatement(GrammarPhrase):
    PHRASE_NAME                             = "Func Definition Statement"

    assert ClassStatement.FUNCTION_STATEMENT_PHRASE_NAME == PHRASE_NAME

    OPERATOR_MAP                            = {
        "__Accept?__" : OperatorType.Accept,
        "__Compare__": OperatorType.Compare,
        "__Deserialize?__": OperatorType.Deserialize,
        "__Serialize?__": OperatorType.Serialize,
        "__Clone?__": OperatorType.Clone,
        "__ToBool__": OperatorType.ToBool,
        "__ToString?__": OperatorType.ToString,
        "__Call?__": OperatorType.Call,
        "__GetAttribute?__": OperatorType.GetAttribute,
        "__Index__": OperatorType.Index,
        "__Iter__": OperatorType.Iter,
        "__Cast?__": OperatorType.Cast,
        "__Negative?__": OperatorType.Negative,
        "__Positive?__": OperatorType.Positive,
        "__BitFlip?__": OperatorType.BitFlip,
        "__Divide?__": OperatorType.Divide,
        "__DivideFloor?__": OperatorType.DivideFloor,
        "__Modulo?__": OperatorType.Modulo,
        "__Multiply?__": OperatorType.Multiply,
        "__Power?__": OperatorType.Power,
        "__Add?__": OperatorType.Add,
        "__Subtract?__": OperatorType.Subtract,
        "__BitShiftLeft?__": OperatorType.BitShiftLeft,
        "__BitShiftRight?__": OperatorType.BitShiftRight,
        "__Greater__": OperatorType.Greater,
        "__GreaterEqual__": OperatorType.GreaterEqual,
        "__Less__": OperatorType.Less,
        "__LessEqual__": OperatorType.LessEqual,
        "__Equal__": OperatorType.Equal,
        "__NotEqual__": OperatorType.NotEqual,
        "__BitAnd?__": OperatorType.BitAnd,
        "__BitXOr?__": OperatorType.BitXor,
        "__BitOr?__": OperatorType.BitOr,
        "__Contains__": OperatorType.Contains,
        "__NotContains__": OperatorType.NotContains,
        "__Not__": OperatorType.Not,
        "__LogicalAnd__": OperatorType.LogicalAnd,
        "__LogicalOr__": OperatorType.LogicalOr,
        "__BitFlipInplace?__": OperatorType.BitFlipInplace,
        "__DivideInplace?__": OperatorType.DivideInplace,
        "__DivideFloorInplace?__": OperatorType.DivideFloorInplace,
        "__ModuloInplace?__": OperatorType.ModuloInplace,
        "__MultiplyInplace?__": OperatorType.MultiplyInplace,
        "__PowerInplace?__": OperatorType.PowerInplace,
        "__AddInplace?__": OperatorType.AddInplace,
        "__SubtractInplace?__": OperatorType.SubtractInplace,
        "__BitShiftLeftInplace?__": OperatorType.BitShiftLeftInplace,
        "__BitShiftRightInplace?__": OperatorType.BitShiftRightInplace,
        "__BitAndInplace?__": OperatorType.BitAndInplace,
        "__BitXOrInplace?__": OperatorType.BitXorInplace,
        "__BitOrInplace?__": OperatorType.BitOrInplace,
    }

    assert len(OPERATOR_MAP) == len(OperatorType), (len(OPERATOR_MAP), len(OperatorType))

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncDefinitionStatement, self).__init__(
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

                # <method_type_modifier>?
                OptionalPhraseItem(
                    name="Method Modifier",
                    item=CreateMethodModifierPhraseItem(),
                ),

                # <return_type>
                DynamicPhrasesType.Expressions,

                # <name>
                CommonTokens.FuncOrTypeName,

                # Template Parameters, Captures
                CommonTokens.PushIgnoreWhitespaceControl,

                # <template_parameters>?
                OptionalPhraseItem(
                    TemplateParametersFragment.Create(),
                ),

                # <captured_variables>?
                OptionalPhraseItem(
                    CapturedVariablesFragment.Create(),
                ),

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
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(  # pylint: disable=too-many-statements
        cls,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():  # pylint: disable=too-many-locals
            nodes = ExtractSequence(node)
            assert len(nodes) == 12

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
                for attribute in AttributesFragment.Extract(attributes_node):
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
            return_type_info = cast(ExpressionParserInfo, GetParserInfo(return_type_node))

            # Clear all info if we are looking at a None return type
            if isinstance(return_type_info, NoneExpressionParserInfo):
                return_type_info = None
                return_type_node = None

            # <name>
            name_leaf = cast(AST.Leaf, nodes[4])
            name_info = CommonTokens.FuncOrTypeName.Extract(name_leaf)  # type: ignore

            if name_info.startswith("__") and name_info.endswith("__"):
                operator_type = cls.OPERATOR_MAP.get(name_info, None)
                if operator_type is None:
                    errors.append(
                        InvalidReservedMethodName.Create(
                            region=CreateRegion(name_leaf),
                            name=name_info,
                        ),
                    )
                else:
                    name_info = operator_type

            # TODO: Get compile status from name
            # TODO: Get exceptional information from name
            # TODO: Get visibility information from name

            # <template_parameters>?
            template_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[6])))
            if template_parameters_node is None:
                template_parameters_info = None
            else:
                template_parameters_info = TemplateParametersFragment.Extract(template_parameters_node)

            # <captured_variables>?
            captured_variables_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
            if captured_variables_node is None:
                captured_variables_info = None
            else:
                captured_variables_info = CapturedVariablesFragment.Extract(captured_variables_node)

            # <parameters>
            parameters_node = cast(AST.Node, nodes[9])
            parameters_info = FuncParametersFragment.Extract(parameters_node)

            # <mutability_modifier>?
            mutability_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[10])))
            if mutability_modifier_node is None:
                mutability_modifier_info = None
            else:
                mutability_modifier_info = MutabilityModifier.Extract(mutability_modifier_node)

            # Statements or None
            statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[11])))

            if isinstance(statements_node, AST.Leaf):
                statements_node = None
                statements_info = None

                docstring_leaf = None
                docstring_info = None
            else:
                statements_info, docstring_info = StatementsFragment.Extract(statements_node)

                if docstring_info is None:
                    docstring_leaf = None
                else:
                    docstring_leaf, docstring_info = docstring_info

            if errors:
                raise ErrorException(*errors)

            assert not isinstance(parameters_info, list)

            return FuncDefinitionStatementParserInfo.Create(
                CreateRegions(
                    node,
                    parameters_node,
                    visibility_node,
                    mutability_modifier_node,
                    method_type_modifier_node,
                    name_leaf,
                    docstring_leaf,
                    captured_variables_node,
                    statements_node,
                    is_deferred_node,
                    is_exceptional_node,
                    is_generator_node,
                    is_reentrant_node,
                    is_scoped_node,
                    is_static_node,
                ),
                ClassStatement.GetParentClassCapabilities(node),
                parameters_info,
                visibility_info,
                mutability_modifier_info,
                method_type_modifier_info,
                return_type_info,
                name_info,
                docstring_info,
                template_parameters_info,
                captured_variables_info,
                statements_info,
                is_deferred_info,
                is_exceptional_info,
                is_generator_info,
                is_reentrant_info,
                is_scoped_info,
                is_static_info,
            )

        # ----------------------------------------------------------------------

        return Callback


# ----------------------------------------------------------------------
CreateMethodModifierPhraseItem              = ModifierImpl.StandardCreatePhraseItemFuncFactory(MethodModifier)
ExtractMethodModifier                       = ModifierImpl.StandardExtractFuncFactory(MethodModifier)
