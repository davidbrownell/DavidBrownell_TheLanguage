# ----------------------------------------------------------------------
# |
# |  Region.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-01 09:12:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Region object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import ComparisonOperators
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Lexer.Location import Location



# ----------------------------------------------------------------------
@ComparisonOperators
@dataclass(frozen=True, repr=False)
class Region(ObjectReprImplBase):
    """Begining and ending for interesting blocks of code within a source file"""

    begin: Location
    end: Location

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

        assert self.begin <= self.end       # type: ignore (operator is added dynamically)

    # ----------------------------------------------------------------------
    def __contains__(self, other):
        return other.begin >= self.begin and other.end <= self.end

    # ----------------------------------------------------------------------
    @staticmethod
    def Compare(value1, value2):
        result = Location.Compare(value1.begin, value2.begin)
        if result != 0:
            return result

        result = Location.Compare(value1.end, value2.end)
        if result != 0:
            return result

        return 0
