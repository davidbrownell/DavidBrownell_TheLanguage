# ----------------------------------------------------------------------
# |
# |  ParametersPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 12:07:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality when parsing parameters"""

import itertools
import os

from enum import auto, Enum
from typing import Any, cast, Dict, Generator, List, Optional, Set, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from .Impl import ModifierImpl

    from ...Error import Error

    from ....Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Common.ParametersParserInfo import (
        ExpressionParserInfo,
        ParameterParserInfo,
        ParametersParserInfo,
        TypeParserInfo,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo


# ----------------------------------------------------------------------
class ParametersType(Enum):
    pos                                     = auto()
    any                                     = auto()
    key                                     = auto()

ParametersType.CreatePhraseItem             = staticmethod(ModifierImpl.StandardCreatePhraseItemFuncFactory(ParametersType))  # type: ignore
ParametersType.Extract                      = staticmethod(ModifierImpl.StandardExtractFuncFactory(ParametersType))  # type: ignore


# ----------------------------------------------------------------------
class TraditionalParameterDelimiter(Enum):
    Positional                              = "/"
    Keyword                                 = "*"


TraditionalParameterDelimiter.CreatePhraseItem          = staticmethod(ModifierImpl.ByValueCreatePhraseItemFuncFactory(TraditionalParameterDelimiter))  # type: ignore
TraditionalParameterDelimiter.Extract                   = staticmethod(ModifierImpl.ByValueExtractFuncFactory(TraditionalParameterDelimiter))  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NewStyleParameterGroupDuplicateError(Error):
    GroupName: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The parameter group '{GroupName}' has already been specified.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterOrderError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') must appear before the keyword delimiter ('{}').".format(
            TraditionalParameterDelimiter.Positional.value,
            TraditionalParameterDelimiter.Keyword.value,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicatePositionalError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterDelimiter.Positional.value,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterDuplicateKeywordError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') may only appear once in a list of parameters.".format(
            TraditionalParameterDelimiter.Keyword.value,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterPositionalError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The positional delimiter ('{}') must appear after at least 1 parameter.".format(
            TraditionalParameterDelimiter.Positional.value,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TraditionalDelimiterKeywordError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The keyword delimiter ('{}') must appear before at least 1 parameter.".format(
            TraditionalParameterDelimiter.Keyword.value,
        ),
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RequiredParameterAfterDefaultError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "A required parameter may not appear after a parameter with a default value.",
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    """\
    '(' <<parameters>>? ')'
    """

    # <type> '*'? <name> ('=' <expression>)?
    parameter_item = PhraseItem.Create(
        name="Parameter",
        item=[
            # <type>
            DynamicPhrasesType.Types,

            # '*'?
            OptionalPhraseItem.Create(
                name="Variable Parameter",
                item="*",
            ),

            # <name>
            CommonTokens.ParameterName,

            # ('=' <expression>)?
            OptionalPhraseItem.Create(
                name="With Default",
                item=[
                    "=",
                    DynamicPhrasesType.Expressions,
                ],
            ),
        ],
    )

    traditional_parameter_item = (parameter_item, ) + TraditionalParameterDelimiter.CreatePhraseItem()  # type: ignore

    return PhraseItem.Create(
        name="Parameters",
        item=[
            # '('
            "(",
            CommonTokens.PushIgnoreWhitespaceControl,

            # <<parameters>>?
            OptionalPhraseItem.Create(
                item=(
                    # New Style:
                    #
                    #   ... '('
                    #           ('pos' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #           ('any' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #           ('key' ':' <parameter_item> (',' <parameter_item>)* ','?)?
                    #       ')'
                    #
                    OneOrMorePhraseItem.Create(
                        name="New Style",
                        item=[
                            # <parameters_type> ':'
                            ParametersType.CreatePhraseItem(),  # type: ignore
                            ":",

                            # <parameter_item>
                            parameter_item,

                            # (',' <parameter_item>)*
                            ZeroOrMorePhraseItem.Create(
                                name="Comma and Parameter",
                                item=[
                                    ",",
                                    parameter_item,
                                ],
                            ),

                            # ','?
                            OptionalPhraseItem.Create(
                                name="Trailing Comma",
                                item=",",
                            ),
                        ],
                    ),

                    # Traditional:
                    #
                    #   ... '('
                    #           (<parameter_item>|'/'|'*') (',' (<parameter_item>|'/'|'*'))* ','?
                    #       ')'
                    #
                    PhraseItem.Create(
                        name="Traditional",
                        item=[
                            # (<parameter_item> | '/' | '*')
                            traditional_parameter_item,

                            # (',' (<parameter_item> | '/' | '*'))*
                            ZeroOrMorePhraseItem.Create(
                                name="Common and Parameter",
                                item=[
                                    ",",
                                    traditional_parameter_item,
                                ],
                            ),

                            OptionalPhraseItem.Create(
                                name="Trailing Comma",
                                item=",",
                            ),
                        ],
                    ),
                ),
            ),

            # ')'
            CommonTokens.PopIgnoreWhitespaceControl,
            ")",
        ],
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> Union[bool, ParametersParserInfo]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    all_parameters_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
    if all_parameters_node is None:
        # We don't want to return None here, as there aren't any parameters, but parameter information
        # (e.g. '(' and ')') was found). Return a non-null value so that the caller can associate a
        # node with the result.
        return False

    all_parameters_node = cast(Node, ExtractOr(all_parameters_node))
    assert all_parameters_node.Type is not None

    if all_parameters_node.Type.Name == "Traditional":
        enum_func = _EnumTraditional
    else:
        enum_func = _EnumNewStyle

    encountered_default = False
    parameters_infos: Dict[ParametersType, Tuple[Node, List[ParameterParserInfo]]] = {}

    for parameters_type, parameters_node, parameter_nodes in enum_func(all_parameters_node):
        parameters: List[ParameterParserInfo] = []

        for parameter_node in parameter_nodes:
            these_parameter_nodes = ExtractSequence(parameter_node)
            assert len(these_parameter_nodes) == 4

            # <type>
            type_node = cast(Node, ExtractDynamic(cast(Node, these_parameter_nodes[0])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            # '*'?
            is_var_args_node = cast(
                Optional[Node],
                ExtractOptional(cast(Optional[Node], these_parameter_nodes[1])),
            )
            is_var_args_info = None if is_var_args_node is None else True

            # <name>
            name_leaf = cast(Leaf, these_parameter_nodes[2])
            name_info = cast(str, ExtractToken(name_leaf))

            # ('=' <expression>)?
            default_node = cast(
                Optional[Node],
                ExtractOptional(cast(Optional[Node], these_parameter_nodes[3])),
            )

            if default_node is None:
                if encountered_default:
                    raise RequiredParameterAfterDefaultError.FromNode(parameter_node)

                default_info = None
            else:
                encountered_default = True

                default_nodes = ExtractSequence(default_node)
                assert len(default_nodes) == 2

                default_node = ExtractDynamic(cast(Node, default_nodes[1]))
                default_info = cast(ExpressionParserInfo, GetParserInfo(default_node))

            parameters.append(
                # pylint: disable=too-many-function-args
                ParameterParserInfo(
                    CreateParserRegions(parameter_node, type_node, name_leaf, default_node, is_var_args_node),  # type: ignore
                    type_info,
                    name_info,
                    default_info,
                    is_var_args_info,
                ),
            )

        assert parameters

        assert parameters_type not in parameters_infos, parameters_type
        parameters_infos[parameters_type] = (parameters_node, parameters)

    # Extract information from parameters_infos to create a dict used in invoke ParametersParserInfo
    parser_regions_args: List[Any] = [node]
    parser_info_args: List[Any] = []

    for parameter_type in [
        ParametersType.pos,
        ParametersType.key,
        ParametersType.any,
    ]:
        parameter_info = parameters_infos.get(parameter_type, None)
        if parameter_info is None:
            parser_region_arg = None
            parser_info_arg = None
        else:
            parser_region_arg, parser_info_arg = parameter_info

        parser_regions_args.append(parser_region_arg)
        parser_info_args.append(parser_info_arg)

    parser_info_args.insert(
        0,
        CreateParserRegions(*parser_regions_args),  # type: ignore
    )

    return ParametersParserInfo(*parser_info_args)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnumNewStyle(
    node: Node,
) -> Generator[
    Tuple[ParametersType, Node, List[Node]],
    None,
    None,
]:
    encountered: Set[ParametersType] = set()

    for node in cast(List[Node], ExtractRepeat(node)):
        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # <parameters_type>
        parameters_type_node = cast(Node, nodes[0])
        parameters_type_value = ParametersType.Extract(parameters_type_node)  # type: ignore

        if parameters_type_value in encountered:
            raise NewStyleParameterGroupDuplicateError.FromNode(
                parameters_type_node,
                parameters_type_value.name,
            )

        encountered.add(parameters_type_value)

        parameters = list(
            itertools.chain(
                [nodes[2]],
                (
                    ExtractSequence(delimited_node)[1]
                    for delimited_node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[3])))
                ),
            ),
        )

        yield parameters_type_value, node, cast(List[Node], parameters)


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

    parameter_nodes = list(
        itertools.chain(
            [nodes[0]],
            (
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(List[Node], ExtractRepeat(cast(Optional[Node], nodes[1])))
            ),
        ),
    )

    encountered_positional_parameter = False
    keyword_parameter_index: Optional[int] = None

    parameters: List[Node] = []

    for parameter_node_index, parameter_node in enumerate(cast(List[Node], parameter_nodes)):
        # Drill into the or node
        parameter_or_delimiter_node = cast(Node, ExtractOr(parameter_node))

        if isinstance(parameter_or_delimiter_node, Node):
            parameters.append(parameter_or_delimiter_node)
            continue

        delimiter_value = TraditionalParameterDelimiter.Extract(parameter_node)  # type: ignore

        if delimiter_value == TraditionalParameterDelimiter.Positional:
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

        elif delimiter_value == TraditionalParameterDelimiter.Keyword:
            # We shouldn't see this more than once
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterDuplicateKeywordError.FromNode(parameter_node)

            keyword_parameter_index = parameter_node_index

            if parameters:
                yield ParametersType.any, node, parameters

        else:
            assert False, delimiter_value  # pragma: no cover

        parameters = []

    # The keyword delimiter should never be the last parameter
    if keyword_parameter_index == len(parameter_nodes) - 1:
        raise TraditionalDelimiterKeywordError.FromNode(cast(Node, parameter_nodes[-1]))

    if parameters:
        if keyword_parameter_index is not None:
            parameters_type = ParametersType.key
        else:
            parameters_type = ParametersType.any

        yield parameters_type, node, parameters
