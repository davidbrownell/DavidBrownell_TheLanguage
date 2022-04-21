# ----------------------------------------------------------------------
# |
# |  ParametersFragmentImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:53:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that helps when implementing parameters"""

import itertools
import os

from enum import auto, Enum
from typing import Callable, cast, Dict, Generator, List, Optional, Type, TypeVar, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import ModifierImpl

    from .. import Tokens as CommonTokens

    from ...GrammarPhrase import AST

    from ....Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        Error,
        ErrorException,
        ParserInfo,
        Region,
    )


# ----------------------------------------------------------------------
class ParametersType(Enum):
    pos                                     = auto()
    key                                     = auto()
    any                                     = auto()

CreateParametersTypePhraseItem              = ModifierImpl.StandardCreatePhraseItemFuncFactory(ParametersType)
ExtractParametersType                       = ModifierImpl.StandardExtractFuncFactory(ParametersType)


# ----------------------------------------------------------------------
class TraditionalParameterDelimiter(Enum):
    positional                              = "/"
    keyword                                 = "*"

CreateTraditionalParameterDelimiterPhraseItem           = ModifierImpl.ByValueCreatePhraseItemFuncFactory(TraditionalParameterDelimiter)
ExtractTraditionalParameterDelimiter                    = ModifierImpl.ByValueExtractFuncFactory(TraditionalParameterDelimiter)


# ----------------------------------------------------------------------
RequiredParameterAfterDefaultError          = CreateError(
    "A required parameter may not appear after a parameter with a default value",
    prev_region=Region,
)

NewStyleParameterGroupDuplicateError        = CreateError(
    "The parameter group '{name}' has already been specified",
    name=str,
    prev_region=Region,
)

TraditionalDelimiterPositionalError         = CreateError(
    "The positional delimiter ('{}') must appear after at least 1 parameter".format(
        TraditionalParameterDelimiter.positional.value,
    ),
)

TraditionalDelimiterDuplicatePositionalError            = CreateError(
    "The positional delimiter ('{}') may only appear once in a list of parameters".format(
        TraditionalParameterDelimiter.positional.value,
    ),
    prev_region=Region,
)

TraditionalDelimiterOrderError              = CreateError(
    "The positional delimiter ('{}') must appear before the keyword delimiter ('{}')".format(
        TraditionalParameterDelimiter.positional.value,
        TraditionalParameterDelimiter.keyword.value,
    ),
    keyword_region=Region,
)

TraditionalDelimiterDuplicateKeywordError   = CreateError(
    "The keyword delimiter ('{}') may only appear once in a list of parameters".format(
        TraditionalParameterDelimiter.keyword.value,
    ),
    prev_region=Region,
)

TraditionalDelimiterKeywordError            = CreateError(
    "The keyword delimiter ('{}') must appear before at least 1 parameter".format(
        TraditionalParameterDelimiter.keyword.value,
    ),
)


# ----------------------------------------------------------------------
def Create(
    name: str,
    open_token: str,
    close_token: str,
    parameter_element: PhraseItem,
    *,
    allow_empty: bool,
) -> PhraseItem:
    traditional_parameter_element = (parameter_element, ) + CreateTraditionalParameterDelimiterPhraseItem()

    content_phrase_element = (
        # New Style
        #
        #   (<parameters_type> ':' <parameter_element> (',' <parameter_element>)* ',')?)+
        #
        OneOrMorePhraseItem(
            name="New Style",
            item=[
                # <parameters_type> ':'
                CreateParametersTypePhraseItem(),
                ":",

                # <parameter_element>
                parameter_element,

                # (',' <parameter_element>)*
                ZeroOrMorePhraseItem(
                    name="Comma and Element",
                    item=[
                        ",",
                        parameter_element,
                    ],
                ),

                # ','?
                OptionalPhraseItem(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        ),

        # Traditional
        #
        #   <traditional_parameter_element> (',' <traditional_parameter_element>)* ','
        #
        PhraseItem(
            name="Traditional",
            item=[
                # <traditional_parameter_element>
                traditional_parameter_element,

                # (',' <traditional_parameter_element>)*
                ZeroOrMorePhraseItem(
                    name="Comma and Element",
                    item=[
                        ",",
                        traditional_parameter_element,
                    ],
                ),

                # ','?
                OptionalPhraseItem(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        ),
    )

    if allow_empty:
        content_phrase_element = OptionalPhraseItem(content_phrase_element)

    return PhraseItem(
        name=name,
        item=[
            open_token,
            CommonTokens.PushIgnoreWhitespaceControl,

            content_phrase_element,

            CommonTokens.PopIgnoreWhitespaceControl,
            close_token,
        ],
    )


# ----------------------------------------------------------------------
ExtractReturnType                           = TypeVar("ExtractReturnType", bound=ParserInfo)

def Extract(
    parser_info_type: Type[ExtractReturnType],
    extract_element_func: Callable[[AST.Node], Union[List[Error], Tuple[ParserInfo, bool]]],
    node: AST.Node,
    *,
    allow_empty: bool,
) -> Union[
    List[Error],
    bool,
    ExtractReturnType,
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 5

    if allow_empty:
        all_parameters_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
        if all_parameters_node is None:
            return False
    else:
        all_parameters_node = cast(AST.Node, nodes[2])

    all_parameters_node = cast(AST.Node, ExtractOr(all_parameters_node))

    assert all_parameters_node.type is not None

    if all_parameters_node.type.name == "Traditional":
        enum_func = _EnumTraditional
    else:
        enum_func = _EnumNewStyle

    initial_default_param: Optional[AST.Node] = None

    parameters_parser_infos: Dict[ParametersType, Tuple[AST.Node, List[ParserInfo]]] = {}
    errors: List[Error] = []

    for parameters_type, parameters_node, parameter_nodes, parameter_errors in enum_func(all_parameters_node):
        if parameter_errors:
            errors += parameter_errors
            continue

        parser_infos: List[ParserInfo] = []

        for parameter_node in parameter_nodes:
            try:
                result = extract_element_func(parameter_node)
                if isinstance(result, list):
                    errors += result
                    continue

                parser_info, has_default = result
            except ErrorException as ex:
                errors += ex.errors
                continue

            if has_default:
                initial_default_param = parameter_node
            elif initial_default_param is not None:
                errors.append(
                    RequiredParameterAfterDefaultError.Create(
                        region=CreateRegion(parameter_node),
                        prev_region=CreateRegion(initial_default_param),
                    ),
                )

            parser_infos.append(parser_info)

        assert parser_infos
        assert parameters_type not in parameters_parser_infos

        parameters_parser_infos[parameters_type] = (parameters_node, parser_infos)

    if not errors:
        try:
            return parser_info_type.Create(  # type: ignore
                CreateRegions(
                    node,
                    parameters_parser_infos.get(ParametersType.pos, [None])[0],
                    parameters_parser_infos.get(ParametersType.any, [None])[0],
                    parameters_parser_infos.get(ParametersType.key, [None])[0],
                ),
                parameters_parser_infos.get(ParametersType.pos, [None, None])[1],
                parameters_parser_infos.get(ParametersType.any, [None, None])[1],
                parameters_parser_infos.get(ParametersType.key, [None, None])[1],
            )
        except ErrorException as ex:
            errors += ex.errors

    assert errors
    return errors


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _EnumNewStyle(
    node: AST.Node,
) -> Generator[
    Tuple[ParametersType, AST.Node, List[AST.Node], List[Error]],
    None,
    None,
]:
    errors: List[Error] = []
    encountered: Dict[ParametersType, AST.Node] = {}

    for node in cast(List[AST.Node], ExtractRepeat(node)):
        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # <parameters_type>
        parameters_type_node = cast(AST.Node, nodes[0])
        parameters_type_info = ExtractParametersType(parameters_type_node)

        prev_parameters_type = encountered.get(parameters_type_info, None)
        if prev_parameters_type is not None:
            errors.append(
                NewStyleParameterGroupDuplicateError.Create(
                    region=CreateRegion(parameters_type_node),
                    prev_region=CreateRegion(prev_parameters_type),
                ),
            )

        encountered[parameters_type_info] = parameters_type_node

        parameters = list(
            itertools.chain(
                [cast(AST.Node, nodes[2]), ],
                (
                    cast(AST.Node, ExtractSequence(delimited_node)[1])
                    for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(Optional[AST.Node], nodes[3])))
                ),
            ),
        )

        yield parameters_type_info, node, parameters, errors


# ----------------------------------------------------------------------
def _EnumTraditional(
    node: AST.Node,
) -> Generator[
    Tuple[ParametersType, AST.Node, List[AST.Node], List[Error]],
    None,
    None,
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    parameter_nodes = list(
        itertools.chain(
            [cast(AST.Node, nodes[0]), ],
            (
                cast(AST.Node, ExtractSequence(delimited_node)[1])
                for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(Optional[AST.Node], nodes[1])))
            ),
        ),
    )

    positional_delimiter_node: Optional[AST.Node] = None
    keyword_delimiter_node: Optional[AST.Node] = None

    parameters: List[AST.Node] = []
    errors: List[Error] = []

    for parameter_node_index, parameter_node in enumerate(parameter_nodes):
        parameter_or_delimiter_node = cast(AST.Node, ExtractOr(parameter_node))

        if isinstance(parameter_or_delimiter_node, AST.Node):
            parameters.append(parameter_or_delimiter_node)
            continue

        delimiter_value = ExtractTraditionalParameterDelimiter(parameter_or_delimiter_node)

        if delimiter_value == TraditionalParameterDelimiter.positional:
            # This should never be the first parameter
            if parameter_node_index == 0:
                errors.append(
                    TraditionalDelimiterPositionalError.Create(
                        region=CreateRegion(parameter_node),
                    ),
                )

            # We shouldn't see this more than once
            if positional_delimiter_node is not None:
                errors.append(
                    TraditionalDelimiterDuplicatePositionalError.Create(
                        region=CreateRegion(parameter_node),
                        prev_region=CreateRegion(positional_delimiter_node),
                    ),
                )

            # We shouldn't see this after a keyword parameter
            if keyword_delimiter_node is not None:
                errors.append(
                    TraditionalDelimiterOrderError.Create(
                        region=CreateRegion(parameter_node),
                        keyword_region=CreateRegion(keyword_delimiter_node),
                    ),
                )

            positional_delimiter_node = parameter_node

            assert parameters
            yield ParametersType.pos, node, parameters, errors

        elif delimiter_value == TraditionalParameterDelimiter.keyword:
            # We shouldn't see this more than once
            if keyword_delimiter_node is not None:
                errors.append(
                    TraditionalDelimiterDuplicateKeywordError.Create(
                        region=CreateRegion(parameter_node),
                        prev_region=CreateRegion(keyword_delimiter_node),
                    ),
                )

            keyword_delimiter_node = parameter_node

            if parameters:
                yield ParametersType.any, node, parameters, errors

        else:
            assert False, delimiter_value  # pragma: no cover

        parameters = []
        errors = []

    # The keyword delimiter should never be the last parameter
    if keyword_delimiter_node == parameter_nodes[len(parameter_nodes) - 1]:
        errors.append(
            TraditionalDelimiterKeywordError.Create(
                region=CreateRegion(keyword_delimiter_node),
            ),
        )

    if parameters:
        if keyword_delimiter_node is not None:
            parameters_type = ParametersType.key
        else:
            parameters_type = ParametersType.any

        yield parameters_type, node, parameters, errors
