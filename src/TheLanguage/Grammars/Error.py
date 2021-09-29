# ----------------------------------------------------------------------
# |
# |  Error.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 08:31:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Error object"""

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
    from .GrammarInfo import CreateParserRegion
    from ..Lexer.Components.AST import Leaf, Node
    from ..Parser.Error import Error as ParserError


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Error(ParserError):
    """Base class for all errors generated by Grammar-related code"""

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Union[Leaf, Node],
        *args,
    ):
        return cls(CreateParserRegion(node), *args)
