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
from typing import cast, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.Impl.ModifierBase import CreateModifierBaseClass, ModifierBase
    from ..Common.VisibilityModifier import VisibilityModifier

    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Phrases.DSL import (
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
# TODO: Add modifier to control what can be in class ("mutable", "immutable")
class ClassStatement(GrammarPhrase):
    """\
    Statement that creates a class.

    <visibility>? 'class'|'interface'|'mixin'|'enum'|'exception' <name>
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
        Visibility: VisibilityModifier
        Name: str

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(GrammarPhrase.NodeInfo):
        Type: "ClassStatement.ClassType"
        Name: str
        Visibility: VisibilityModifier
        Base: Optional["ClassStatement.BaseInfo"]
        Interfaces: List["ClassStatement.BaseInfo"]
        Mixins: List["ClassStatement.BaseInfo"]
        Statements: List[Union[Leaf, Node]]

        # TODO: Need to store leaf info for all of this

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
                    # TODO: Attributes

                    # <visibility>? (class)
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
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
        assert len(nodes) == 12

        # Get the class type before the visibility, as the class type will impact the default value
        # applied for the visibility if one wasn't explicitly specified.

        # Class type
        class_type = cls.ClassType.Extract(cast(Node, nodes[1]))

        # Validate the visibility modifier
        if nodes[0] is None:
            if class_type == cls.ClassType.Exception:
                class_visibility = VisibilityModifier.public
            else:
                class_visibility = VisibilityModifier.private
        else:
            class_visibility = VisibilityModifier.Extract(
                cast(Node, ExtractOptional(cast(Node, nodes[0]))),
            )

        # Class name
        class_name = cast(str, ExtractToken(cast(Leaf, nodes[2])))

        # Base info
        if nodes[5] is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(cast(Node, ExtractOptional(cast(Node, nodes[5]))))
            assert base_infos

            if len(base_infos) > 1:
                raise MultipleBasesError.FromNode(cast(Node, nodes[5]))

            base_info = base_infos[0]

        # Interfaces and mixins
        interfaces_and_mixins = {}

        for base_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[9]))):
            base_nodes = ExtractSequence(base_node)
            assert len(base_nodes) == 2

            # 'implements'|'uses'
            base_type_node = cast(Node, base_nodes[0])
            base_type = cls.BaseTypeIndicator.Extract(base_type_node)

            if base_type in interfaces_and_mixins:
                raise DuplicateInterfacesTypeError.FromNode(base_type_node, base_type.name)

            # Items
            base_node_items = cast(Node, ExtractOr(cast(Node, base_nodes[1])))
            assert base_node_items.Type

            if base_node_items.Type.Name == "Grouped":
                base_node_items = ExtractSequence(base_node_items)[2]

            interfaces_and_mixins[base_type] = cls._ExtractBaseInfo(cast(Node, base_node_items))

        # Statements
        statements = StatementsPhraseItem.Extract(cast(Node, nodes[11]))

        # Commit the results
        object.__setattr__(
            node,
            "Info",
            # pylint: disable=too-many-function-args
            cls.NodeInfo(
                class_type,
                class_name,
                class_visibility,  # type: ignore
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

        results = []

        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        for base_item in itertools.chain(
            [nodes[0]],
            [ExtractSequence(node)[1] for node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[1])))],
        ):
            base_items = ExtractSequence(cast(Node, base_item))
            assert len(base_items) == 2

            # Visibility
            if base_items[0] is None:
                visibility = VisibilityModifier.private
            else:
                visibility = VisibilityModifier.Extract(
                    cast(Node, ExtractOptional(cast(Node, base_items[0]))),
                )

            # Name
            name = cast(str, ExtractToken(cast(Leaf, base_items[1])))

            # Commit the results

            # pylint: disable=too-many-function-args
            results.append(cls.BaseInfo(visibility, name))  # type: ignore

        return results
