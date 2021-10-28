# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 13:10:32
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
from typing import Callable, cast, Dict, List, Optional, Tuple, Union

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

    from ...Error import Error
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, CreateParserRegion, GetParserInfo

    from ....Parser.Statements.ClassStatementParserInfo import (
        ClassStatementDependencyParserInfo,
        ClassStatementParserInfo,
        ClassType,
    )

    # Convenience imports
    # <<unused-import> pylint: disable=W0611
    from ..Common.StatementsPhraseItem import (
        InvalidDocstringError,
        MultipleDocstringsError,
        MisplacedDocstringError,
        StatementsRequiredError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleBasesError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Classes can have only one base class; consider using interfaces, mixins, and traits instead.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateBaseTypeError(Error):
    Type: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The base type indicator '{Type}' may appear only once.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassStatementsRequiredError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Classes must have at least one statement.",
    )


# ----------------------------------------------------------------------
class ClassStatement(GrammarPhrase):
    """\
    Statement that creates a class.

    <attributes>?
    <visibility>?
    <class_type>?
    ('class' | 'enum' | 'exception' | 'interface' | 'mixin' | 'primitive' | 'struct' | 'trait')
    <name>
        '(' (<base_visibility>? <name>)? ')'
        (
            ('implements' | 'uses')) <name> (',' <name>)* ','?
        )*
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
    class BaseTypeIndicator(Enum):
        implements                          = auto()
        uses                                = auto()

    # ----------------------------------------------------------------------
    def __init__(self):
        # <visibility>? <name>
        base_item = PhraseItem.Create(
            name="Base Item",
            item=[
                # <visibility>?
                OptionalPhraseItem.Create(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # <generic_name>
                CommonTokens.GenericUpperName,
            ],
        )

        # <base_item> (',' <base_item>)* ','?
        base_items = PhraseItem.Create(
            name="Base Items",
            item=[
                # <base_item>
                base_item,

                # (',' <base_item>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Base",
                    item=[
                        ",",
                        base_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        super(ClassStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <attributes>*
                    AttributesPhraseItem.Create(),

                    # <visibility>? (class)
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # <class_modifier>?
                    OptionalPhraseItem.Create(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                    ),

                    # ('class' | 'enum' | 'exception' | 'interface' | 'mixin' | 'primitive' | 'struct' | 'trait')
                    PhraseItem.Create(
                        name="Class Type",
                        item=self.__class__._CreateClassTypePhraseItem(),
                    ),

                    # <name> (class)
                    CommonTokens.GenericUpperName,

                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    OptionalPhraseItem.Create(
                        name="Base Items",
                        item=base_items,
                    ),

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",

                    # Implements/Uses
                    CommonTokens.PushIgnoreWhitespaceControl,

                    ZeroOrMorePhraseItem.Create(
                        name="Implements and Uses",
                        item=[
                            # ('implements' | 'uses')
                            self.__class__.BaseTypeIndicator.CreatePhraseItem(),  # type: ignore

                            # Items
                            PhraseItem.Create(
                                item=(
                                    # '(' <base_items> ')'
                                    PhraseItem.Create(
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
                                ambiguities_resolved_by_order=True,
                            ),
                        ],
                    ),

                    CommonTokens.PopIgnoreWhitespaceControl,

                    StatementsPhraseItem.Create(),
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
        nodes = ExtractSequence(node)
        assert len(nodes) == 14

        # <attributes>*
        attributes_node = cast(Optional[AST.Node], nodes[0])
        attribute_data = AttributesPhraseItem.ExtractLexerData(attributes_node)

        # TODO: Leverage attribute_data

        # <visibility>?
        visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
        if visibility_node is None:
            visibility_info = None
        else:
            visibility_info = VisibilityModifier.Extract(visibility_node)

        # <class_modifier>?
        class_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if class_modifier_node is None:
            class_modifier_info = None
        else:
            class_modifier_info = ClassModifier.Extract(class_modifier_node)

        # <class_type>
        class_type_node = cast(AST.Node, nodes[3])
        class_type_info = cls._ExtractClassType(class_type_node)

        # <generic_name>
        class_name_leaf = cast(AST.Leaf, nodes[4])
        class_name_info = cast(str, ExtractToken(class_name_leaf))

        if not CommonTokens.TypeNameRegex.match(class_name_info):
            raise CommonTokens.InvalidTokenError.FromNode(class_name_leaf, class_name_info, "type")

        # Base Info
        base_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
        if base_node is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(base_node)
            assert base_infos

            if len(base_infos) > 1:
                raise MultipleBasesError.FromNode(base_node)

            base_info = base_infos[0]

        # Implements/Uses
        implements_and_uses: Dict[
            ClassStatement.BaseTypeIndicator,
            Tuple[
                AST.Node,
                List[ClassStatementDependencyParserInfo],
            ]
        ] = {}

        for this_base_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[11]))):
            base_nodes = ExtractSequence(this_base_node)
            assert len(base_nodes) == 2

            # 'implements' | 'uses'
            base_type_node = cast(AST.Node, base_nodes[0])
            base_type_info = cls.BaseTypeIndicator.Extract(base_type_node)  # type: ignore

            if base_type_info in implements_and_uses:
                raise DuplicateBaseTypeError.FromNode(base_type_node, base_type_info.name)

            # Items
            base_node_items = cast(AST.Node, ExtractOr(cast(AST.Node, base_nodes[1])))

            assert base_node_items.Type is not None
            if base_node_items.Type.Name == "Grouped":
                base_node_items = cast(AST.Node, ExtractSequence(base_node_items)[2])

            implements_and_uses[base_type_info] = (
                this_base_node,
                cls._ExtractBaseInfo(base_node_items),
            )

        # Statements
        statements_node = cast(AST.Node, nodes[13])

        # Note that the statements aren't fully available right now, so we will
        # have to extract that information on the second pass

        parser_info = ClassStatementParserInfo(
            CreateParserRegions(
                node,
                visibility_node,
                class_modifier_node,
                class_type_node,
                class_name_leaf,
                base_node,
                implements_and_uses.get(cls.BaseTypeIndicator.implements, (None,))[0],
                implements_and_uses.get(cls.BaseTypeIndicator.uses, (None,))[0],
                statements_node,
                None,
            ),  # type: ignore
            visibility_info,  # type: ignore
            class_modifier_info,  # type: ignore
            class_type_info,
            class_name_info,
            base_info,
            implements_and_uses.get(cls.BaseTypeIndicator.implements, (None, None))[1],
            implements_and_uses.get(cls.BaseTypeIndicator.uses, (None, None))[1],
        )

        # ----------------------------------------------------------------------
        def FinalConstruct():
            # <statement>+
            (
                statement_info,
                docstring_info,
            ) = StatementsPhraseItem.ExtractParserInfoWithDocstrings(statements_node)

            if docstring_info is not None:
                docstring_info = (
                    docstring_info[0],
                    CreateParserRegion(docstring_info[1]),
                )

                if not statement_info:
                    raise ClassStatementsRequiredError.FromNode(statements_node)

            parser_info.FinalConstruct(statement_info, docstring_info)

            return parser_info

        # ----------------------------------------------------------------------

        return (parser_info, FinalConstruct)

    # ----------------------------------------------------------------------
    @classmethod
    def GetContainingClassParserInfo(
        cls,
        child_node: AST.Node,
        # Taking this as a parameter to avoid circular dependencies, as
        # FuncDefinitionStatement.py imports this file.
        func_definition_statement_phrase_name: str,
    ) -> Optional[ClassStatementParserInfo]:
        """Returns the ClassStatementParserInfo for the class that contains the given node (if any)"""

        node = child_node.Parent

        while node is not None:
            if node.Type is not None:
                if node.Type.Name == cls.PHRASE_NAME:
                    return cast(ClassStatementParserInfo, GetParserInfo(node))

                if node.Type.Name == func_definition_statement_phrase_name:
                    break

            node = node.Parent

        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _CreateClassTypePhraseItem              = staticmethod(ModifierImpl.ByValueCreatePhraseItemFuncFactory(ClassType))
    _ExtractClassType                       = staticmethod(ModifierImpl.ByValueExtractFuncFactory(ClassType))

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractBaseInfo(
        cls,
        node: AST.Node,
    ) -> List[ClassStatementDependencyParserInfo]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        results: List[ClassStatementDependencyParserInfo] = []

        for base_item in itertools.chain(
            [nodes[0]],
            [
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(
                    List[AST.Node],
                    ExtractRepeat(cast(Optional[AST.Node], nodes[1])),
                )
            ],
        ):
            assert base_item is not None

            base_items = ExtractSequence(cast(AST.Node, base_item))
            assert len(base_items) == 2

            # <visibility>?
            visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], base_items[0])))
            if visibility_node is None:
                visibility_info = None
            else:
                visibility_info = VisibilityModifier.Extract(visibility_node)

            # <generic_name>
            name_leaf = cast(AST.Leaf, base_items[1])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.TypeNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "type")

            results.append(
                # pylint: disable=too-many-function-args
                ClassStatementDependencyParserInfo(
                    CreateParserRegions(node, visibility_node, name_leaf),  # type: ignore
                    visibility_info,  # type: ignore
                    name_info,
                ),
            )

        assert results
        return results


ClassStatement.BaseTypeIndicator.CreatePhraseItem       = staticmethod(ModifierImpl.StandardCreatePhraseItemFuncFactory(ClassStatement.BaseTypeIndicator))  # type: ignore
ClassStatement.BaseTypeIndicator.Extract                = staticmethod(ModifierImpl.StandardExtractFuncFactory(ClassStatement.BaseTypeIndicator))  # type: ignore
