# ----------------------------------------------------------------------
# |
# |  FuncAndMethodDefinitionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-31 21:48:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncAndMethodDefinitionStatement object"""

import os

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
    from .ClassStatement import ClassStatement

    from ..Common import AttributesPhraseItem
    from ..Common.ClassModifier import ClassModifier
    from ..Common import ParametersPhraseItem
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Common.Impl.ModifierBase import ModifierBase

    from ...GrammarPhrase import GrammarPhrase, ValidationError

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid operator name.")  # type: ignore


# ----------------------------------------------------------------------
class FuncAndMethodDefinitionStatement(GrammarPhrase):
    """\
    Defines a function (or method when used within a class statement).
    """

    PHRASE_NAME                             = "Func And Method Definition Statement"

    # TODO: Captures

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class MethodType(ModifierBase):  # type: ignore
        standard                            = auto()
        deferred                            = auto()
        static                              = auto()
        abstract                            = auto()
        virtual                             = auto()
        override                            = auto()
        final                               = auto()

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

        Init                                = auto()
        PostInit                            = auto()

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
    class NodeInfo(GrammarPhrase.NodeInfo):
        Attributes: Any                                                     # Defined in AttributesPhrseItem.py
        Visibility: Optional[VisibilityModifier]
        MethodType: Optional["FuncAndMethodDefinitionStatement.MethodType"]
        ReturnType: Union[Leaf, Node]
        Name: Union[str, "FuncAndMethodDefinitionStatement.OperatorType"]
        Parameters: Any                                                     # Defined in ParametersPhraseItem.py
        ClassModifier: Optional[ClassModifier]
        Statements: Optional[List[Union[Leaf, Node]]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(FuncAndMethodDefinitionStatement.NodeInfo, self).__post_init__(
                Statements=None,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncAndMethodDefinitionStatement, self).__init__(
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

                    # <method_type>?
                    PhraseItem(
                        name="Method Type",
                        item=FuncAndMethodDefinitionStatement.MethodType.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.MethodName,

                    # <parameters>
                    ParametersPhraseItem.Create(),

                    # <class_modifier>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # - Multi-line Definition
                    # - Single-line Definition
                    # - Newline
                    (
                        # Multi-line, Single-line
                        StatementsPhraseItem.Create(),

                        # Newline (no content)
                        CommonTokens.Newline,
                    )
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
        assert len(nodes) == 8

        token_lookup = {}

        # <attributes>*
        attributes = AttributesPhraseItem.Extract(cast(Optional[Node], nodes[0]))

        # <visibility>?
        visibility_node = cast(Optional[Node], nodes[1])

        if visibility_node is not None:
            visibility = VisibilityModifier.Extract(ExtractOptional(visibility_node))
            token_lookup["Visibility"] = visibility_node
        else:
            visibility = None

        # <method_type>?
        method_type_node = cast(Optional[Node], nodes[2])

        if method_type_node is not None:
            method_type = cls.MethodType.Extract(ExtractOptional(method_type_node))
            token_lookup["MethodType"] = method_type_node
        else:
            method_type = None

        # <type>
        return_type = ExtractDynamic(cast(Node, nodes[3]))

        # <name>
        method_name_leaf = cast(Leaf, nodes[4])
        method_name = cast(str, ExtractToken(method_name_leaf))
        token_lookup["Name"] = method_name_leaf

        if method_name.startswith("__") and method_name.endswith("__"):
            try:
                method_name = cls.OperatorType[method_name[2:-2]]
            except KeyError:
                raise InvalidOperatorNameError.FromNode(method_name_leaf, method_name)

        # <parameters>
        parameters = ParametersPhraseItem.Extract(cast(Node, nodes[5]))

        # <class_modifier>?
        class_modifier_node = cast(Optional[Node], nodes[6])

        if class_modifier_node is not None:
            class_modifier = ClassModifier.Extract(ExtractOptional(class_modifier_node))
            token_lookup["ClassModifier"] = class_modifier_node
        else:
            class_modifier = None

        # <statements> or Newline
        statements_node = cast(Node, ExtractOr(cast(Node, nodes[7])))

        if isinstance(statements_node, Leaf):
            statements = None
        else:
            statements = StatementsPhraseItem.Extract(statements_node)

        # Commit the data
        object.__setattr__(
            node,
            "Info",
            cls.NodeInfo(
                token_lookup,
                attributes,
                visibility,
                method_type,
                return_type,
                method_name,
                parameters,
                class_modifier,
                statements,
            ),
        )
