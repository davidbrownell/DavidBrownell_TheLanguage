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

from typing import cast, Dict, Optional, Union

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
    from ..Common import Tokens as CommonTokens
    from ..Common import ClassModifier
    from ..Common import VisibilityModifier

    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.ParserInterfaces.Statements.ClassMemberStatementLexerInfo import (
        ClassMemberStatementLexerInfo,
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
    # TODO (Lexer Impl): Check validity against class type info

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
    @classmethod
    @Interface.override
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        token_lookup: Dict[str, Union[Leaf, Node]] = {
            "self": node,
        }

        nodes = ExtractSequence(node)
        assert len(nodes) == 7

        # <attributes>?
        attributes = AttributesPhraseItem.Extract(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

        if visibility_node is not None:
            visibility = VisibilityModifier.Extract(visibility_node)
            token_lookup["Visibility"] = visibility_node
        else:
            visibility = None

        # <type> (The LexerInfo will be extracted as part of a deferred callback)
        type_node = ExtractDynamic(cast(Node, nodes[2]))

        # <name>
        name_leaf = cast(Leaf, nodes[3])
        name = cast(str, ExtractToken(name_leaf))
        token_lookup["Name"] = name_leaf

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[4])))

        if class_modifier_node is not None:
            class_modifier = ClassModifier.Extract(class_modifier_node)
            token_lookup["ClassModifier"] = class_modifier_node
        else:
            class_modifier = None

        # ('=' <expr>)? (The LexerInfo will be extracted as part of a deferred callback)
        default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[5])))

        if default_node is not None:
            default_nodes = ExtractSequence(default_node)
            assert len(default_nodes) == 2

            default_node = ExtractDynamic(cast(Node, default_nodes[1]))

        # TODO: Leverage attributes

        # ----------------------------------------------------------------------
        def CommitLexerInfo():
            # Get the type LexerInfo
            type_info = None # TODO

            # Get the default LexerInfo
            if default_node is not None:
                default_info = None # TODO
            else:
                default_info = None

            object.__setattr__(
                node,
                "Info",
                # pylint: disable=too-many-function-args
                ClassMemberStatementLexerInfo(
                    token_lookup,
                    ClassStatement.GetContainingClassLexerInfo(node),
                    visibility,  # type: ignore
                    type_info,
                    name,
                    class_modifier,  # type: ignore
                    default_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ValidateSyntaxResult(CommitLexerInfo)
