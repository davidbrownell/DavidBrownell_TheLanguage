# ----------------------------------------------------------------------
# |
# |  MethodDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 08:53:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MethodDefinition object"""

import os
import re
import textwrap

from enum import auto, Enum
from typing import Any, cast, List, Optional, Union

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
    from ..Common import ParametersPhraseItem
    from ..Common.VisibilityModifier import VisibilityModifier
    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
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
class InvalidMethodNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid method name; names must start with an uppercase letter and be at least 2 characters.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid operator name.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassRestrictionError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Class restrictions may not be applied to methods marked as 'static'.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsRequiredError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Statements are required for methods not marked as 'abstract'.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsUnexpectedError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Statements can not be provided for methods marked as 'abstract' (use 'virtual' instead).")


# ----------------------------------------------------------------------
class MethodDefinitionStatement(GrammarPhrase):
    """\
    Defines a method associated with a class.

    <visibility>?
        ('static'|'abstract'|'virtual'|'override'|'final')?
        <type>
        <name>
        <parameter_phrase_item>
        ('mutable'|'immutable')?
        (':'
            <statement>+
        )?

    Examples:
        public static Int StaticFunc():
            pass

        public Int ImmutableFunc() immutable:
            pass

        private abstract Int AbstractFunc1() immutable
        private abstract Int AbstractFunc2() mutable
    """

    PHRASE_NAME                             = "Method Definition Statement"
    VALIDATION_EXPRESSION                   = re.compile(
        textwrap.dedent(
            r"""(?#
                Operator Method             )(?:^__[A-Z][a-zA-Z0-9_]+__\??$)(?#
                    - or -                  )|(?#
                Standard Method             )(?:^_?[A-Z][a-zA-Z0-9_]+\??(?!<__)$)(?#
            )""",
        ),
    )

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class MethodType(Enum):
        standard                            = auto()
        static                              = auto()
        abstract                            = auto()
        virtual                             = auto()
        override                            = auto()
        final                               = auto()

        # ----------------------------------------------------------------------
        @classmethod
        def CreatePhraseItem(cls):
            return tuple(e.name for e in cls)

        # ----------------------------------------------------------------------
        @classmethod
        def Extract(
            cls,
            node: Node,
        ) -> "MethodDefinitionStatement.MethodType":
            return cls[
                cast(
                    str,
                    ExtractToken(
                        cast(Leaf, ExtractOr(node)),
                        use_match=True,
                    ),
                )
            ]

    # ----------------------------------------------------------------------
    class ClassType(Enum):
        immutable                           = auto()
        mutable                             = auto()

        # ----------------------------------------------------------------------
        @classmethod
        def CreatePhraseItem(cls):
            return tuple(e.name for e in cls)

        # ----------------------------------------------------------------------
        @classmethod
        def Extract(
            cls,
            node: Node,
        ) -> "MethodDefinitionStatement.ClassType":
            return cls[
                cast(
                    str,
                    ExtractToken(
                        cast(Leaf, ExtractOr(node)),
                        use_match=True,
                    ),
                )
            ]

    # ----------------------------------------------------------------------
    class OperatorType(Enum):
        """\
        Note that operators are defined as '__<enum_name>__' such as '__ToBool__',
        '__Compare__", and "__Add__".
        """

        # Foundational
        ToBool                              = auto()
        ToString                            = auto()
        Repr                                = auto()
        Clone                               = auto()
        Serialize                           = auto()

        # Initialization (TODO: These names need work)
        Init                                = auto()
        PreInit                             = auto()

        # Dynamic
        GetAttribute                        = auto()
        Call                                = auto()
        Cast                                = auto()
        Index                               = auto()

        # Container
        Contains                            = auto()
        Length                              = auto()
        Iter                                = auto()
        AtEnd                               = auto()

        # Comparison
        Compare                             = auto()
        Equal                               = auto()
        NotEqual                            = auto()
        Less                                = auto()
        LessEqual                           = auto()
        Greater                             = auto()
        GreaterEqual                        = auto()

        # Logical
        And                                 = auto()
        Or                                  = auto()
        Not                                 = auto()

        # Mathematical
        Add                                 = auto()
        Subtract                            = auto()
        Multiply                            = auto()
        Divide                              = auto()
        DivideFloor                         = auto()
        Power                               = auto()
        Mod                                 = auto()
        Positive                            = auto()
        Negative                            = auto()

        AddInplace                          = auto()
        SubtractInplace                     = auto()
        MultiplyInplace                     = auto()
        DivideInplace                       = auto()
        DivideFloorInplace                  = auto()
        PowerInplace                        = auto()
        ModInplace                          = auto()

        # Bit Manipulation
        ShiftLeft                           = auto()
        ShiftRight                          = auto()
        BitAnd                              = auto()
        BitOr                               = auto()
        BitXor                              = auto()
        BitFlip                             = auto()

        ShiftLeftInplace                    = auto()
        ShiftRightInplace                   = auto()
        BitAndInplace                       = auto()
        BitOrInplace                        = auto()
        BitXorInplace                       = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(CommonEnvironment.ObjectReprImplBase):
        Visibility: VisibilityModifier
        MethodType: "MethodDefinitionStatement.MethodType"
        ReturnType: Union[Leaf, Node]
        Name: Union[str, "MethodDefinitionStatement.OperatorType"]
        Parameters: Any  # Defined in ParametersPhraseItem.py
        ClassType: Optional["MethodDefinitionStatement.ClassType"]
        Statements: Optional[List[Union[Leaf, Node]]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                include_class_info=False,
                Statements=lambda statements: None if statements is None else [statement.Type.Name for statement in statements],
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(MethodDefinitionStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # Method Type
                    PhraseItem(
                        name="Method Type",
                        item=self.MethodType.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.GenericName,

                    # <parameter_phrase_item>
                    ParametersPhraseItem.Create(),

                    # Class Type
                    PhraseItem(
                        name="Class Type",
                        item=self.ClassType.CreatePhraseItem(),
                        arity="?",
                    ),

                    # Definition or newline
                    (
                        PhraseItem(
                            name="Definition",
                            item=[
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

                        # Newline
                        CommonTokens.Newline,
                    ),
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
        assert len(nodes) == 7

        # Visibility
        if nodes[0] is None:
            visibility = VisibilityModifier.private
        else:
            visibility = VisibilityModifier.Extract(
                cast(Leaf, ExtractRepeat(cast(Node, nodes[0]))),
            )

        # Method type
        if nodes[1] is None:
            method_type = cls.MethodType.standard
        else:
            method_type = cls.MethodType.Extract(cast(Node, ExtractRepeat(cast(Node, nodes[1]))))

        # Return type
        return_type = ExtractDynamic(cast(Node, nodes[2]))

        # Method Name
        method_name_leaf = cast(Leaf, nodes[3])
        method_name = cast(str, ExtractToken(method_name_leaf))

        if not cls.VALIDATION_EXPRESSION.match(method_name):
            raise InvalidMethodNameError.FromNode(method_name_leaf, method_name)

        if method_name.startswith("__") and method_name.endswith("__"):
            try:
                method_name = cls.OperatorType[method_name[2:-2]]
            except KeyError:
                raise InvalidOperatorNameError.FromNode(method_name_leaf, method_name)

        # Parameters
        parameters = ParametersPhraseItem.Extract(cast(Node, nodes[4]))

        # Class type
        if nodes[5] is None:
            if method_type == cls.MethodType.static:
                class_type = None
            else:
                class_type = cls.ClassType.immutable
        else:
            class_type_node = cast(Node, nodes[5])

            class_type = cls.ClassType.Extract(cast(Node, ExtractRepeat(class_type_node)))

            if method_type == cls.MethodType.static:
                raise InvalidClassRestrictionError.FromNode(class_type_node)

        # Statements
        definition_or_newline_node = ExtractOr(cast(Node, nodes[6]))
        assert definition_or_newline_node.Type

        if definition_or_newline_node.Type.Name == "Definition":
            if method_type == cls.MethodType.abstract:
                raise StatementsUnexpectedError.FromNode(node)

            statements_nodes = ExtractSequence(cast(Node, definition_or_newline_node))
            assert len(statements_nodes) == 5

            statements = [ExtractDynamic(statement_node) for statement_node in cast(List[Node], ExtractRepeat(cast(Node, statements_nodes[3])))]

        else:
            if method_type != cls.MethodType.abstract:
                raise StatementsRequiredError.FromNode(node)

            statements = None

        # Commit the info
        object.__setattr__(
            node,
            "Info",
            # pylint: disable=too-many-function-args
            cls.NodeInfo(
                visibility,
                method_type,
                return_type,
                method_name,
                parameters,
                class_type,
                statements,
            ),
        )
