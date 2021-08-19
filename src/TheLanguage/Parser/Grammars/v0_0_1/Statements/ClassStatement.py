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
import re

from enum import auto, Enum
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
    from ..Common import Tokens as CommonTokens
    from ..Common.VisibilityModifier import VisibilityModifier

    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
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
class InvalidClassNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid class name; names must start with an uppercase letter and be at least 2 characters.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateInterfacesTypeError(ValidationError):
    Type: str

    MessageTemplate                         = Interface.DerivedProperty("The base type indicator '{Type}' may only appear once.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleBasesError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Classes can have only one base class; consider using mixins and interfaces instead.")


# ----------------------------------------------------------------------
# TODO: Add modifier to control what can be in class ("static", "mutable", "immutable", "abstract", "virtual", "override"?)
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
    VALIDATION_EXPRESSION                   = re.compile(r"^_?[A-Z][a-zA-Z0-9_\.]+(?!<__)$")

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class ClassType(Enum):
        Class                               = "class"
        Enum                                = "enum"
        Exception                           = "exception"
        Interface                           = "interface"
        Mixin                               = "mixin"

        # ----------------------------------------------------------------------
        @classmethod
        def CreatePhraseItem(cls):
            return tuple(e.value for e in cls)

        # ----------------------------------------------------------------------
        @classmethod
        def Extract(
            cls,
            node: Node,
        ) -> "ClassStatement.ClassType":
            value = cast(
                str,
                ExtractToken(
                    cast(Leaf, ExtractOr(node)),
                    use_match=True,
                ),
            )

            for e in cls:
                if e.value == value:
                    return e

            assert False, value

    # ----------------------------------------------------------------------
    class BaseTypeIndicator(Enum):
        implements                          = auto()
        uses                                = auto()

        # ----------------------------------------------------------------------
        @classmethod
        def CreatePhraseItem(cls):
            return tuple(e.name for e in cls)

        # ----------------------------------------------------------------------
        @classmethod
        def Extract(
            cls,
            node: Node,
        ) -> "ClassStatement.BaseTypeIndicator":
            value = cast(
                str,
                ExtractToken(
                    cast(Leaf, ExtractOr(node)),
                    use_match=True,
                ),
            )
            return cls[value]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class BaseInfo(CommonEnvironment.ObjectReprImplBase):
        Visibility: VisibilityModifier
        Name: str

        # ----------------------------------------------------------------------
        def __post_init__(self):
            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                include_class_info=False,
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(CommonEnvironment.ObjectReprImplBase):
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
            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                include_class_info=False,
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
                CommonTokens.GenericName,
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
                    CommonTokens.GenericName,

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
                            (
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
                        ],
                        arity="*",
                    ),

                    CommonTokens.PopIgnoreWhitespaceControl,

                    # ':'
                    ":",
                    CommonTokens.Newline,
                    CommonTokens.Indent,

                    # <statement>+
                    PhraseItem(
                        name="Statements",
                        item=DynamicPhrasesType.Statements,
                        arity="+",
                    ),

                    # End
                    CommonTokens.Dedent,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        nodes = ExtractSequence(node)
        assert len(nodes) == 16

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
                cast(Leaf, ExtractRepeat(cast(Node, nodes[0]))),
            )

        # Class name
        class_name = cast(str, ExtractToken(cast(Leaf, nodes[2])))

        if not cls.VALIDATION_EXPRESSION.match(class_name):
            raise InvalidClassNameError.FromNode(cast(Leaf, nodes[2]), class_name)

        # Base info
        if nodes[5] is None:
            base_info = None
        else:
            base_infos = cls._ExtractBaseInfo(cast(Node, ExtractRepeat(cast(Node, nodes[5]))))
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
        statements = cast(List[Union[Leaf, Node]], ExtractRepeat(cast(Node, nodes[14])))

        # Commit the results
        object.__setattr__(
            node,
            "Info",
            # pylint: disable=too-many-function-args
            cls.NodeInfo(
                class_type,
                class_name,
                class_visibility,
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
                    cast(Leaf, ExtractRepeat(cast(Node, base_items[0]))),
                )

            # Name
            name = cast(str, ExtractToken(cast(Leaf, base_items[1])))

            if not cls.VALIDATION_EXPRESSION.match(name):
                raise InvalidClassNameError.FromNode(cast(Leaf, base_items[1]), name)

            results.append(cls.BaseInfo(visibility, name))

        return results
