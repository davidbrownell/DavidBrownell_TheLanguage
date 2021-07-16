# ----------------------------------------------------------------------
# |
# |  GrammarDSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:05:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used across the grammar definition"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    # Convenience imports for other files, please do not remove
    from ....ParserImpl.AST import Leaf, Node, RootNode
    from ....ParserImpl.StatementDSL import (
        DynamicStatements,
        Statement,
        StatementItem,
    )

    # Standard imports
    from . import Tokens as CommonTokens
    from ....ParserImpl import StatementDSL
    from ....ParserImpl.Token import Token


# ----------------------------------------------------------------------
def CreateStatement(
    item: StatementItem.ItemType,
    name: str=None,
) -> Statement:
    # Single tokens don't have the opportunity to participate in node validation,
    # as there won't be a corresponding node emitted. In this case, turn the token
    # into a sequence.
    if isinstance(item, Token):
        item = [item]

    return StatementDSL.CreateStatement(
        item=item,
        name=name,
        comment_token=CommonTokens.Comment,
    )
