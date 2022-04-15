# ----------------------------------------------------------------------
# |
# |  ConstraintTypePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 10:04:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConstraintTypePhrase object"""

import os

from typing import Any, Callable, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Phrase import Phrase, Region
    from ..Common.CompileTimeTypes.CompileTimeType import CompileTimeType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintTypePhrase(Phrase):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]
    type: CompileTimeType

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        super(ConstraintTypePhrase, self).__init__(
            regions,
            regionless_attributes,
            validate,
            **custom_display_funcs,
        )
