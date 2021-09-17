# ----------------------------------------------------------------------
# |
# |  AutomatedTests.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 08:53:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Types and functions that help when writing automated tests"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import Location, Region


# ----------------------------------------------------------------------
def CreateRegion(
    start_line: int,
    start_column: int,
    end_line: int,
    end_column: int,
) -> Region:
    # pylint: disable=too-many-function-args
    return Region(Location(start_line, start_column), Location(end_line, end_column))
