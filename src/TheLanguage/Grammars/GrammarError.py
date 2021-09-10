# ----------------------------------------------------------------------
# |
# |  GrammarError.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-09 15:10:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GrammarError object"""

import os

from typing import Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .GrammarPhrase import CreateLexerRegion
    from ..Lexer.Components.LexerError import LexerError
    from ..Parser.Components.AST import Leaf, Node


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GrammarError(LexerError):
    """Base class for all Grammar-related errors"""

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Union[Leaf, Node],
        *args,
    ):
        return cls(CreateLexerRegion(node), *args)
