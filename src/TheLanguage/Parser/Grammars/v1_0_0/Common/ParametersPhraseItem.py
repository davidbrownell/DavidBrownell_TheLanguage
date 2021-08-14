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
    from ...GrammarPhrase import ValidationError
    from ....Phrases.DSL import (
        DynamicPhrasesType,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )

# TODO: Validate no args with defaults after any with default

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
        node: Union[Node, Tuple[str, Leaf]],
    ) -> "ParametersType":
        if isinstance(node, tuple):
            name, leaf = node
        else:
            name = ExtractToken(
                node,  # type: ignore
                use_match=True,
            )

            leaf = node

        try:
            return cls[name]  # type: ignore
        except KeyError:
            assert False, (name, leaf)


# ----------------------------------------------------------------------
class TraditionalParameterType(object):
    Positional                              = "/"
    Keyword                                 = "*"


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NewStyleParameterGroupDuplicateError(ValidationError):
    GroupName: str

    MessageTemplate                         = Interface.DerivedProperty("The parameter group '{GroupName}' has already been specified.")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterOrderError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ('{}') must appear before the keyword delimiter ('{}').".format(
            TraditionalParameterType.Positional,
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicatePositionalError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterType.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicateKeywordError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterPositionalError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The positional delimiter ('{}') must appear after at least 1 parameter.".format(
            TraditionalParameterType.Positional,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterKeywordError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty(
        "The keyword delimiter ('{}') must appear before at least 1 parameter.".format(
            TraditionalParameterType.Keyword,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NodeInfo(CommonEnvironment.ObjectReprImplBase):
    Parameters: Dict[ParametersType, List[Node]]


# ----------------------------------------------------------------------
def Create():
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
                        arity=(1, len(ParametersType.CreatePhraseItem())),
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
def Validate(
    node: Node,
):
    # Drill into the parameters node
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    parameters_dict = {}

    if nodes[2] is not None:
        node = cast(Node, nodes[2])

        # Drill into the or node
        node = cast(Node, ExtractOr(node))
        assert node.Type

        if node.Type.Name == "Traditional":
            enum_method = _EnumTraditional
        else:
            enum_method = _EnumNewStyle

        # Create the info
        for parameters_type, parameters in enum_method(node):
            assert parameters_type not in parameters_dict, parameters_dict
            parameters_dict[parameters_type] = parameters

    # Commit the info
    object.__setattr__(node, "Info", NodeInfo(parameters_dict))


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

    for node_index, node in enumerate(  # type: ignore
        itertools.chain(
            [nodes[0]],
            [ExtractOr(node.Children[1]) for node in nodes[1]],  # type: ignore
        ),
    ):
        if isinstance(node, Node):
            parameters.append(node)
            continue

        assert isinstance(node, Leaf)

        name = ExtractToken(
            node,  # type: ignore
            use_match=True,
        )

        if name == TraditionalParameterType.Positional:
            # This should never be the first parameter
            if node_index == 0:
                raise TraditionalDelimiterPositionalError.FromNode(node)

            # We shouldn't see this more than once
            if encountered_positional_parameter:
                raise TraditionalDelimiterDuplicatePositionalError.FromNode(node)

            # We shouldn't see this after a keyword parameter
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterOrderError.FromNode(node)

            encountered_positional_parameter = True

            assert parameters

            yield ParametersType.pos, parameters
            parameters = []

        elif name == TraditionalParameterType.Keyword:
            # We shouldn't see this more than once
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterDuplicateKeywordError.FromNode(node)

            keyword_parameter_index = node_index

            if parameters:
                yield ParametersType.any, parameters
                parameters = []

        else:
            assert False, name # pragma: no cover

    # The keyword delimiter should never be the last parameter
    if keyword_parameter_index == node_index:  # type: ignore
        raise TraditionalDelimiterKeywordError.FromNode(node)

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

    for node in ExtractRepeat(node):  # type: ignore
        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # Get the parameter type
        parameters_type = ParametersType.Extract(nodes[0])  # type: ignore

        if parameters_type in encountered:
            raise NewStyleParameterGroupDuplicateError.FromNode(nodes[0], parameters_type.name)  # type: ignore

        encountered.add(parameters_type)

        # Get the parameters
        parameters = list(
            itertools.chain(
                [
                    [nodes[2]],
                    [node.Children[1] for node in nodes[3]],  # type: ignore
                ],
            ),
        )

        yield parameters_type, parameters  # type: ignore
