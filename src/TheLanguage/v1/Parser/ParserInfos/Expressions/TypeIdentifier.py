# ----------------------------------------------------------------------
# |
# |  TypeIdentifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-01 09:57:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used to identify if types are the same or compatible"""

import os

from typing import Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    pass # BugBug


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeIdentifier(object):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Matches(
        other: "TypeIdentifier",
        *,
        strict: bool=False,
    ) -> bool:
        """Returns True if the other type matches this type"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StandardTypeIdentifier(TypeIdentifier):
    # ----------------------------------------------------------------------
    id: Tuple

    # ----------------------------------------------------------------------
    @Interface.override
    def Matches(
        self,
        other: TypeIdentifier,
        *,
        strict: bool=False,
    ) -> bool:
        return (
            isinstance(other, StandardTypeIdentifier)
            and len(self.id) == len(other.id)
            and all(
                this_item.Matches(other_item, strict=strict)
                for this_item, other_item in zip(self.id, other.id)
            )
        )
