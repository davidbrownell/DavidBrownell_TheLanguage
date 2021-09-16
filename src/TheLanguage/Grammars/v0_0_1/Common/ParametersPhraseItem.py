# ----------------------------------------------------------------------
# |
# |  ParametersPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 21:12:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing parameters (such as functions and methods)"""

import itertools
import os

from enum import auto, Enum
from typing import cast, Dict, Generator, List, Optional, Tuple, Union

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

    from ...GrammarError import GrammarError
    from ...GrammarPhrase import CreateLexerRegions

    from ....Lexer.Common.ParametersLexerInfo import (
        ExpressionLexerInfo,
        ParameterLexerInfo,
        ParametersLexerInfo,
        TypeLexerInfo,
    )

    from ....Lexer.LexerInfo import GetLexerInfo

    from ....Parser.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
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
class ParametersType(Enum):
    pos                                     = auto()
    any                                     = auto()
    key                                     = auto()

    # ----------------------------------------------------------------------
    @classmethod
    def CreatePhraseItem(cls):
        return tuple(value.name for value in cls)

    # ----------------------------------------------------------------------
    @classmethod
    def Extract(
        cls,
        node: Node,
    ) -> "ParametersType":
        leaf = cast(Leaf, ExtractOr(node))

        name = cast(
            str,
            ExtractToken(
                leaf,
                use_match=True,
            ),
        )

        try:
            return cls[name]
        except KeyError:
            assert False, (name, leaf)


# ----------------------------------------------------------------------
class TraditionalParameterDelimiter(object):
    Positional                              = "/"
    Keyword                                 = "*"


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NewStyleParameterGroupDuplicateError(GrammarError):
    GroupName: str

    MessageTemplate                         = Interface.DerivedProperty("The parameter group '{GroupName}' has already been specified.")  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterOrderError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') must appear before the keyword delimiter ('{}').".format(
            TraditionalParameterDelimiter.Positional,
            TraditionalParameterDelimiter.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicatePositionalError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterDelimiter.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicateKeywordError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterDelimiter.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterPositionalError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') must appear after at least 1 parameter.".format(
            TraditionalParameterDelimiter.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterKeywordError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') must appear before at least 1 parameter.".format(
            TraditionalParameterDelimiter.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RequiredParameterAfterDefaultError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "A required parameter may not appear after a parameter with a default value.",
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    """\
    '(' <parameters>? ')'
    """

    # <type> '*'? <name> ('=' <expr>)?
    parameter_item = PhraseItem(
        name="Parameter",
        item=[
            # <type>
            DynamicPhrasesType.Types,

            # '*'?
            PhraseItem(
                name="Var Args",
                item="*",
                arity="?",
            ),

            # <name>
            CommonTokens.GenericName,

            # ('=' <expr>)?
            PhraseItem(
                name="With Default",
                item=[
                    "=",
                    DynamicPhrasesType.Expressions,
                ],
                arity="?",
            ),
        ],
    )

    return PhraseItem(
        name="Parameters",
        item=[
            # '('
            "(",
            CommonTokens.PushIgnoreWhitespaceControl,

            # <parameters>?
            PhraseItem(
                item=(
                    # New Style:
                    #
                    #       ...(
                    #               ('pos' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #               ('any' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #               ('key' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #       )
                    #
                    PhraseItem(
                        name="New Style",
                        item=[
                            ParametersType.CreatePhraseItem(),
                            ":",

                            # <parameter_item>
                            parameter_item,

                            # (',' <parameter_item>)*
                            PhraseItem(
                                name="Comma and Parameter",
                                item=[
                                    ",",
                                    parameter_item,
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
                        arity="+",
                    ),

                    # Traditional:
                    #
                    #       ...(
                    #               (<parameter_item>|'/','*') (',' (<parameter_item>|'/','*'))* ','?
                    #       )
                    #
                    #       Everything before '/' must be a positional argument
                    #       Everything after '/' and before '*' can either be a positional or keyword argument (this is the default)
                    #       Everything after '*' must be a keyword argument
                    #
                    PhraseItem(
                        name="Traditional",
                        item=[
                            # <parameter_item>|'/'|'*'
                            (
                                parameter_item,
                                TraditionalParameterDelimiter.Positional,
                                TraditionalParameterDelimiter.Keyword,
                            ),

                            # (',' (<parameter_item>|'/','*'))*
                            PhraseItem(
                                name="Comma and Parameter",
                                item=[
                                    ",",
                                    (
                                        parameter_item,
                                        TraditionalParameterDelimiter.Positional,
                                        TraditionalParameterDelimiter.Keyword,
                                    ),
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
                    ),
                ),
                arity="?",
            ),

            # ')'
            CommonTokens.PopIgnoreWhitespaceControl,
            ")",
        ],
    )


# ----------------------------------------------------------------------
def ExtractLexerInfo(
    node: Node,
) -> Tuple[Optional[Node], Optional[ParametersLexerInfo]]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    # <parameters>
    all_parameters_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
    if all_parameters_node is None:
        return None, None

    all_parameters_node = cast(Node, ExtractOr(all_parameters_node))
    assert all_parameters_node.Type is not None

    if all_parameters_node.Type.Name == "Traditional":
        enum_method = _EnumTraditional
    else:
        enum_method = _EnumNewStyle

    encountered_default = False

    positional_parameters_node = None
    positional_parameters_info = None

    keyword_parameters_node = None
    keyword_parameters_info = None

    any_parameters_node = None
    any_parameters_info = None

    for parameters_type, parameters_node, parameter_nodes in enum_method(all_parameters_node):
        parameters = []

        for parameter_node in parameter_nodes:
            these_parameter_nodes = ExtractSequence(parameter_node)
            assert len(these_parameter_nodes) == 4

            # <type>
            parameter_type_node = cast(Node, ExtractDynamic(cast(Node, these_parameter_nodes[0])))
            parameter_type_info = cast(TypeLexerInfo, GetLexerInfo(parameter_type_node))

            # '*'?
            is_var_args_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], these_parameter_nodes[1])))

            if is_var_args_node is not None:
                is_var_args_info = True
            else:
                is_var_args_info = None

            # <name>
            name_leaf = cast(Leaf, these_parameter_nodes[2])
            name_info = cast(str, ExtractToken(name_leaf))

            # ('=' <expr>)?
            default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], these_parameter_nodes[3])))

            if default_node is not None:
                encountered_default = True

                default_nodes = ExtractSequence(default_node)
                assert len(default_nodes) == 2

                default_info = cast(ExpressionLexerInfo, GetLexerInfo(ExtractDynamic(cast(Node, default_nodes[1]))))
            else:
                if encountered_default:
                    raise RequiredParameterAfterDefaultError.FromNode(parameter_node)

                default_info = None

            parameters.append(
                # pylint: disable=too-many-function-args
                ParameterLexerInfo(
                    CreateLexerRegions(
                        parameter_node,
                        parameter_type_node,
                        name_leaf,
                        default_node,
                        is_var_args_node,
                    ),  # type: ignore
                    parameter_type_info,
                    name_info,
                    default_info,
                    is_var_args_info,
                ),
            )

        if parameters_type == ParametersType.pos:
            assert positional_parameters_node is None
            assert positional_parameters_info is None

            positional_parameters_node = parameters_node
            positional_parameters_info = parameters

        elif parameters_type == ParametersType.key:
            assert keyword_parameters_node is None
            assert keyword_parameters_info is None

            keyword_parameters_node = parameters_node
            keyword_parameters_info = parameters

        elif parameters_type == ParametersType.any:
            assert any_parameters_node is None
            assert any_parameters_info is None

            any_parameters_node = parameters_node
            any_parameters_info = parameters

        else:
            assert False, parameters_type

    return (
        node,
        # pylint: disable=too-many-function-args
        ParametersLexerInfo(
            CreateLexerRegions(
                all_parameters_node,
                positional_parameters_node,
                keyword_parameters_node,
                any_parameters_node,
            ),  # type: ignore
            positional_parameters_info,
            keyword_parameters_info,
            any_parameters_info,
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnumTraditional(
    node: Node,
) -> Generator[
    Tuple[ParametersType, Node, List[Node]],
    None,
    None,
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    encountered_positional_parameter = False
    keyword_parameter_index: Optional[int] = None

    parameters = []

    for parameter_node_index, parameter_node in enumerate(
        itertools.chain(
            [nodes[0]],
            [
                ExtractSequence(node)[1] for node in cast(
                    List[Node],
                    ExtractRepeat(cast(Node, nodes[1])),
                )
            ],
        ),
    ):
        # Drill into the or node
        parameter_node = cast(Node, ExtractOr(cast(Node, parameter_node)))

        if isinstance(parameter_node, Node):
            parameters.append(parameter_node)
            continue

        assert isinstance(parameter_node, Leaf)

        name = cast(
            str,
            ExtractToken(
                parameter_node,
                use_match=True,
            ),
        )

        if name == TraditionalParameterDelimiter.Positional:
            # This should never be the first parameter
            if parameter_node_index == 0:
                raise TraditionalDelimiterPositionalError.FromNode(parameter_node)

            # We shouldn't see this more than once
            if encountered_positional_parameter:
                raise TraditionalDelimiterDuplicatePositionalError.FromNode(parameter_node)

            # We shouldn't see this after a keyword parameter
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterOrderError.FromNode(parameter_node)

            encountered_positional_parameter = True

            assert parameters

            yield ParametersType.pos, node, parameters
            parameters = []

        elif name == TraditionalParameterDelimiter.Keyword:
            # We shouldn't see this more than once
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterDuplicateKeywordError.FromNode(parameter_node)

            keyword_parameter_index = parameter_node_index

            if parameters:
                yield ParametersType.any, node, parameters
                parameters = []

        else:
            assert False, name # pragma: no cover

    # The keyword delimiter should never be the last parameter
    if keyword_parameter_index == parameter_node_index:  # type: ignore
        raise TraditionalDelimiterKeywordError.FromNode(parameter_node)  # type: ignore

    if parameters:
        if keyword_parameter_index is not None:
            parameters_type = ParametersType.key
        else:
            parameters_type = ParametersType.any

        yield parameters_type, node, parameters


# ----------------------------------------------------------------------
def _EnumNewStyle(
    node: Node,
) -> Generator[
    Tuple[ParametersType, Node, List[Node]],
    None,
    None,
]:
    encountered = set()

    for node in cast(List[Node], ExtractRepeat(node)):
        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # Get the parameter type
        parameters_type = ParametersType.Extract(cast(Node, nodes[0]))

        if parameters_type in encountered:
            raise NewStyleParameterGroupDuplicateError.FromNode(cast(Node, nodes[0]), parameters_type.name)

        encountered.add(parameters_type)

        # Get the parameters
        parameters = list(
            itertools.chain(
                [nodes[2]],
                [ExtractSequence(node)[1] for node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[3])))],
            ),
        )

        yield parameters_type, node, cast(List[Node], parameters)
