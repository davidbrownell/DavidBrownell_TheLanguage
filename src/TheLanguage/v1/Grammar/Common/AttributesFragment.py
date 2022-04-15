# ----------------------------------------------------------------------
# |
# |  AttributesFragment.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 12:22:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when processing attributes"""

import itertools
import os

from typing import Any, cast, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import FuncArgumentsFragment
    from . import Tokens as CommonTokens

    from ..GrammarPhrase import AST

    from ...Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ...Parser.Error import CreateError, Error


# ----------------------------------------------------------------------
UnsupportedAttributeError                   = CreateError(
    "'{name}' is not a valid attribute in this context",
    name=str,
)

UnsupportedArgumentsError                   = CreateError(
    "The attribute '{name}' does not support arguments",
    name=str,
)

ArgumentsRequiredError                      = CreateError(
    "The attribute '{name}' must be called with arguments",
    name=str,
)

InvalidArgumentError                        = CreateError(
    "'{value_str}' is not valid for the attribute '{name}'; valid values are {valid_values_str}",
    name=str,
    value=Any,
    valid_values=List[Any],
    value_str=str,
    valid_values_str=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class AttributeData(object):
    leaf: AST.Leaf
    name: str

    arguments_node: Optional[AST.Node]
    arguments: Optional[Union[bool, FuncArgumentsFragment.FuncArgumentsPhrase]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    attribute_element = PhraseItem(
        name="Attribute Element",
        item=[
            # <name>
            CommonTokens.RuntimeAttributeName,

            # <function_arguments>?
            OptionalPhraseItem(
                FuncArgumentsFragment.Create(),
            ),
        ],
    )

    return PhraseItem(
        name="Attributes",
        item=[
            # '['
            "[",
            CommonTokens.PushIgnoreWhitespaceControl,

            # <attribute_element> (',' <attribute_element>)* ','?
            attribute_element,

            ZeroOrMorePhraseItem(
                name="Comma and Element",
                item=[
                    ",",
                    attribute_element,
                ],
            ),

            OptionalPhraseItem(
                name="Trailing Comma",
                item=",",
            ),

            # ']'
            CommonTokens.PopIgnoreWhitespaceControl,
            "]",

            # <newline>?
            OptionalPhraseItem(CommonTokens.Newline),
        ],
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> Union[
    List[Error],
    List[AttributeData]
]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 8

    errors: List[Error] = []
    results: List[AttributeData] = []

    for attribute_node in itertools.chain(
        [cast(AST.Node, nodes[2]), ],
        (
            cast(AST.Node, ExtractSequence(delimited_node)[1])
            for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[3])))
        ),
    ):
        attribute_nodes = ExtractSequence(attribute_node)
        assert len(attribute_nodes) == 1  # ODO: 2

        # <name>
        attribute_name_node = cast(AST.Leaf, attribute_nodes[0])
        attribute_name_info = ExtractToken(attribute_name_node)

        # <function_arguments>?
        function_arguments_info = None

        function_arguments_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], attribute_nodes[2])))
        if function_arguments_node is not None:
            func_arguments_info = FuncArgumentsFragment.Extract(function_arguments_node)
            if isinstance(func_arguments_info, list):
                errors += func_arguments_info
                continue

        results.append(
            AttributeData.Create(
                attribute_name_node,
                attribute_name_info,
                function_arguments_node,
                function_arguments_info,
            ),
        )

    return errors or results
