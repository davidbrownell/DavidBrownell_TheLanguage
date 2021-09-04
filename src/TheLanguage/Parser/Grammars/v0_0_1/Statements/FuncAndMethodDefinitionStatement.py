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

    from ..Common.ClassModifier import ClassModifier
    from ..Common import ParametersPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Common.Impl.ModifierBase import ModifierBase

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
class InvalidMethodTypeApplicationError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Method modifiers may not be used on functions.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorApplicationError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Operators must be methods.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierApplicationFunctionError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Class modifiers may not be used on functions.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidClassModifierApplicationStaticError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Class modifiers may not be used on static methods.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidOperatorNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid operator name.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FunctionStatementsRequiredError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Statements are required for functions.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MethodStatementsRequiredError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Statements are required for methods not marked as 'abstract'.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementsUnexpectedError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Statements can not be provided for methods marked as 'abstract' (use 'virtual' instead).")  # type: ignore


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
        IsFunction: bool
        Visibility: VisibilityModifier
        MethodType: Optional["FuncAndMethodDefinitionStatement.MethodType"]
        ReturnType: Union[Leaf, Node]
        Name: Union[str, "FuncAndMethodDefinitionStatement.OperatorType"]
        Parameters: Any  # Defined in ParametersPhraseItem.py
        ClassModifier: Optional[ClassModifier]
        Statements: Optional[List[Union[Leaf, Node]]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            if self.IsFunction:
                assert self.MethodType is None, self
                assert isinstance(self.Name, str), self
                assert self.ClassModifier is None, self
                assert self.Statements, self

            else:
                assert self.MethodType is not None, self
                assert self.ClassModifier is not None, self
                assert self.Statements or self.MethodType == FuncAndMethodDefinitionStatement.MethodType.abstract, self

            super(FuncAndMethodDefinitionStatement.NodeInfo, self).__post_init__(
                Statements=lambda statements: None if statements is None else [statement.Type.Name for statement in statements],
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
                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <method_type>?
                    PhraseItem(
                        name="Method Type",
                        item=self.MethodType.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <name>
                    CommonTokens.MethodName,

                    # <parameters>
                    ParametersPhraseItem.Create(),

                    # <class_type>?
                    PhraseItem(
                        name="Class Modifier",
                        item=ClassModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # TODO: Move ':' here

                    # - Multi-line Definition
                    # - Single-line Definition
                    # - Newline
                    (
                        PhraseItem(
                            name="Multi-line Definition",
                            item=[
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

                        PhraseItem(
                            name="Single-line Definition",
                            item=[
                                ":",
                                DynamicPhrasesType.Statements,
                            ],
                        ),

                        CommonTokens.Newline,
                    )
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateSyntax(
        self,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # Determine if this is function or a method. This is a function if:
        #   - It is embedded within another function/method
        #   - It is not embedded within a class

        # ----------------------------------------------------------------------
        def IsFunction() -> bool:
            parent = node.Parent

            while parent:
                if parent.Type is not None:
                    if parent.Type.Name == self.PHRASE_NAME:
                        return True

                    if parent.Type.Name == ClassStatement.PHRASE_NAME:
                        return False

                parent = parent.Parent

            return True

        # ----------------------------------------------------------------------

        is_function = IsFunction()

        # Extract the info
        nodes = ExtractSequence(node)
        assert len(nodes) == 7

        # <visibility>?
        if nodes[0] is None:
            visibility = VisibilityModifier.private
        else:
            visibility = VisibilityModifier.Extract(
                cast(Node, ExtractRepeat(cast(Node, nodes[0]))),
            )

        # <method_type>?
        if nodes[1] is None:
            if is_function:
                method_type = None
            else:
                method_type = self.MethodType.standard
        else:
            if is_function:
                raise InvalidMethodTypeApplicationError.FromNode(nodes[1])

            method_type = self.MethodType.Extract(cast(Node, ExtractRepeat(cast(Node, nodes[1]))))

        # <type>
        return_type = ExtractDynamic(cast(Node, nodes[2]))

        # <name>
        method_name_leaf = cast(Leaf, nodes[3])
        method_name = cast(str, ExtractToken(method_name_leaf))

        if method_name.startswith("__") and method_name.endswith("__"):
            if is_function:
                raise InvalidOperatorApplicationError.FromNode(method_name_leaf)

            try:
                method_name = self.OperatorType[method_name[2:-2]]
            except KeyError:
                raise InvalidOperatorNameError.FromNode(method_name_leaf, method_name)

        # <parameters>
        parameters = ParametersPhraseItem.Extract(cast(Node, nodes[4]))

        # <class_type>?
        if nodes[5] is None:
            if is_function:
                class_type = None
            else:
                class_type = ClassModifier.immutable
        else:
            if is_function:
                raise InvalidClassModifierApplicationFunctionError.FromNode(nodes[5])

            if method_type == self.MethodType.static:
                raise InvalidClassModifierApplicationStaticError.FromNode(nodes[5])

            class_type = ClassModifier.Extract(cast(Node, ExtractRepeat(cast(Node, nodes[5]))))

        # Statements
        statement_node = ExtractOr(cast(Node, nodes[6]))

        if isinstance(statement_node, Leaf):
            if method_type != self.MethodType.abstract:
                if is_function:
                    raise FunctionStatementsRequiredError.FromNode(statement_node)
                else:
                    raise MethodStatementsRequiredError.FromNode(statement_node)

            statements = None

        else:
            assert isinstance(statement_node, Node)
            assert statement_node.Type

            if method_type == self.MethodType.abstract:
                raise StatementsUnexpectedError.FromNode(statement_node)

            statements_nodes = ExtractSequence(statement_node)

            if statement_node.Type.Name == "Multi-line Definition":
                assert len(statements_nodes) == 5

                statements = [
                    ExtractDynamic(statement_node)
                    for statement_node in cast(List[Node], ExtractRepeat(cast(Node, statements_nodes[3])))
                ]

            elif statement_node.Type.Name == "Single-line Definition":
                assert len(statements_nodes) == 2

                statements = [
                    ExtractDynamic(cast(Node, statements_nodes[1])),
                ]

            else:
                assert False, statement_node.Type

            assert statements

        # Commit the info
        object.__setattr__(
            node,
            "Info",
            self.NodeInfo(
                is_function,
                visibility,  # type: ignore
                method_type,
                return_type,
                method_name,
                parameters,
                class_type,  # type: ignore
                statements,
            ),
        )
