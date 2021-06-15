# ----------------------------------------------------------------------
# |
# |  FuncDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 12:21:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDeclarationStatement object"""

import itertools
import os

from enum import auto, Enum
from typing import List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from .Common import Statements as CommonStatements

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Leaf,
        Node,
        Statement,
        ValidationError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PositionalParameterAfterDefaultValueParameterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Positional parameters may not appear after a parameter with a default value has been defined")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidNewStyleParameterGroupOrderingError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Parameter groups must appear in the order {}".format(", ".join(token.Name for token in CommonTokens.AllNewStyleParameters)))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTraditionalDelimiterOrderError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) must appear before the keyword delimiter ({})".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTraditionalPositionalDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) must appear after at least 1 parameter".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTraditionalKeywordDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ({}) must appear before at least 1 parameter".format(
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTraditionalDuplicatePositionalDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ({}) may only appear once in a list of parameters".format(
            CommonTokens.FunctionParameterPositionalDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTraditionalDuplicateKeywordDelimiterError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ({}) may only appear once in a list of parameters".format(
            CommonTokens.FunctionParameterKeywordDelimiter.Name,
        ),
    )


# ----------------------------------------------------------------------
class FuncDeclarationStatement(GrammarStatement):
    """\
    Declares a function.

    <type> <name> '(' <args> ')' ':'
        <dynamic_statements>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        parameter_statement = Statement(
            "Parameter",
            CommonStatements.Type,
            [
                # <name> = <rhs>
                Statement(
                    "With Default",
                    CommonTokens.Name,
                    CommonTokens.Equal,
                    DynamicStatements.Expressions,
                ),

                # <name>
                CommonTokens.Name,
            ],
        )

        traditional_parameter_statement = [
            parameter_statement,
            CommonTokens.FunctionParameterPositionalDelimiter,
            CommonTokens.FunctionParameterKeywordDelimiter,
        ]

        super(FuncDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement(
                "Function Declaration",
                CommonStatements.Type,
                CommonTokens.Name,
                CommonTokens.LParen,
                CommonTokens.PushIgnoreWhitespaceControl,

                # Parameters are optional
                (
                    [
                        # New Style:
                        #
                        #       <type> Func(
                        #           pos: <type> a, <type> b, <type> c,
                        #           any: <type> d, <type> e=100
                        #           key: <type> f=200, <type> g=300
                        #       ):
                        #           <statements>
                        #
                        (
                            Statement(
                                "New Style",
                                CommonTokens.AllNewStyleParameters,
                                CommonTokens.Colon,
                                parameter_statement,
                                (
                                    Statement(
                                        "Comma and Parameter",
                                        CommonTokens.Comma,
                                        parameter_statement,
                                    ),
                                    0,
                                    None,
                                ),
                                (CommonTokens.Comma, 0, 1),
                            ),
                            1,
                            len(CommonTokens.AllNewStyleParameters),
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
                        Statement(
                            "Traditional",
                            traditional_parameter_statement,
                            (
                                Statement(
                                    "Comma and Parameter",
                                    CommonTokens.Comma,
                                    traditional_parameter_statement,
                                ),
                                0,
                                None,
                            ),
                            (CommonTokens.Comma, 0, 1),
                        ),
                    ],
                    0,
                    1,
                ),

                CommonTokens.PopIgnoreWhitespaceControl,
                CommonTokens.RParen,
                CommonTokens.Colon,
                CommonTokens.NewlineToken(),

                CommonTokens.Indent,
                (DynamicStatements.Statements, 1, None),
                CommonTokens.Dedent,
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        assert len(node.Children) > 4
        node.parameters = cls._GetParameters(node.Children[3])

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _ParameterInfo(object):
        Parameter: Node
        Type: str
        TypeModifier: CommonTokens.RegexToken
        Name: str
        DefaultValue: Optional[Node]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _Parameters(object):
        Positional: List["FuncDeclarationStatement._ParameterInfo"]
        PositionalOrKeyword: List["FuncDeclarationStatement._ParameterInfo"]
        Keyword: List["FuncDeclarationStatement._ParameterInfo"]

    # ----------------------------------------------------------------------
    @classmethod
    def _GetParameters(
        cls,
        node: Union[Node, Leaf],
    ) -> "FuncDeclarationStatement._Parameters":

        if isinstance(node, Leaf):
            # The leaf is the closing ')' token; this indicates that there aren't any
            # parameters
            return cls._Parameters([], [], [])

        # Drill into the Optional statement
        assert isinstance(node.Type, tuple)
        assert len(node.Children) == 1
        node = node.Children[0]

        # Drill into the Or statement
        assert isinstance(node.Type, list)
        assert len(node.Children) == 1
        node = node.Children[0]

        # Arrive at the content node
        if isinstance(node.Type, tuple):
            result = cls._GetNewStyleParameters(node)
        elif node.Type.Name == "Traditional":
            result = cls._GetTraditionalParameters(node)
        else:
            assert False, node  # pragma: no cover

        # Ensure that all parameters after the first with a default value
        # also have a default value.
        encountered_default = False

        for parameter_info in itertools.chain(
            result.Positional,
            result.PositionalOrKeyword,
            result.Keyword,
        ):
            if parameter_info.DefaultValue:
                encountered_default = True
            elif encountered_default:
                raise PositionalParameterAfterDefaultValueParameterError.FromNode(
                    parameter_info.Parameter,
                )

        return result

    # ----------------------------------------------------------------------
    @classmethod
    def _GetTraditionalParameters(
        cls,
        node: Node,
    ) -> "FuncDeclarationStatement._Parameters":

        positional_parameters: List["_ParameterInfo"] = []
        positional_or_keyword_parameters: List["_ParameterInfo"] = []
        keyword_parameters: List["_ParameterInfo"] = []

        encountered_positional_delimiter = False
        encountered_keyword_delimiter = False

        # ----------------------------------------------------------------------
        class State(Enum):
            PositionalOrKeyword     = auto()
            Keyword                 = auto()

        # ----------------------------------------------------------------------

        state = State.PositionalOrKeyword

        # ----------------------------------------------------------------------
        def ProcessParameter(
            parameter: Union[Statement, CommonTokens.RegexToken],
            is_last_parameter: bool,
        ):
            nonlocal positional_parameters
            nonlocal positional_or_keyword_parameters
            nonlocal keyword_parameters

            nonlocal encountered_positional_delimiter
            nonlocal encountered_keyword_delimiter

            nonlocal state

            if parameter.Type == CommonTokens.FunctionParameterPositionalDelimiter:
                # We shouldn't see this as the first parameter
                if (
                    not positional_parameters
                    and not positional_or_keyword_parameters
                    and not keyword_parameters
                ):
                    raise InvalidTraditionalPositionalDelimiterError.FromNode(parameter)

                # We shouldn't see this if we have already seen a keyword delimiter
                if encountered_keyword_delimiter:
                    raise InvalidTraditionalDelimiterOrderError.FromNode(parameter)

                # We shouldn't see this delimiter more than once
                if encountered_positional_delimiter:
                    raise InvalidTraditionalDuplicatePositionalDelimiterError.FromNode(parameter)

                assert not positional_parameters
                positional_parameters = positional_or_keyword_parameters
                positional_or_keyword_parameters = []

                encountered_positional_delimiter = True

            elif parameter.Type == CommonTokens.FunctionParameterKeywordDelimiter:
                # We shouldn't see this delimiter as the last parameter
                if is_last_parameter:
                    raise InvalidTraditionalKeywordDelimiterError.FromNode(parameter)

                # We shouldn't see this delimiter more than once
                if encountered_keyword_delimiter:
                    raise InvalidTraditionalDuplicateKeywordDelimiterError.FromNode(parameter)

                encountered_keyword_delimiter = True
                state = State.Keyword

            elif parameter.Type.Name == "Parameter":
                parameter_info = cls._CreateParameterInfo(parameter)

                if state == State.PositionalOrKeyword:
                    positional_or_keyword_parameters.append(parameter_info)
                elif state == State.Keyword:
                    keyword_parameters.append(parameter_info)
                else:
                    assert False, state  # pragma: no cover

            else:
                assert False, parameter  # pragma: no cover

        # ----------------------------------------------------------------------

        has_comma_delimited_parameters = (
            len(node.Children) > 1
            and isinstance(node.Children[1].Type, tuple)
            and isinstance(node.Children[1].Type[0], Statement)
        )

        # Initial parameter
        assert len(node.Children[0].Children) == 1

        ProcessParameter(
            node.Children[0].Children[0],
            is_last_parameter=not has_comma_delimited_parameters,
        )

        # Following parameters
        if has_comma_delimited_parameters:
            node = node.Children[1]

            for child_index, child in enumerate(node.Children):
                # First value is the comma, second value is the parameter
                assert len(child.Children) == 2
                child = child.Children[1]

                # Drill into the Or statement
                assert isinstance(child.Type, list)
                assert len(child.Children) == 1
                child = child.Children[0]

                ProcessParameter(
                    child,
                    is_last_parameter=child_index + 1 == len(node.Children),
                )

        return cls._Parameters(
            positional_parameters,
            positional_or_keyword_parameters,
            keyword_parameters,
        )

    # ----------------------------------------------------------------------
    @classmethod
    def _GetNewStyleParameters(
        cls,
        node: Node,
    ) -> "FuncDeclarationStatement._Parameters":

        positional_parameters: List["_ParameterInfo"] = []
        positional_or_keyword_parameters: List["_ParameterInfo"] = []
        keyword_parameters: List["_ParameterInfo"] = []

        for child in node.Children:
            # Get the type
            the_type = child.Children[0]

            # Drill into the Or statement
            assert isinstance(the_type.Type, list)
            assert len(the_type.Children) == 1
            the_type = the_type.Children[0]

            # Set the result list and check for errors
            if the_type.Type == CommonTokens.FunctionParameterPositional:
                parameters_list = positional_parameters
                has_error = positional_or_keyword_parameters or keyword_parameters
            elif the_type.Type == CommonTokens.FunctionParameterAny:
                parameters_list = positional_or_keyword_parameters
                has_error = bool(keyword_parameters)
            elif the_type.Type == CommonTokens.FunctionParameterKeyword:
                parameters_list = keyword_parameters
                has_error = False
            else:
                assert False, the_type  # pragma: no cover

            if has_error:
                raise InvalidNewStyleParameterGroupOrderingError.FromNode(the_type)

            # Get the parameters
            parameters_list.append(cls._CreateParameterInfo(child.Children[2]))

            if (
                len(child.Children) > 4
                and isinstance(child.Children[3].Type, tuple)
                and isinstance(child.Children[3].Type[0], Statement)
            ):
                parameter_nodes = child.Children[3]

                for parameter_node in parameter_nodes.Children:
                    # First value is the comma, second is the parameter
                    assert len(parameter_node.Children) == 2
                    parameter_node = parameter_node.Children[1]

                    parameters_list.append(cls._CreateParameterInfo(parameter_node))

        return cls._Parameters(
            positional_parameters,
            positional_or_keyword_parameters,
            keyword_parameters,
        )

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateParameterInfo(
        cls,
        node: Node,
    ) -> "FuncDeclarationStatement._ParameterInfo":
        assert len(node.Children) == 2

        type_info = CommonStatements.TypeInfo.FromNode(node.Children[0])

        # Drill into the Parameter statement
        node = node.Children[1]

        # Drill into the Or statement
        assert isinstance(node.Type, list)
        assert len(node.Children) == 1
        node = node.Children[0]

        if isinstance(node, Leaf):
            # Name
            name_node = node
            default_value = None
        else:
            # Name with default
            assert len(node.Children) == 3

            name_node = node.Children[0]
            default_value = CommonStatements.ExtractDynamicExpressionsNode(node.Children[2])

        return cls._ParameterInfo(
            node,
            type_info.Name,
            type_info.Modifier,
            name_node.Value.Match.group("value"),
            default_value,
        )
