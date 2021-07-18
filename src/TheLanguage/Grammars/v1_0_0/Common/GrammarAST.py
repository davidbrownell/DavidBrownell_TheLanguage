# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:59:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities used by multiple statements and expressions"""

import os

from typing import cast, Match, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....ParserImpl.Token import Token

    from ...GrammarStatement import (
        Leaf,
        Node,
        Statement,
    )

    from ....ParserImpl.Statements.DynamicStatement import DynamicStatement
    from ....ParserImpl.Statements.OrStatement import OrStatement


# ----------------------------------------------------------------------
def ExtractLeafValue(
    leaf: Leaf,
    group_value_name: Optional[str]="value",
) -> Union[
    Match,                                  # When `group_value_name` is None
    str,                                    # When `group_value_name` is a string
]:
    result = cast(
        Token.RegexMatch,
        leaf.Value,
    ).Match

    if group_value_name is not None:
        result = result.group(group_value_name)

    return result


# ----------------------------------------------------------------------
def ExtractDynamicExpressionNode(
    node: Node,
) -> Node:
    # Drill into the Dynamic Expression node
    assert isinstance(node.Type, DynamicStatement)
    assert len(node.Children) == 1
    node = cast(Node, node.Children[0])

    # Drill into the grammar node
    assert isinstance(node.Type, OrStatement)
    assert len(node.Children) == 1
    node = cast(Node, node.Children[0])

    return node
