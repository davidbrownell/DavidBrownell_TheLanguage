# ----------------------------------------------------------------------
# |
# |  ClassUsingStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-19 09:06:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassUsingStatement object"""

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

    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier
    from ..Expressions.BinaryExpression import BinaryExpression, OperatorType as BinaryExpressionOperatorType

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ...Lexer.Phrases.DynamicPhrase import DynamicPhrase, Phrase

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        ErrorException,
        GetParserInfo,
    )

    from ...Parser.ParserInfos.Statements.ClassUsingStatementParserInfo import (
        ClassUsingStatementParserInfo,
        BinaryExpressionParserInfo,
    )


# ----------------------------------------------------------------------
InvalidClassUsingError                      = CreateError(
    "Using statements may only be used in class-like types",
)


# ----------------------------------------------------------------------
class ClassUsingStatement(GrammarPhrase):
    PHRASE_NAME                             = "Class Using Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        # ----------------------------------------------------------------------
        def IsValidData(
            data: Phrase.LexResultData,
        ) -> bool:
            data = DynamicPhrase.GetDynamicData(data)

            return (
                data.phrase.name == BinaryExpression.PHRASE_NAME
                and BinaryExpression.GetOperatorType(data) == BinaryExpressionOperatorType.Access
            )

        # ----------------------------------------------------------------------

        super(ClassUsingStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <visibility>?
                OptionalPhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                "using",

                # <type>
                PhraseItem(
                    item=DynamicPhrasesType.Expressions,
                    is_valid_data_func=IsValidData,
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
            assert len(nodes) == 4

            errors: List[Error] = []

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            type_info = cast(BinaryExpressionParserInfo, GetParserInfo(type_node))

            class_capabilities = ClassStatement.GetParentClassCapabilities(node)

            if class_capabilities is None:
                errors.append(
                    InvalidClassUsingError.Create(
                        region=CreateRegion(node),
                    ),
                )

            if errors:
                raise ErrorException(*errors)

            return ClassUsingStatementParserInfo.Create(
                CreateRegions(node, visibility_node),
                ClassStatement.GetParentClassCapabilities(node),
                visibility_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Callback
