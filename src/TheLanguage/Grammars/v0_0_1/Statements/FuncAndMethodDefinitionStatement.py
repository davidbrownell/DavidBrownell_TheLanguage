# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-31 21:48:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncAndMethodDefinitionStatement object"""

import os

from typing import cast, Optional

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
    from ..Common import ParametersPhraseItem
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier
    from ..Common.Impl import ModifierImpl

    from ...GrammarError import GrammarError
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import SetLexerInfo
    from ....Lexer.Statements.FuncAndMethodDefinitionStatementLexerInfo import (
        FuncAndMethodDefinitionStatementLexerInfo,
        FuncAndMethodDefinitionStatementLexerRegions,
        MethodType,
        OperatorType,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(GrammarError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid operator name.")  # type: ignore


# ----------------------------------------------------------------------
class FuncAndMethodDefinitionStatement(GrammarPhrase):
    """\
    Defines a function (or method when used within a class statement).
    """

    PHRASE_NAME                             = "Func And Method Definition Statement"

    # TODO: Captures

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    OperatorNameMap                         = {
        # Foundational
        OperatorType.ToBool: "__ToBool__",
        OperatorType.ToString: "__ToString__",
        OperatorType.Repr: "__Repr__",
        OperatorType.Clone: "__Clone__",
        OperatorType.Serialize: "__Serialize__",

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
        OperatorType.LessEqual: "__LessEqual__",
        OperatorType.Greater: "__Greater__",
        OperatorType.GreaterEqual: "__GreaterEqual__",

        # Logical
        OperatorType.And: "__And__",
        OperatorType.Or: "__Or__",
        OperatorType.Not: "__Not__",

        # Mathematical
        OperatorType.Add: "__Add__",
        OperatorType.Subtract: "__Subtract__",
        OperatorType.Multiply: "__Multiply__",
        OperatorType.Divide: "__Divide__",
        OperatorType.DivideFloor: "__DivideFloor__",
        OperatorType.Power: "__Power__",
        OperatorType.Mod: "__Mod__",
        OperatorType.Positive: "__Positive__",
        OperatorType.Negative: "__Negative__",

        OperatorType.AddInplace: "__AddInplace__",
        OperatorType.SubtractInplace: "__SubtractInplace__",
        OperatorType.MultiplyInplace: "__MultiplyInplace__",
        OperatorType.DivideInplace: "__DivideInplace__",
        OperatorType.DivideFloorInplace: "__DivideFloorInplace__",
        OperatorType.PowerInplace: "__PowerInplace__",
        OperatorType.ModInplace: "__ModInplace__",

        # Bit Manipulation
        OperatorType.ShiftLeft: "__ShiftLeft__",
        OperatorType.ShiftRight: "__ShiftRight__",
        OperatorType.BitAnd: "__BitAnd__",
        OperatorType.BitOr: "__BitOr__",
        OperatorType.BitXor: "__BitXor__",
        OperatorType.BitFlip: "__BitFlip__",

        OperatorType.ShiftLeftInplace: "__ShiftLeftInplace__",
        OperatorType.ShiftRightInplace: "__ShiftRightInplace__",
        OperatorType.BitAndInplace: "__BitAndInplace__",
        OperatorType.BitOrInplace: "__BitOrInplace__",
        OperatorType.BitXorInplace: "__BitXorInplace__",
    }

    NameOperatorMap                         = {
        v: k for k, v in OperatorNameMap.items()
    }

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        # Ensure that the OperatorNameMap is fully populated
        for v in OperatorType:
            assert v in self.OperatorNameMap, v

        assert len(self.OperatorNameMap) == len(list(OperatorType))

        # Initialize the phrase
        super(FuncAndMethodDefinitionStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>*
                    AttributesPhraseItem.Create(),

                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <method_type_modifier>?
                    PhraseItem(
                        name="Method Type",
                        item=self._CreateMethodTypePhraseItem(),
                        arity="?",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.MethodName,

                    # <parameters>
                    ParametersPhraseItem.Create(),

                    # <class_modifier>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # - Multi-line Definition
                    # - Single-line Definition
                    # - Newline
                    (
                        # Multi-line, Single-line
                        StatementsPhraseItem.Create(),

                        # Newline (no content)
                        CommonTokens.Newline,
                    )
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
        assert len(nodes) == 8

        # <attributes>*
        attributes = AttributesPhraseItem.Extract(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

        if visibility_node is not None:
            visibility = VisibilityModifier.Extract(visibility_node)
        else:
            visibility = None

        # <method_type_modifier>?
        method_type_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))

        if method_type_modifier_node is not None:
            method_type_modifier = cls._ExtractMethodType(method_type_modifier_node)
        else:
            method_type_modifier = None

        # <type> (The TypeLexerInfo will be extracted as part of a deferred callback)
        return_type_node = ExtractDynamic(cast(Node, nodes[3]))

        # <name>
        method_name_leaf = cast(Leaf, nodes[4])
        method_name = cast(str, ExtractToken(method_name_leaf))

        if method_name.startswith("__") and method_name.endswith("__"):
            operator_name = cls.NameOperatorMap.get(method_name, None)
            if operator_name is None:
                raise InvalidOperatorNameError.FromNode(
                    method_name_leaf,
                    method_name,
                )

            method_name = operator_name

        # <parameters>
        parameters_node = cast(Node, nodes[5])

        parameters = ParametersPhraseItem.Extract(parameters_node)

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[6])))

        if class_modifier_node is not None:
            class_modifier = ClassModifier.Extract(class_modifier_node)
        else:
            class_modifier = None

        # <statements> or Newline
        statements_node = cast(Node, ExtractOr(cast(Node, nodes[7])))

        if isinstance(statements_node, Leaf):
            statements = None
        else:
            statements = StatementsPhraseItem.Extract(statements_node)

        # TODO: Leverage attributes

        # ----------------------------------------------------------------------
        def CommitLexerInfo():
            # Get the type TypeLexerInfo
            return_type = None
            return_type_node = None

            # TODO: Get the parameters ExprLexerInfo

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                FuncAndMethodDefinitionStatementLexerInfo(
                    CreateLexerRegions(
                        FuncAndMethodDefinitionStatementLexerRegions, # type: ignore
                        node,
                        visibility_node,
                        method_type_modifier_node,
                        return_type_node,
                        method_name_leaf,
                        parameters_node,
                        class_modifier_node,
                    ),
                    ClassStatement.GetContainingClassLexerInfo(  # type: ignore
                        node,
                        cls.PHRASE_NAME,
                    ),
                    visibility,  # type: ignore
                    method_type_modifier,  # type: ignore
                    return_type,  # type: ignore
                    method_name,  # type: ignore
                    parameters,  # type: ignore
                    class_modifier,  # type: ignore
                    statements is not None,  # type: ignore
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CommitLexerInfo)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _CreateMethodTypePhraseItem             = staticmethod(ModifierImpl.CreateStandardCreatePhraseItemFunc(MethodType))
    _ExtractMethodType                      = staticmethod(ModifierImpl.CreateStandardExtractFunc(MethodType))
