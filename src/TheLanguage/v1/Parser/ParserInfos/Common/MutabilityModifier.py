# ----------------------------------------------------------------------
# |
# |  MutabilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 12:26:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MutabilityModifier object"""

import os

from enum import auto, Enum

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Error import CreateError


# ----------------------------------------------------------------------
MutabilityModifierRequiredError             = CreateError(
    "A mutability modifier is required in this context",
)

MutabilityModifierNotAllowedError           = CreateError(
    "A mutability modifier is not allowed in this context",
)

InvalidNewMutabilityModifierError           = CreateError(
    "The mutability modifier 'new' is not allowed in this context",
)


# ----------------------------------------------------------------------
class MutabilityModifier(Enum):
    #                                                     Mutable   Shared      Finalized   Notes
    #                                                     --------  ----------  ---------   -----------------
    var                                     = auto()    # Yes       No          No
    ref                                     = auto()    # Yes       Yes         No
    view                                    = auto()    # No        No          No
    val                                     = auto()    # No        Yes         Yes
    immutable                               = auto()    # No        Yes | No    Yes | No    view | val

    new                                     = auto()    # Depends on associated Type; should only be used with method return values
                                                        # in concepts, interfaces, and mixins when the actual type is not known.

    # TODO: Validate that new is used appropriately
