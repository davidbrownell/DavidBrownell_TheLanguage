# ----------------------------------------------------------------------
# |
# |  Statements.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 12:12:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains common statements used in other statement definitions"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from ...GrammarStatement import Node, Statement


# ----------------------------------------------------------------------
# <type_name> <var|ref|val|view|...>
Type                                        = Statement(
    "Type",
    CommonTokens.Name,
    # TODO: Tempataes
    Statement.NamedItem(
        "Modifier",
        [
            # TODO: Not sure that all of these should be here
            CommonTokens.Var,
            CommonTokens.Ref,
            CommonTokens.Val,
            CommonTokens.View,
            CommonTokens.Isolated,
            CommonTokens.Shared,
            CommonTokens.Immutable,
            CommonTokens.Mutable,
        ],
    ),
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeInfo(object):
    """Contains information about a type"""

    Name: str
    Modifier: CommonTokens.RegexToken


def GetTypeInfo(
    node: Node,
) -> TypeInfo:
    assert len(node.Children) == 2

    name = node.Children[0].Value.Match.group("value")

    assert len(node.Children[1].Children) == 1
    modifier = node.Children[1].Children[0].Type

    return TypeInfo(name, modifier)
