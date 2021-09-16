# ----------------------------------------------------------------------
# |
# |  ClassMemberStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-02 12:03:44
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
    from .FuncAndMethodDefinitionStatement import FuncAndMethodDefinitionStatement

    from ..Common import AttributesPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import ClassModifier
    from ..Common import VisibilityModifier

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.ClassMemberStatementLexerInfo import (
        ClassMemberStatementLexerInfo,
        ExpressionLexerInfo,
        TypeLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class ClassMemberStatement(GrammarPhrase):
    """\
    Defines a class member.

    <attributes>? <visibility>? <type> <name> <class_modifier>? ('=' <expr>)?

    Examples:
        Int foo
        Int bar = 42

        @Member(init=True, serialize=False)
        Int var baz immutable

        @Member(compare=False)
        Int var biz immutable = 42
    """

    PHRASE_NAME                             = "Class Member Statement"

    # TODO (Lexer Impl): Potential Attributes: Init, ToStr, Serialize, Equality # <TODO> pylint: disable=W0511

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ClassMemberStatement, self).__init__(
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

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.GenericName,

                    # <class_modifier>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # ('=' <expr>)?
                    PhraseItem(
                        name="Default Value",
                        item=[
                            "=",
                            DynamicPhrasesType.Expressions,
                        ],
                        arity="?",
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 7

            # <attributes>*
            attributes_data = AttributesPhraseItem.ExtractData(cast(Optional[Node], nodes[0]))

            # <visibility>?
            visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

            if visibility_node is not None:
                visibility_info = VisibilityModifier.Extract(visibility_node)
            else:
                visibility_info = None

            # <type> (The TypeLexerInfo will be extracted as part of a deferred callback)
            type_node = ExtractDynamic(cast(Node, nodes[2]))
            type_info = cast(TypeLexerInfo, GetLexerInfo(type_node))

            # <name>
            name_leaf = cast(Leaf, nodes[3])
            name_info = cast(str, ExtractToken(name_leaf))

            # <class_modifier>?
            class_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[4])))

            if class_modifier_node is not None:
                class_modifier_info = ClassModifier.Extract(class_modifier_node)
            else:
                class_modifier_info = None

            # ('=' <expr>)? (The ExprLexerInfo will be extracted as part of a deferred callback)
            default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[5])))

            if default_node is not None:
                default_nodes = ExtractSequence(default_node)
                assert len(default_nodes) == 2

                default_node = ExtractDynamic(cast(Node, default_nodes[1]))

            # TODO: Leverage attributes (init, serialize, etc.)

            # Get the default ExprLexerInfo
            if default_node is not None:
                default_info = cast(ExpressionLexerInfo, GetLexerInfo(default_node))
            else:
                default_info = None

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                ClassMemberStatementLexerInfo(
                    CreateLexerRegions(
                        node,
                        visibility_node,
                        type_node,
                        name_leaf,
                        class_modifier_node,
                        default_node,
                    ),  # type: ignore
                    ClassStatement.GetContainingClassLexerInfo(  # type: ignore
                        node,
                        FuncAndMethodDefinitionStatement.PHRASE_NAME,
                    ),
                    visibility_info,  # type: ignore
                    type_info,  # type: ignore
                    name_info,  # type: ignore
                    class_modifier_info,  # type: ignore
                    default_info,  # type: ignore
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
