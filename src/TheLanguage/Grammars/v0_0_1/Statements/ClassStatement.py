# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 00:32:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatement object"""

import itertools
import os

from enum import auto, Enum
from typing import cast, Dict, List, Optional, Tuple, Type

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import AttributesPhraseItem
    from ..Common import ClassModifier
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier
    from ..Common.Impl import ModifierImpl

    from ...GrammarError import GrammarError
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.ClassStatementLexerInfo import (
        ClassDependencyLexerInfo,
        ClassStatementLexerInfo,
        ClassType,
        StatementLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateInterfacesTypeError(GrammarError):
    Type: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The base type indicator '{Type}' may only appear once.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleBasesError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Classes can have only one base class; consider using mixins and interfaces instead.",
    )


# ----------------------------------------------------------------------
class ClassStatement(GrammarPhrase):
    """\
    Statement that creates a class.

    <attributes>? <visibility>? <class_type>? 'class'|'interface'|'mixin'|'enum'|'exception' <name>
        '(' (<base_visibility>? <name>)? ')'
            ('implements'|'uses' <name> (',' <name>)* ','?)){2}
    ':'
        <statement>+

    Examples:
        class Foo():
            pass

        class Bar(public Foo):
            pass

        public interface IBiz():
            pass

        public class Baz() implements IBiz:
            pass
    """

    PHRASE_NAME                             = "Class Statement"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class BaseTypeIndicator(ModifierImpl.StandardMixin, Enum):
        implements                          = auto()
        uses                                = auto()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        # <visibility>? <name>
        base_item = PhraseItem(
            name="Base Item",
            item=[
                # <visibility>?
                PhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                    arity="?",
                ),

                # <name>
                CommonTokens.TypeName,
            ],
        )

        # <base_item> (',' <base_item>)* ','?
        base_items = PhraseItem(
            name="Base Items",
            item=[
                # <base_item>
                base_item,

                # (',' <base_item>)*
                PhraseItem(
                    name="Comma and Content",
                    item=[
                        ",",
                        base_item,
                    ],
                    arity="*",
                ),

                # ','?
                PhraseItem(
                    name="Trailing Comma",
                    item=",",
                    arity="?",
                ),
            ],
        )

        super(ClassStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>?
                    AttributesPhraseItem.Create(),

                    # <visibility>? (class)
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <class_modifier>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # 'class'|'interface'|'mixin'|'enum'|'exception'
                    PhraseItem(
                        name="Class Type",
                        item=self._CreateClassTypePhraseItem(),
                    ),

                    # <name> (class)
                    CommonTokens.TypeName,

                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    PhraseItem(
                        name="Base Items",
                        item=base_items,
                        arity="?",
                    ),

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",

                    # Implements / Uses
                    CommonTokens.PushIgnoreWhitespaceControl,
                    PhraseItem(
                        name="Implements and Uses",
                        item=[
                            # 'implements'|'uses'
                            self.BaseTypeIndicator.CreatePhraseItem(),

                            # Items
                            PhraseItem(
                                item=(
                                    # '(' <base_items> ')'
                                    PhraseItem(
                                        name="Grouped",
                                        item=[
                                            "(",
                                            CommonTokens.PushIgnoreWhitespaceControl,

                                            base_items,

                                            CommonTokens.PopIgnoreWhitespaceControl,
                                            ")",
                                        ],
                                    ),

                                    # <base_items>
                                    base_items,
                                ),

                                # Use the order to disambiguate between group clauses and tuples.
                                ordered_by_priority=True,
                            ),
                        ],
                        arity="*",
                    ),
                    CommonTokens.PopIgnoreWhitespaceControl,

                    StatementsPhraseItem.Create(),
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
        assert len(nodes) == 14

        # <attributes>*
        attributes_data = AttributesPhraseItem.ExtractData(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

        if visibility_node is not None:
            visibility_info = VisibilityModifier.Extract(visibility_node)
        else:
            visibility_info = None

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))

        if class_modifier_node is not None:
            class_modifier_info = ClassModifier.Extract(class_modifier_node)
        else:
            class_modifier_info = None

        # <class_type>
        class_type_node = cast(Node, nodes[3])
        class_type_info = cls._ExtractClassType(class_type_node)

        # <name>
        class_name_leaf = cast(Leaf, nodes[4])
        class_name_info = cast(str, ExtractToken(class_name_leaf))

        # Base Info
        base_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[7])))

        if base_node is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(base_node)
            assert base_infos

            if len(base_infos) > 1:
                raise MultipleBasesError.FromNode(base_node)

            base_info = base_infos[0]

        # Interfaces and Mixins
        interfaces_and_mixins: Dict[
            Type[ClassStatement.BaseTypeIndicator],
            Tuple[
                Node,
                List[ClassDependencyLexerInfo],
            ]
        ] = {}

        for this_base_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[11]))):
            base_nodes = ExtractSequence(this_base_node)
            assert len(base_nodes) == 2

            # 'implements'|'uses'
            base_type_node = cast(Node, base_nodes[0])
            base_type = cls.BaseTypeIndicator.Extract(base_type_node)

            if base_type in interfaces_and_mixins:
                raise DuplicateInterfacesTypeError.FromNode(base_type_node, base_type.name)

            # Items
            base_node_items = cast(Node, ExtractOr(cast(Node, base_nodes[1])))
            assert base_node_items.Type is not None

            if base_node_items.Type.Name == "Grouped":
                base_node_items = ExtractSequence(base_node_items)[2]

            interfaces_and_mixins[base_type] = (
                this_base_node,
                cls._ExtractBaseInfo(cast(Node, base_node_items)),
            )

        # Statements
        statements_node = cast(Node, nodes[13])

        # TODO: Leverage attributes

        # pylint: disable=too-many-function-args
        SetLexerInfo(
            node,
            ClassStatementLexerInfo(
                CreateLexerRegions(
                    node,
                    visibility_node,
                    class_modifier_node,
                    class_type_node,
                    class_name_leaf,
                    base_node,
                    interfaces_and_mixins.get(cls.BaseTypeIndicator.implements, (None,))[0],  # type: ignore
                    interfaces_and_mixins.get(cls.BaseTypeIndicator.uses, (None,))[0],  # type: ignore
                    statements_node,
                ),
                visibility_info,  # type: ignore
                class_modifier_info,  # type: ignore
                class_type_info,
                class_name_info,  # type: ignore
                base_info,  # type: ignore
                interfaces_and_mixins.get(cls.BaseTypeIndicator.implements, (None, None))[1], # type: ignore
                interfaces_and_mixins.get(cls.BaseTypeIndicator.uses, (None, None))[1],  # type: ignore
            ),
        )

        # ----------------------------------------------------------------------
        def FinalConstruct():
            lexer_info = cast(ClassStatementLexerInfo, GetLexerInfo(node))

            # <statement>+
            statements_info = StatementsPhraseItem.ExtractLexerInfo(statements_node)

            lexer_info.FinalConstruct(statements_info)

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(FinalConstruct)

    # ----------------------------------------------------------------------
    @classmethod
    def GetContainingClassLexerInfo(
        cls,
        child_node: Node,
        # Taking this as a parameter to avoid circular dependencies, as
        # FuncAndMethodDefinitionStatement.py imports this file.
        func_and_method_statement_name: str,
    ) -> Optional[ClassStatementLexerInfo]:
        """Returns the ClassStatementLexerInfo for the class that contains the given node"""

        node = child_node.Parent

        while node is not None:
            if node.Type:
                if node.Type.Name == cls.PHRASE_NAME:
                    return getattr(node, "Info")

                if node.Type.Name == func_and_method_statement_name:
                    return None

            node = node.Parent

        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _CreateClassTypePhraseItem              = staticmethod(ModifierImpl.CreateByValueCreatePhraseItemFunc(ClassType))
    _ExtractClassType                       = staticmethod(ModifierImpl.CreateByValueExtractFunc(ClassType))

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractBaseInfo(
        cls,
        node: Node,
    ) -> List[ClassDependencyLexerInfo]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        results: List[ClassDependencyLexerInfo] = []

        for base_item in itertools.chain(
            [nodes[0]],
            [ExtractSequence(node)[1] for node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[1])))],
        ):
            assert base_item is not None

            base_items = ExtractSequence(cast(Node, base_item))
            assert len(base_items) == 2

            # <visibility>?
            visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], base_items[0])))

            if visibility_node is not None:
                visibility_info = VisibilityModifier.Extract(visibility_node)
            else:
                visibility_info = None

            # <name>
            name_leaf = cast(Leaf, base_items[1])
            name_info = cast(str, ExtractToken(name_leaf))

            # Commit the results
            results.append(
                # <Too many positional arguments> pylint: disable=too-many-function-args
                ClassDependencyLexerInfo(
                    CreateLexerRegions(
                        node,
                        visibility_node,
                        name_leaf,
                    ),  # type: ignore
                    visibility_info,  # type: ignore
                    name_info,  # type: ignore
                ),
            )

        return results
