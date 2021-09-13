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
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarError import GrammarError
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
class TraditionalParameterType(object):
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
            TraditionalParameterType.Positional,
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicatePositionalError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterType.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicateKeywordError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterPositionalError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') must appear after at least 1 parameter.".format(
            TraditionalParameterType.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterKeywordError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') must appear before at least 1 parameter.".format(
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RequiredParameterAfterDefaultError(GrammarError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "A required parameter may not appear after a parameter with a default value.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Parameter(YamlRepr.ObjectReprImplBase):
    Type: Union[Leaf, Node]
    IsVarArgs: bool
    Name: Union[Leaf, Node]
    Default: Optional[Union[Leaf, Node]]


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
            DynamicPhrasesType.Names,

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
                                TraditionalParameterType.Positional,
                                TraditionalParameterType.Keyword,
                            ),

                            # (',' (<parameter_item>|'/','*'))*
                            PhraseItem(
                                name="Comma and Parameter",
                                item=[
                                    ",",
                                    (
                                        parameter_item,
                                        TraditionalParameterType.Positional,
                                        TraditionalParameterType.Keyword,
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
def Extract(
    node: Node,
) -> Dict[ParametersType, List[Parameter]]:

    # TODO: Revisit this

    # Drill into the parameters node
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    parameters_dict = {}

    if nodes[2] is not None:
        node = cast(
            Node,
            ExtractOr(
                cast(
                    Node,
                    ExtractOptional(cast(Node, nodes[2])),
                ),
            ),
        )

        assert node.Type

        if node.Type.Name == "Traditional":
            enum_method = _EnumTraditional
        else:
            enum_method = _EnumNewStyle

        # Create the info
        encountered_default = False

        for parameters_type, parameter_nodes in enum_method(node):
            parameters = []

            for parameter_node in parameter_nodes:
                parameter_nodes = ExtractSequence(parameter_node)
                assert len(parameter_nodes) == 4

                parameter_type = ExtractDynamic(cast(Node, parameter_nodes[0]))
                is_var_args = bool(parameter_nodes[1])
                parameter_name = ExtractDynamic(cast(Node, parameter_nodes[2]))

                default_node = cast(Optional[Node], parameter_nodes[3])

                if default_node is not None:
                    encountered_default = True


                    default_nodes = ExtractSequence(cast(Node, ExtractOptional(default_node)))
                    assert len(default_nodes) == 2

                    default_node = ExtractDynamic(cast(Node, default_nodes[1]))

                elif encountered_default:
                    raise RequiredParameterAfterDefaultError.FromNode(parameter_node)

                parameters.append(
                    Parameter(parameter_type, is_var_args, parameter_name, default_node),
                )

            assert parameters
            assert parameters_type not in parameters_dict, parameters_dict
            parameters_dict[parameters_type] = parameters

    return parameters_dict


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnumTraditional(
    node: Node,
) -> Generator[
    Tuple[ParametersType, List[Node]],
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

        if name == TraditionalParameterType.Positional:
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

            yield ParametersType.pos, parameters
            parameters = []

        elif name == TraditionalParameterType.Keyword:
            # We shouldn't see this more than once
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterDuplicateKeywordError.FromNode(parameter_node)

            keyword_parameter_index = parameter_node_index

            if parameters:
                yield ParametersType.any, parameters
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

        yield parameters_type, parameters


# ----------------------------------------------------------------------
def _EnumNewStyle(
    node: Node,
) -> Generator[
    Tuple[ParametersType, List[Node]],
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

        yield parameters_type, cast(List[Node], parameters)
