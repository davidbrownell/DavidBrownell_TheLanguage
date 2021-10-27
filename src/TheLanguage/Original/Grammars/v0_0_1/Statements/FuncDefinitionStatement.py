# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 16:54:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefintionStatement object"""

import os

from typing import Callable, cast, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ClassStatement import ClassStatement

    from ..Common import AttributesPhraseItem
    from ..Common import ClassModifier
    from ..Common import MethodModifier
    from ..Common import ParametersPhraseItem

    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ..Expressions.NoneLiteralExpression import NoneLiteralExpression

    from ...Error import Error
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        ExtractTokenSpan,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.FuncDefinitionStatementParserInfo import (
        FuncDefinitionStatementParserInfo,
        OperatorType,
        TypeParserInfo,
    )

    # Convenience imports
    # <<unused-import> pylint: disable=W0611
    from ..Common.ParametersPhraseItem import (
        NewStyleParameterGroupDuplicateError,
        TraditionalDelimiterOrderError,
        TraditionalDelimiterDuplicatePositionalError,
        TraditionalDelimiterDuplicateKeywordError,
        TraditionalDelimiterPositionalError,
        TraditionalDelimiterKeywordError,
        RequiredParameterAfterDefaultError,
    )

    # <<unused-import> pylint: disable=W0611
    from ..Common.StatementsPhraseItem import (
        InvalidDocstringError,
        MultipleDocstringsError,
        MisplacedDocstringError,
        StatementsRequiredError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(Error):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Name}' is not a valid operator name.",
    )


# ----------------------------------------------------------------------
class FuncDefinitionStatement(GrammarPhrase):
    """\
    Defines a function (or method when used within a class statement)
    """

    PHRASE_NAME                             = "Func Definition Statement"

    # TODO: Add Captures
    # TODO: Add Templates

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    # TODO: Decorate these values with 'Async', '...', and '?'
    OperatorNameMap                         = {
        # Foundational
        OperatorType.ToBool: "__ToBool__",
        OperatorType.ToString: "__ToString__",
        OperatorType.Repr: "__Repr__",
        OperatorType.Clone: "__Clone__",
        OperatorType.Serialize: "__Serialize__",
        OperatorType.Deserialize: "__Deserialize__",

        # Instance Instantiation
        OperatorType.Init: "__Init__",
        OperatorType.PostInit: "__PostInit__",

        # Dynamic
        OperatorType.GetAttribute: "__GetAttribute__",
        OperatorType.Call: "__Call__",
        OperatorType.Cast: "__Cast__",
        OperatorType.Index: "__Index__",

        # Container
        OperatorType.Contains: "__Contains__",
        OperatorType.Length: "__Length__",
        OperatorType.Iter: "__Iter__",
        OperatorType.AtEnd: "__AtEnd__",

        # Comparison
        OperatorType.Compare: "__Compare__",
        OperatorType.Equal: "__Equal__",
        OperatorType.NotEqual: "__NotEqual__",
        OperatorType.Less: "__Less__",
        OperatorType.LessOrEqual: "__LessOrEqual__",
        OperatorType.Greater: "__Greater__",
        OperatorType.GreaterOrEqual: "__GreaterOrEqual__",

        # Logical
        OperatorType.And: "__And__",
        OperatorType.Or: "__Or__",
        OperatorType.Not: "__Not__",

        # Mathematical
        OperatorType.Add: "__Add__",
        OperatorType.Subtract: "__Subtract__",
        OperatorType.Multiply: "__Multiply__",
        OperatorType.Power: "__Power__",
        OperatorType.Divide: "__Divide__",
        OperatorType.DivideFloor: "__DivideFloor__",
        OperatorType.Modulo: "__Modulo__",
        OperatorType.Positive: "__Positive__",
        OperatorType.Negative: "__Negative__",

        OperatorType.AddInplace: "__AddInplace__",
        OperatorType.SubtractInplace: "__SubtractInplace__",
        OperatorType.MultiplyInplace: "__MultiplyInplace__",
        OperatorType.PowerInplace: "__PowerInplace__",
        OperatorType.DivideInplace: "__DivideInplace__",
        OperatorType.DivideFloorInplace: "__DivideFloorInplace__",
        OperatorType.ModuloInplace: "__ModuloInplace__",

        # Bit Manipulation
        OperatorType.BitShiftLeft: "__BitShiftLeft__",
        OperatorType.BitShiftRight: "__BitShiftRight__",
        OperatorType.BitAnd: "__BitAnd__",
        OperatorType.BitOr: "__BitOr__",
        OperatorType.BitXor: "__BitXor__",
        OperatorType.BitFlip: "__BitFlip__",

        OperatorType.BitShiftLeftInplace: "__BitShiftLeftInplace__",
        OperatorType.BitShiftRightInplace: "__BitShiftRightInplace__",
        OperatorType.BitAndInplace: "__BitAndInplace__",
        OperatorType.BitOrInplace: "__BitOrInplace__",
        OperatorType.BitXorInplace: "__BitXorInplace__",
    }

    NameOperatorMap                         = {
        v: k for k, v in OperatorNameMap.items()
    }

    assert len(OperatorNameMap) == len(OperatorType)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncDefinitionStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # TODO: 'deferred' and 'synchronized' are attributes
                    # <attributes>*
                    AttributesPhraseItem.Create(),

                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <method_type_modifier>?
                    OptionalPhraseItem.Create(
                        name="Method Type",
                        item=MethodModifier.CreatePhraseItem(),
                    ),

                    # <type>
                    PhraseItem.Create(
                        name="Return Type",
                        item=(
                            DynamicPhrasesType.Types,
                            NoneLiteralExpression.CreatePhraseItem(),
                        ),
                    ),

                    # <name>
                    CommonTokens.FuncName,

                    # <parameters>
                    ParametersPhraseItem.Create(),

                    # <class_modifier>?
                    OptionalPhraseItem.Create(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                    ),

                    # Statements or None
                    (
                        StatementsPhraseItem.Create(),

                        # Newline (no content)
                        CommonTokens.Newline,
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 8

            # <attributes>*
            attributes_node = cast(Optional[AST.Node], nodes[0])
            attribute_data = AttributesPhraseItem.ExtractLexerData(attributes_node)

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
                method_type_modifier_info = MethodModifier.Extract(method_type_modifier_node)

            # <type>
            return_type_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[3])))

            assert return_type_node.Type is not None

            if isinstance(return_type_node.Type, DynamicPhrase):
                return_type_node = ExtractDynamic(return_type_node)
                return_type_info = cast(TypeParserInfo, GetParserInfo(return_type_node))
            elif return_type_node.Type.Name == NoneLiteralExpression.PHRASE_ITEM_NAME:
                return_type_info = False
            else:
                assert False, return_type_node.Type  # pragma: no cover

            # <name>
            func_name_leaf = cast(AST.Leaf, nodes[4])
            func_name_info = cast(str, ExtractToken(func_name_leaf, group_dict_name="value"))

            # Get the alphanumeric portion of the function name to determine if it is async
            alpha_region = ExtractTokenSpan(func_name_leaf, "alphanum")
            assert alpha_region is not None

            alpha_text = alpha_region[0].Content[alpha_region[0].Offset : alpha_region[1].Offset]
            if alpha_text.endswith("Async"):
                alpha_region[0].Advance(len(alpha_text) - len("Async"))

                is_async_info = True
                is_async_region = alpha_region
            else:
                is_async_info = None
                is_async_region = None

            is_generator_region = ExtractTokenSpan(func_name_leaf, "generator_suffix")
            is_generator_info = None if is_generator_region is None else True

            is_exceptional_region = ExtractTokenSpan(func_name_leaf, "exceptional_suffix")
            is_exceptional_info = None if is_exceptional_region is None else True

            if func_name_info.startswith("__") or func_name_info.endswith("__"):
                operator_name = cls.NameOperatorMap.get(func_name_info, None)
                if operator_name is None:
                    raise InvalidOperatorNameError.FromNode(func_name_leaf, func_name_info)

                func_name_info = operator_name

            # <parameters>
            parameters_node = cast(AST.Node, nodes[5])
            parameters_info = ParametersPhraseItem.ExtractParserInfo(parameters_node)

            # <class_modifier>?
            class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[6])))

            if class_modifier_node is None:
                class_modifier_info = None
            else:
                class_modifier_info = ClassModifier.Extract(class_modifier_node)

            # Statements Or None
            statements_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[7])))

            if isinstance(statements_node, AST.Leaf):
                statements_node = None
                statements_info = None

                docstring_leaf = None
                docstring_info = None
            else:
                statements_info, docstring_info = StatementsPhraseItem.ExtractParserInfoWithDocstrings(statements_node)

                if docstring_info is None:
                    docstring_leaf = None
                else:
                    docstring_info, docstring_leaf = docstring_info

                    if not statements_info:
                        statements_info = None
                        statements_node = None

            # TODO: Extract information from the func attributes
            is_deferred_region = None
            is_deferred_info = None

            is_synchronized_region = None
            is_synchronized_info = None

            return FuncDefinitionStatementParserInfo(
                CreateParserRegions(
                    node,
                    visibility_node,
                    method_type_modifier_node,
                    class_modifier_node,
                    return_type_node,
                    func_name_leaf,
                    parameters_node,
                    statements_node,
                    docstring_leaf,
                    is_async_region,
                    is_deferred_region,
                    is_exceptional_region,
                    is_generator_region,
                    is_synchronized_region,
                ), # type: ignore
                ClassStatement.GetContainingClassParserInfo(node, cls.PHRASE_NAME),  # type: ignore
                visibility_info,  # type: ignore
                method_type_modifier_info,  # type: ignore
                class_modifier_info,  # type: ignore
                return_type_info,
                func_name_info,
                parameters_info,
                statements_info,
                docstring_info,
                is_async_info,
                is_deferred_info,
                is_exceptional_info,
                is_generator_info,
                is_synchronized_info,
            )

        # ----------------------------------------------------------------------

        return Impl
