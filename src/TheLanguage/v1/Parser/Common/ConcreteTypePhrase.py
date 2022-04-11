# ----------------------------------------------------------------------
# |
# |  ConcreteTypePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 09:47:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConcreteTypePhrase"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Phrase import Phrase

    from ...Common.Region import Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConcreteTypeItemPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    name: str

    # TODO: Templates
    # TODO: Constraints

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ConcreteTypeItemPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConcreteTypePhrase(Phrase):
    has_children__                          = True

    regions: InitVar[List[Optional[Region]]]
    items: List[ConcreteTypeItemPhrase]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ConcreteTypePhrase, self).__init__(regions)
