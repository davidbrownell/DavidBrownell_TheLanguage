# ----------------------------------------------------------------------
# |
# |  ConstrainedType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 13:48:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConstrainedType object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ConcreteType import ConcreteType


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConstrainedType(Interface.Interface):
    """Type with a specific set of constraint parameters (if required)"""

    # ----------------------------------------------------------------------
    concrete_type: ConcreteType
