# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 20:37:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import os

from enum import Enum
from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import TypeNode
    from ..Common import Flags


# ----------------------------------------------------------------------
class TypeModifier(Enum):
    """\
    TODO: Comment
    """

    #             Isolated    Shared
    #             --------    ------
    # Mutable:      Var        Ref
    # Immutable:    Val        View
    #
    # Modifier values valid when Type is used as a...
    #
    #   ...Variable: Var, Val, View
    #   ...Parameter: Ref, Immutable, Val, View
    #   ...Return Type: Var, Ref, Val, View

    Mutable                                 = Flags.TypeFlags.Mutable
    Immutable                               = Flags.TypeFlags.Immutable

    Var                                     = Flags.TypeFlags.Mutable | Flags.TypeFlags.Isolated
    Ref                                     = Flags.TypeFlags.Mutable | Flags.TypeFlags.Shared
    Val                                     = Flags.TypeFlags.Immutable | Flags.TypeFlags.Isolated
    View                                    = Flags.TypeFlags.Immutable | Flags.TypeFlags.Shared


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StandardType(TypeNode):
    """\
    TODO: Comment
    """

    Name: str

    # TODO: Templates

    # If this value is None, use context to determine the most appropriate value; default to Var if
    # the context is ambiguous.
    Modifier: Optional[TypeModifier]
