# ----------------------------------------------------------------------
# |
# |  Location.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-01 08:01:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Location object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import ComparisonOperators
from CommonEnvironment.YamlRepr import ObjectReprImplBase

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@ComparisonOperators
@dataclass(frozen=True, repr=False)
class Location(ObjectReprImplBase):
    """Point of interest within a source file"""

    line: int
    column: int

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        ObjectReprImplBase.__init__(self)

        assert self.line >= 1
        assert self.column >= 1

    # ----------------------------------------------------------------------
    @staticmethod
    def Compare(value1, value2):
        result = value1.line - value2.line
        if result != 0:
            return result

        result = value1.column - value2.column
        if result != 0:
            return result

        return 0
