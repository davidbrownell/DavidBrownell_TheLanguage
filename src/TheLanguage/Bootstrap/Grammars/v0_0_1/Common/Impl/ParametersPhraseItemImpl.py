import itertools
import os

from enum import auto, Enum
from typing import cast, Callable, Dict, Generator, List, Optional, Set, Tuple, Type, TypeVar, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import ModifierImpl

    from .. import Tokens as CommonTokens

    from ....Error import Error

    from .....Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        Node,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from .....Parser.Parser import CreateParserRegions
    from .....Parser.ParserInfo import ParserInfo


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
def Create(
    name: str,
    open_token: str,
    close_token: str,
    parameter_item: PhraseItem,
    *,
    allow_empty: bool,
) -> PhraseItem:
    traditional_parameter_item = (parameter_item, ) + TraditionalParameterDelimiter.CreatePhraseItem()  # type: ignore

    content_phrase_item = (
        # New Style
        #
        #    (<parameters_type> ':' <parameter_item> (',' <parameter_item>)* ',')+
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

        # Traditional
        #
        #    <traditional_parameter_item> (',' <traditional_parameter_item>)* ','
        #
        PhraseItem.Create(
            name="Traditional",
            item=[
                # <traditional_parameter_item>
                traditional_parameter_item,

                # (',' <traditional_parameter_item>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Parameter",
                    item=[
                        ",",
                        traditional_parameter_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        ),
    )

    if allow_empty:
        content_phrase_item = OptionalPhraseItem(content_phrase_item)

    return PhraseItem.Create(
        name=name,
        item=[
            open_token,
            CommonTokens.PushIgnoreWhitespaceControl,

            content_phrase_item,

            CommonTokens.PopIgnoreWhitespaceControl,
            close_token,
        ],
    )


# ----------------------------------------------------------------------
ParserInfoType                              = TypeVar("ParserInfoType", bound=ParserInfo)

def ExtractParserInfo(
    parser_info_type: Type[ParserInfoType],
    extract_parameter_info_func: Callable[
        [Node],
        Tuple[
            ParserInfo,                     # ParserInfo for the parameter
            bool,                           # True if the node contains a parameter with a default, False if not
        ]
    ],
    node: Node,
    *,
    allow_empty: bool,
) -> Union[bool, ParserInfoType]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    if allow_empty:
        all_parameters_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
        if all_parameters_node is None:
            return False
    else:
        all_parameters_node = cast(Node, nodes[2])

    all_parameters_node = cast(Node, ExtractOr(all_parameters_node))

    assert all_parameters_node.Type is not None
    if all_parameters_node.Type.Name == "Traditional":
        enum_func = _EnumTraditional
    else:
        enum_func = _EnumNewStyle

    encountered_default = False
    parameters_infos: Dict[ParametersType, Tuple[Node, List[ParserInfo]]] = {}

    for parameters_type, parameters_node, parameter_nodes in enum_func(all_parameters_node):
        infos: List[ParserInfo] = []

        for parameter_node in parameter_nodes:
            info, has_default = extract_parameter_info_func(parameter_node)

            if has_default:
                encountered_default = True
            elif encountered_default:
                raise RequiredParameterAfterDefaultError.FromNode(parameter_node)

            infos.append(info)

        assert infos

        assert parameters_type not in parameters_infos
        parameters_infos[parameters_type] = (parameters_node, infos)

    # Extract information from the parameter infos to create the parser info object
    assert parameters_infos

    region_args: List[Optional[Node]] = [node, ]
    parser_info_args = []

    for parameters_type in [
        # The order of these items corresponds to what is expected to be the order in parser_info_type
        ParametersType.pos,
        ParametersType.any,
        ParametersType.key,
    ]:
        parameters_info = parameters_infos.get(parameters_type, None)
        if parameters_info is None:
            region_arg = None
        else:
            region_arg, parameters_info = parameters_info

        region_args.append(region_arg)
        parser_info_args.append(parameters_info)

    parser_info_args.insert(
        0,
        CreateParserRegions(*region_args),
    )

    return parser_info_type(*parser_info_args)


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

    encountered_positional = False
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
            if encountered_positional:
                raise TraditionalDelimiterDuplicatePositionalError.FromNode(parameter_node)

            # We shouldn't see this after a keyword parameter
            if keyword_parameter_index is not None:
                raise TraditionalDelimiterOrderError.FromNode(parameter_node)

            encountered_positional = True

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
