import os

from typing import Callable, cast, List, Optional, Tuple, Union

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

    from ..Common import AttributePhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
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
                    ZeroOrMorePhraseItem.Create(
                        name="Attributes",
                        item=AttributePhraseItem.Create(),
                    ),

                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <generic_name>
                    CommonTokens.GenericLowerName,

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
            assert len(nodes) == 6

            # <attribute>*
            attributes_node = cast(Optional[AST.Node], nodes[0])

            attribute_data: List[List[AttributePhraseItem.AttributeData]] = []

            for attribute_node in cast(List[AST.Node], ExtractRepeat(attributes_node)):
                attribute_data.append(AttributePhraseItem.ExtractLexerData(cast(AST.Node, attribute_node)))

            # Leverage attribute data
            no_init_node = None
            no_init_info = None

            no_serialize_node = None
            no_serialize_info = None

            no_compare_node = None
            no_compare_info = None

            is_override_node = None
            is_override_info = None

            for attributes in attribute_data:
                for attribute in attributes:
                    if attribute.Name == "NoInit":
                        no_init_node = attribute.NameLeaf
                        no_init_info = True

                    elif attribute.Name == "NoSerialize":
                        no_serialize_node = attribute.NameLeaf
                        no_serialize_info = True

                    elif attribute.Name == "NoCompare":
                        no_compare_node = attribute.NameLeaf
                        no_compare_info = True

                    elif attribute.Name == "Override":
                        is_override_node = attribute.NameLeaf
                        is_override_info = True

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

            # ('=' <expression>)?
            initializer_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if initializer_node is None:
                initializer_info = None
            else:
                initializer_nodes = ExtractSequence(initializer_node)
                assert len(initializer_nodes) == 2

                initializer_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, initializer_nodes[1])))
                initializer_info = cast(ExpressionParserInfo, GetParserInfo(initializer_node))

            return ClassMemberStatementParserInfo(
                CreateParserRegions(
                    node,
                    visibility_node,
                    type_node,
                    name_leaf,
                    initializer_node,
                    no_init_node,
                    no_serialize_node,
                    no_compare_node,
                    is_override_node,
                ),  # type: ignore
                ClassStatement.GetContainingClassParserInfo(node, FuncDefinitionStatement.PHRASE_NAME),  # type: ignore
                visibility_info,  # type: ignore
                type_info,
                name_info,
                initializer_info,
                no_init_info,
                no_serialize_info,
                no_compare_info,
                is_override_info,
            )

        # ----------------------------------------------------------------------

        return Impl
