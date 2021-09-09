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
from typing import Any, cast, Dict, List, Optional, Union

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

    from ...GrammarPhrase import GrammarPhrase, ValidationError

    from ....Lexer.ParserInterfaces.Statements.ClassStatementLexerInfo import (
        ClassDependencyLexerInfo,
        ClassStatementLexerInfo,
        ClassType,
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
class DuplicateInterfacesTypeError(ValidationError):
    Type: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The base type indicator '{Type}' may only appear once.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleBasesError(ValidationError):
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
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        token_lookup: Dict[str, Union[Leaf, Node]] = {
            "self": node,
        }

        nodes = ExtractSequence(node)
        assert len(nodes) == 14

        # <attributes>?
        attributes = AttributesPhraseItem.Extract(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))

        if visibility_node is not None:
            visibility = VisibilityModifier.Extract(visibility_node)
            token_lookup["Visibility"] = visibility_node
        else:
            visibility = None

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))

        if class_modifier_node is not None:
            class_modifier = ClassModifier.Extract(class_modifier_node)
            token_lookup["ClassModifier"] = class_modifier_node
        else:
            class_modifier = None

        # <class_type>
        class_type_node = cast(Node, nodes[3])
        class_type = cls._ExtractClassType(class_type_node)
        token_lookup["ClassType"] = class_type_node

        # <name>
        class_name_leaf = cast(Leaf, nodes[4])
        class_name = cast(str, ExtractToken(class_name_leaf))
        token_lookup["Name"] = class_name_leaf

        # Base Info
        base_info_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[7])))

        if base_info_node is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(base_info_node)
            assert base_infos

            if len(base_infos) > 1:
                raise MultipleBasesError.FromNode(base_info_node)

            base_info = base_infos[0]

        # Interfaces and Mixins
        interfaces_and_mixins = {}

        for base_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[11]))):
            base_nodes = ExtractSequence(base_node)
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

            interfaces_and_mixins[base_type] = cls._ExtractBaseInfo(cast(Node, base_node_items))

        # Statements
        statements = StatementsPhraseItem.Extract(cast(Node, nodes[13]))

        # TODO: Leverage attributes and statements

        # Commit the data
        object.__setattr__(
            node,
            "Info",
            # pylint: disable=too-many-function-args
            ClassStatementLexerInfo(
                token_lookup,
                visibility,  # type: ignore
                class_modifier,  # type: ignore
                class_type,
                class_name,
                base_info,
                interfaces_and_mixins.get(cls.BaseTypeIndicator.implements, []),
                interfaces_and_mixins.get(cls.BaseTypeIndicator.uses, []),
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def GetContainingClassLexerInfo(
        cls,
        child_node: Node,
        # Taking this as a parameter to avoid circular dependencies, as
        # FuncAndMethodDefinitionStatement.py imports this file.
        func_and_method_statement_name: str,
    ) -> Optional[ClassStatementLexerInfo]:
        """Returns the LexerInfo for the class that contains the given node"""

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

            token_lookup: Dict[str, Union[Leaf, Node]] = {
                "self": base_item,
            }

            base_items = ExtractSequence(cast(Node, base_item))
            assert len(base_items) == 2

            # <visibility>?
            visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], base_items[0])))

            if visibility_node is not None:
                visibility = VisibilityModifier.Extract(visibility_node)
                token_lookup["Visibility"] = visibility_node
            else:
                visibility = None

            # <name>
            name_leaf = cast(Leaf, base_items[1])
            name = cast(str, ExtractToken(name_leaf))
            token_lookup["Name"] = name_leaf

            # Commit the results
            results.append(
                # <Too many positional arguments> pylint: disable=too-many-function-args
                ClassDependencyLexerInfo(
                    token_lookup,
                    visibility,  # type: ignore
                    name,
                ),
            )

        return results
