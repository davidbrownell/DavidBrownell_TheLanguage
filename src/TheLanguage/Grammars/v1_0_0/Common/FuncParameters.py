# ----------------------------------------------------------------------
# |
# |  FuncParameters.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-17 20:53:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality support function/method parameters"""

import itertools
import os
import textwrap

from enum import auto, Enum
from typing import cast, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import StringHelpers
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .GrammarAST import (
        ExtractDynamicExpressionNode,
        ExtractLeafValue,
        ExtractOptionalNode,
        ExtractOrNode,
        ExtractRepeatedNodes,
        Leaf,
        Node,
        Statement,
    )

    from . import GrammarDSL
    from . import NamingConventions
    from . import Tokens as CommonTokens

    from ...GrammarStatement import ValidationError

    from ....ParserImpl.Token import Token


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParameterInfo(object):
    ParameterNode: Node
    TypeNode: Node
    NameLeaf: Leaf

    Name: str
    DefaultValue: Optional[Node]

    # TODO: Should arity apply to all parameters?
    VarArgs: bool                           = False

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.ToString()

    # ----------------------------------------------------------------------
    def ToString(
        self,
        verbose=False,
    ) -> str:
        return textwrap.dedent(
            """\
            {name}
                Parameter: [{param_start_line}, {param_start_col} -> {param_end_line}, {param_end_col}]
                Type: [{type_start_line}, {type_start_col} -> {type_end_line}, {type_end_col}]
                Name: [{name_start_line}, {name_start_col} -> {name_end_line}, {name_end_col}]
                Default:{default}
            """,
        ).format(
            name=self.Name,
            param_start_line=self.ParameterNode.IterBefore.Line,
            param_start_col=self.ParameterNode.IterBefore.Column,
            param_end_line=self.ParameterNode.IterAfter.Line,
            param_end_col=self.ParameterNode.IterAfter.Column,
            type_start_line=self.TypeNode.IterBefore.Line,
            type_start_col=self.TypeNode.IterBefore.Column,
            type_end_line=self.TypeNode.IterAfter.Line,
            type_end_col=self.TypeNode.IterAfter.Column,
            name_start_line=self.NameLeaf.IterBefore.Line,
            name_start_col=self.NameLeaf.IterBefore.Column,
            name_end_line=self.NameLeaf.IterAfter.Line,
            name_end_col=self.NameLeaf.IterAfter.Column,
            default=" <No Default>" if not self.DefaultValue else "\n        {}\n".format(
                StringHelpers.LeftJustify(
                    self.DefaultValue.ToString(
                        verbose=verbose,
                    ).rstrip(),
                    8,
                ),
            ),
        )

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Parameters(object):
    Positional: List[ParameterInfo]
    Any: List[ParameterInfo]
    Keyword: List[ParameterInfo]

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.ToString()

    # ----------------------------------------------------------------------
    def ToString(
        self,
        verbose=False,
    ) -> str:
        return textwrap.dedent(
            """\
            Positional:
                {positional}
            Any:
                {any}
            Keyword:
                {keyword}
            """,
        ).format(
            positional=StringHelpers.LeftJustify(
                ("\n".join(
                    [
                        param.ToString(
                            verbose=verbose,
                        )
                        for param in self.Positional
                    ],
                ) if self.Positional else "<No Parameters>").rstrip(),
                4,
            ),
            any=StringHelpers.LeftJustify(
                ("\n".join(
                    [
                        param.ToString(
                            verbose=verbose,
                        )
                        for param in self.Any
                    ],
                ) if self.Any else "<No Parameters>").rstrip(),
                4,
            ),
            keyword=StringHelpers.LeftJustify(
                ("\n".join(
                    [
                        param.ToString(
                            verbose=verbose,
                        )
                        for param in self.Keyword
                    ],
                ) if self.Keyword else "<No Parameters>").rstrip(),
                4,
            ),
        )

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateParameterNameError(ValidationError):
    ParameterName: str

    MessageTemplate                         = Interface.DerivedProperty("The parameter name '{ParameterName}' has already been specified")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NonDefaultParameterAfterDefaultValueParameterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Parameters without a default value may not appear after a parameter with a default value has been defined")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NewStyleParameterGroupOrderingError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Parameter groups must appear in the order {}".format(", ".join(token.Name for token in CommonTokens.AllNewStyleParameters)))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NewStyleParameterGroupDuplicateError(ValidationError):
    GroupName: str

    MessageTemplate                         = Interface.DerivedProperty("The parameter group '{GroupName}' has already been specified")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterOrderError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) must appear before the keyword delimiter ({})".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDuplicateKeywordDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ({}) may only appear once in a list of parameters".format(
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDuplicatePositionalDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) may only appear once in a list of parameters".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalKeywordDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ({}) must appear before at least 1 parameter".format(
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalPositionalDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) must appear after at least 1 parameter".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateStatement() -> Statement:
    """\
    Function or method parameters.

    '(' <args> ')'
    """

    parameter_statement = GrammarDSL.StatementItem(
        name="Parameter",
        item=[
            # <type> '*'? <name> ('=' <expr>)?
            GrammarDSL.DynamicStatements.Types,
            GrammarDSL.StatementItem(
                name="Arity",
                item=CommonTokens.FunctionParameterVarArgsType,
                arity="?",
            ),
            CommonTokens.Name,
            GrammarDSL.StatementItem(
                name="With Default",
                item=[
                    CommonTokens.Equal,
                    GrammarDSL.DynamicStatements.Expressions,
                ],
                arity="?",
            ),
        ],
    )

    return GrammarDSL.CreateStatement(
        name="Parameters",
        item=[
            # '('
            CommonTokens.LParen,
            CommonTokens.PushIgnoreWhitespaceControl,

            # <parameters>?
            GrammarDSL.StatementItem(
                item=(
                    # New Style:
                    #
                    #        <type> Func(
                    #            pos: <type> a, <type> b, <type> c,
                    #            any:
                    #               <type> d,
                    #               <type>e=100,
                    #            key: <type> f=200, <type> g=300,
                    #        ):
                    #            <statements>
                    #
                    GrammarDSL.StatementItem(
                        name="New Style",
                        item=[
                            tuple(CommonTokens.AllNewStyleParameters),
                            CommonTokens.Colon,
                            GrammarDSL.CreateDelimitedStatementItem(parameter_statement),
                        ],
                        arity=(1, len(CommonTokens.AllNewStyleParameters)),
                    ),

                    # Traditional:
                    #
                    #       # Exactly matches the new-style definition above:
                    #       #
                    #       #   - Everything before '/' is positional
                    #       #   - Everything after '/' and before '*' is any
                    #       #   - Everything after '*' is keyword
                    #       #
                    #       <type> Func(<type> a, <type> b, <type> c, /, <type> d, <type> e=100, *, <type> f=200, <type> g=300):
                    #           <statements>
                    #
                    #       # No restriction on positional or keyword parameters
                    #       <type> Func(<type> a, <type> b, <type> c, <type> d, <type> e=100, <type> f=200, <type> g=300):
                    #           <statement>
                    GrammarDSL.CreateDelimitedStatementItem(
                        name="Traditional",
                        item=(
                            parameter_statement,
                            CommonTokens.FunctionParameterPositionalDelimiter,
                            CommonTokens.FunctionParameterKeywordDelimiter,
                        ),
                    ),
                ),
                arity="?",
            ),

            # ')'
            CommonTokens.PopIgnoreWhitespaceControl,
            CommonTokens.RParen,
        ],
    )


# ----------------------------------------------------------------------
def Extract(
    node: Node,
) -> Parameters:
    child_index = 0

    # '('
    assert len(node.Children) >= child_index + 1
    child_index += 1

    # <parameters>?
    potential_parameters_node = ExtractOptionalNode(node, child_index)
    if potential_parameters_node is not None:
        child_index += 1

        parameters_node = cast(Node, ExtractOrNode(cast(Node, potential_parameters_node)))

        potential_new_style_children = ExtractRepeatedNodes(
            parameters_node,
            name="New Style",
        )

        if potential_new_style_children is not None:
            parameters = _ExtractNewStyleParameters(cast(List[Node], potential_new_style_children))
        else:
            parameters = _ExtractTraditionalParameters(parameters_node)
    else:
        parameters = Parameters([], [], [])

    # ')'
    assert len(node.Children) >= child_index
    child_index += 1

    assert len(node.Children) == child_index

    # Check for error conditions
    parameter_names = set()
    encountered_default = False

    # TODO: Handle var args

    for parameter_info in itertools.chain(
        parameters.Positional,
        parameters.Any,
        parameters.Keyword,
    ):
        # Check for duplicate names
        if parameter_info.Name in parameter_names:
            raise DuplicateParameterNameError.FromNode(parameter_info.NameLeaf, parameter_info.Name)

        parameter_names.add(parameter_info.Name)

        # Check for valid defaults
        if parameter_info.DefaultValue:
            encountered_default = True
        elif encountered_default:
            raise NonDefaultParameterAfterDefaultValueParameterError.FromNode(
                parameter_info.NameLeaf,
            )

    return parameters


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractNewStyleParameters(
    children: List[Node],
) -> Parameters:
    pos_parameters: List[ParameterInfo] = []
    any_parameters: List[ParameterInfo] = []
    key_parameters: List[ParameterInfo] = []

    for child in children:
        child = cast(Node, child)
        assert len(child.Children) == 3

        # Get the type
        the_type_node = cast(Node, child.Children[0])
        the_type = cast(Leaf, ExtractOrNode(the_type_node))

        if the_type.Type == CommonTokens.FunctionParameterPositional:
            parameters_list = pos_parameters
            has_order_error = any_parameters or key_parameters

        elif the_type.Type == CommonTokens.FunctionParameterAny:
            parameters_list = any_parameters
            has_order_error = bool(key_parameters)

        elif the_type.Type == CommonTokens.FunctionParameterKeyword:
            parameters_list = key_parameters
            has_order_error = False

        else:
            assert False, the_type  # pragma: no cover

        if parameters_list:
            regex_match = cast(Token.RegexMatch, the_type.Value).Match

            raise NewStyleParameterGroupDuplicateError.FromNode(
                the_type,
                regex_match.string[regex_match.start():regex_match.end()],
            )

        if has_order_error:
            raise NewStyleParameterGroupOrderingError.FromNode(the_type)

        # Get the parameters
        for parameter in GrammarDSL.ExtractDelimitedNodes(cast(Node, child.Children[2])):
            parameters_list.append(_ExtractParameterInfo(parameter))

    return Parameters(
        pos_parameters,
        any_parameters,
        key_parameters,
    )


# ----------------------------------------------------------------------
def _ExtractTraditionalParameters(
    node: Node,
) -> Parameters:
    # ----------------------------------------------------------------------
    class State(Enum):
        Any                                 = auto()
        Key                                 = auto()

    # ----------------------------------------------------------------------

    pos_parameters: List[ParameterInfo] = []
    any_parameters: List[ParameterInfo] = []
    key_parameters: List[ParameterInfo] = []

    encountered_pos_delimiter = False
    encountered_key_delimiter = False

    state = State.Any

    parameters = list(GrammarDSL.ExtractDelimitedNodes(node))

    for parameter_index, parameter in enumerate(parameters):
        parameter = cast(Node, ExtractOrNode(parameter))
        assert parameter.Type

        if parameter.Type == CommonTokens.FunctionParameterPositionalDelimiter:
            # This should never be the first token
            if (
                not pos_parameters
                and not any_parameters
                and not key_parameters
            ):
                raise TraditionalPositionalDelimiterError.FromNode(parameter)

            # We shouldn't see this if we have already seen a keyword delimiter
            if encountered_key_delimiter:
                raise TraditionalDelimiterOrderError.FromNode(parameter)

            # We shouldn't see this delimiter more than once
            if encountered_pos_delimiter:
                raise TraditionalDuplicatePositionalDelimiterError.FromNode(parameter)

            assert not pos_parameters
            pos_parameters = any_parameters
            any_parameters = []

            encountered_pos_delimiter = True

        elif parameter.Type == CommonTokens.FunctionParameterKeywordDelimiter:
            # We shouldn't see this delimiter as the last parameter
            if parameter_index + 1 == len(parameters):
                raise TraditionalKeywordDelimiterError.FromNode(parameter)

            # We shouldn't see this delimiter more than once
            if encountered_key_delimiter:
                raise TraditionalDuplicateKeywordDelimiterError.FromNode(parameter)

            encountered_key_delimiter = True
            state = State.Key

        elif parameter.Type.Name == "Parameter":
            parameter_info = _ExtractParameterInfo(parameter)

            if state == State.Any:
                any_parameters.append(parameter_info)
            elif state == State.Key:
                key_parameters.append(parameter_info)
            else:
                assert False, state  # pragma: no cover

        else:
            assert False, parameter  # pragma: no cover

    return Parameters(
        pos_parameters,
        any_parameters,
        key_parameters,
    )


# ----------------------------------------------------------------------
def _ExtractParameterInfo(
    node: Node,
) -> ParameterInfo:

    child_index = 0

    # <type>
    assert len(node.Children) >= child_index + 1
    the_type = ExtractDynamicExpressionNode(cast(Node, node.Children[child_index]))
    child_index += 1

    # arity?
    potential_arity_node = ExtractOptionalNode(node, child_index, "Arity")
    if potential_arity_node is not None:
        raise Exception("TODO")
        arity = "TODO"
        child_index += 1
    else:
        arity = None

    # <name>
    assert len(node.Children) >= child_index + 1
    name_leaf = cast(Leaf, node.Children[child_index])
    name = cast(str, ExtractLeafValue(name_leaf))
    child_index += 1

    if not NamingConventions.Parameter.Regex.match(name):
        raise NamingConventions.InvalidParameterNameError.FromNode(name_leaf, name)

    # ('=' <expr>)?
    potential_default_node = ExtractOptionalNode(node, child_index, "With Default")
    if potential_default_node is not None:
        child_index += 1

        default_node = cast(Node, potential_default_node)

        assert len(default_node.Children) == 2
        default = ExtractDynamicExpressionNode(cast(Node, default_node.Children[1]))
    else:
        default = None

    assert len(node.Children) == child_index

    return ParameterInfo(
        node,
        the_type,
        name_leaf,
        name,
        default,
        arity == "*",
    )