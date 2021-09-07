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

from enum import auto
from typing import Any, cast, List, Optional

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
    from ..Common.ClassModifier import ClassModifier
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.Impl.ModifierBase import CreateModifierBaseClass, ModifierBase
    from ..Common.VisibilityModifier import VisibilityModifier

    from ...GrammarPhrase import GrammarPhrase, ValidationError
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
    class ClassType(
        CreateModifierBaseClass(  # type: ignore
            by_value=True,
        ),
    ):
        # <Line too long> pylint: disable=C0301
        """\
        |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
        |           | Default Visibility |    Allowed Visibilities    | Default Member Visibility | Allowed Member Visibilities | Default Method Type |               Allowed Method Types                   |    Allow Method Definitions?   | Default Class Modifier | Allowed Class Modifiers | Requires Special Member Definitions | Allows Data Members? | Allows Mutable Public Data Members? |          Can Be Instantiated Directly?           | Bases? | Interfaces? | Mixins? |           |
        |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
        | Primitive |      private       | public, protected, private |          public           |           public            |      deferred       |        deferred, standard (for special members)      | yes (only for special members) |        immutable       |    mutable, immutable   |                 yes                 |          yes         |                 no                  |                       yes                        |   no   |      no     |   no    | Primitive |
        | Class     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   |     Class |
        | Struct    |      private       |          private           |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |         mutable        |         mutable         |   no (defaults will be generated)   |          yes         |                 yes                 |                       yes                        |   yes  |      no     |   no    |    Struct |
        | Exception |      public        |          public            |          public           | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |        immutable        |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      yes    |   yes   | Exception |
        | Enum      |      private       | public, protected, private |          public           |           public            |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          yes         |                 no                  |                       yes                        |   yes  |      no     |   no    |      Enum |
        | Interface |      private       | public, protected, private |          public           |           public            |      abstract       |       static, abstract, virtual, override, final     |               yes              |        immutable       |    mutable, immutable   |   no (defaults will be generated)   |          no          |                 no                  |     no (must be implemented by a super class)    |   no   |      yes    |   no    | Interface |
        | Mixin     |      private       | public, protected, private |          private          | public, protected, private  |      standard       | standard, static, abstract, virtual, override, final |               yes              |        immutable       |    mutable, immutable   |                 no                  |          yes         |                 no                  | no (functionality is "grafted" into super class) |   yes  |      no     |   yes   |     Mixin |
        |-----------|--------------------|----------------------------|---------------------------|-----------------------------|---------------------|------------------------------------------------------|--------------------------------|------------------------|-------------------------|-------------------------------------|----------------------|-------------------------------------|--------------------------------------------------|--------|-------------|---------|-----------|
        """

        Primitive                           = "primitive"
        Class                               = "class"
        Struct                              = "struct"
        Exception                           = "exception"
        Enum                                = "enum"
        Interface                           = "interface"
        Mixin                               = "mixin"

        # TODO: Enum doesn't seem to fit here

    # ----------------------------------------------------------------------
    class BaseTypeIndicator(ModifierBase):  # type: ignore
        implements                          = auto()
        uses                                = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class BaseInfo(GrammarPhrase.NodeInfo):
        Visibility: Optional[VisibilityModifier]
        Name: str

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(GrammarPhrase.NodeInfo):
        Attributes: Any                                 # Defined in AttributesPhraseItem.py
        Visibility: Optional[VisibilityModifier]
        Modifier: Optional[ClassModifier]
        Type: "ClassStatement.ClassType"
        Name: str
        Base: Optional["ClassStatement.BaseInfo"]
        Interfaces: List["ClassStatement.BaseInfo"]
        Mixins: List["ClassStatement.BaseInfo"]
        Statements: Any                                 # Defined in StatementsPhraseItem.py

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(ClassStatement.NodeInfo, self).__post_init__(
                Statements=None,
            )

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
                        item=self.ClassType.CreatePhraseItem(),
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
        nodes = ExtractSequence(node)
        assert len(nodes) == 14

        token_lookup = {}

        # <attributes>?
        attributes = AttributesPhraseItem.Extract(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], nodes[1])

        if visibility_node is not None:
            visibility = VisibilityModifier.Extract(ExtractOptional(visibility_node))
            token_lookup["Visibility"] = visibility_node
        else:
            visibility = None

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], nodes[2])

        if class_modifier_node is not None:
            class_modifier = ClassModifier.Extract(ExtractOptional(class_modifier_node))
            token_lookup["Modifier"] = class_modifier_node
        else:
            class_modifier = None

        # <class_type>
        class_type_node = cast(Node, nodes[3])
        class_type = cls.ClassType.Extract(class_type_node)
        token_lookup["Type"] = class_type_node

        # <name>
        class_name_leaf = cast(Leaf, nodes[4])
        class_name = cast(str, ExtractToken(class_name_leaf))
        token_lookup["Name"] = class_name_leaf

        # Base Info
        base_info_node = cast(Optional[Node], nodes[7])

        if base_info_node is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(cast(Node, ExtractOptional(base_info_node)))
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

        # Commit the data
        object.__setattr__(
            node,
            "Info",
            cls.NodeInfo(
                token_lookup,
                attributes,
                visibility,
                class_modifier,
                class_type,
                class_name,
                base_info,
                interfaces_and_mixins.get(cls.BaseTypeIndicator.implements, []),
                interfaces_and_mixins.get(cls.BaseTypeIndicator.uses, []),
                statements,
            ),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractBaseInfo(
        cls,
        node: Node,
    ) -> List["ClassStatement.BaseInfo"]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        results: List[ClassStatement.BaseInfo] = []

        for base_item in itertools.chain(
            [nodes[0]],
            [ExtractSequence(node)[1] for node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[1])))],
        ):
            base_items = ExtractSequence(cast(Node, base_item))
            assert len(base_items) == 2

            token_lookup = {}

            # <visibility>?
            visibility_node = cast(Optional[Node], base_items[0])

            if visibility_node is not None:
                visibility = VisibilityModifier.Extract(ExtractOptional(visibility_node))
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
                cls.BaseInfo(
                    token_lookup,
                    visibility,  # type: ignore
                    name,
                ),
            )

        return results
