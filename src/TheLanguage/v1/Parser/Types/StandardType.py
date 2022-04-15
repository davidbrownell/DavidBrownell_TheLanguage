# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 10:46:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypePhrase import Phrase, Region, TypePhrase

    from ..Common.ConstraintArgumentsPhrase import ConstraintArgumentsPhrase
    from ..Common.TemplateArgumentsPhrase import TemplateArgumentsPhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeItemPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    name: str

    templates: Optional[TemplateArgumentsPhrase]
    constraints: Optional[ConstraintArgumentsPhrase]

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
        super(StandardTypeItemPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardType(TypePhrase):
    items: List[StandardTypeItemPhrase]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(StandardType, self).__post_init__(regions)
