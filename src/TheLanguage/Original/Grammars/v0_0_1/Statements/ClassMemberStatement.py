# ----------------------------------------------------------------------
# |
# |  ClassMemberStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 09:50:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassMemberStatement object"""

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
    from .ClassStatement import ClassStatement
    from .FuncDefinitionStatement import FuncDefinitionStatement

    from ..Common import AttributesPhraseItem
    from ..Common import ClassModifier
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.ClassMemberStatementParserInfo import (
        ClassMemberStatementParserInfo,
        ExpressionParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class ClassMemberStatement(GrammarPhrase):
    """\
    Defines a class member.

    <attributes>? <visibility>? <type> <name> <class_modifier>? ('=' <expression>)?

    Examples:
        Int foo
        Int bar = 42

        @Member(init=True, serialize=False)
        Int var baz immutable

        @Member(compare=False)
        Int var biz immutable = 42
    """

    PHRASE_NAME                             = "Class Member Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassMemberStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>*
                    AttributesPhraseItem.Create(),

                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <generic_name>
                    CommonTokens.GenericLowerName,

                    # <class_modifier>?
                    OptionalPhraseItem.Create(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                    ),

                    # ('=' <expression>)?
                    OptionalPhraseItem.Create(
                        name="Initializer",
                        item=[
                            "=",
                            DynamicPhrasesType.Expressions,
                        ],
                    ),

                    CommonTokens.Newline,
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
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 7

            # <attributes>+
            attributes_node = cast(AST.Node, nodes[0])
            attributes_info = AttributesPhraseItem.ExtractLexerData(attributes_node)

            # TODO: use attributes_info

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            # <generic_name>
            name_leaf = cast(AST.Leaf, nodes[3])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.VariableNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "variable")

            # <class_modifier>?
            class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if class_modifier_node is None:
                class_modifier_info = None
            else:
                class_modifier_info = ClassModifier.Extract(class_modifier_node)

            # ('=' <expression>)?
            initializer_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[5])))
            if initializer_node is None:
                initializer_info = None
            else:
                initializer_nodes = ExtractSequence(initializer_node)
                assert len(initializer_nodes) == 2

                initializer_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, initializer_nodes[1])))
                initializer_info = cast(ExpressionParserInfo, GetParserInfo(initializer_node))

            return ClassMemberStatementParserInfo(
                CreateParserRegions(node, visibility_node, class_modifier_node, type_node, name_leaf, initializer_node),  # type: ignore
                ClassStatement.GetContainingClassParserInfo(node, FuncDefinitionStatement.PHRASE_NAME),  # type: ignore
                visibility_info,  # type: ignore
                class_modifier_info,  # type: ignore
                type_info,
                name_info,
                initializer_info,
            )

        # ----------------------------------------------------------------------

        return Impl
