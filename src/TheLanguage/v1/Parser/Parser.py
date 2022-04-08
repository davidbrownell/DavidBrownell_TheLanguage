# ----------------------------------------------------------------------
# |
# |  Parser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 12:49:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Creates and extracts parser information from nodes"""

import os

from typing import List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Phrase import Region

    from ..Lexer.Lexer import AST, Phrase as LexerPhrase


# ----------------------------------------------------------------------
def CreateRegions(
    *nodes: Union[
        AST.Leaf,
        AST.Node,
        Region,
        LexerPhrase.NormalizedIteratorRange,
        None,
    ],
) -> List[Optional[Region]]:
    results: List[Optional[Region]] = []

    for node in nodes:
        if node is None:
            results.append(None)
        elif isinstance(node, Region):
            results.append(node)
        elif isinstance(node, LexerPhrase.NormalizedIteratorRange):
            results.append(node.ToRegion())
        elif isinstance(node, (AST.Leaf, AST.Node)):
            if node.iter_range is None:
                results.append(None)
            else:
                results.append(node.iter_range.ToRegion())
        else:
            assert False, node  # pragma: no cover

    return results
