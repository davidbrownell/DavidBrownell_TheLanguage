# ----------------------------------------------------------------------
# |
# |  AutomatedTests.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:16:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Utilities helpful when writing automated tests"""

import os

from typing import List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Parser import Location, Region


# ----------------------------------------------------------------------
class RegionCreator(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        start=1,
    ):
        self._start: int                                = start
        self._regions: List[Region]                     = []
        self._expected_error: Optional[Region]          = None

    # ----------------------------------------------------------------------
    def __call__(
        self,
        *,
        container=False,
        expected_error=False,
    ) -> Region:
        if not self._regions:
            end_factor = 1000000
        elif container:
            end_factor = 10000
        else:
            end_factor = 1

        region = Region(
            Location(self._start, self._start + 1),
            Location(
                (self._start + 2) * end_factor,
                (self._start + 3) * end_factor,
            ),
        )

        self._start += 4

        if expected_error:
            assert self._expected_error is None
            self._expected_error = region

        self._regions.append(region)
        return region

    # ----------------------------------------------------------------------
    def __getitem__(
        self,
        index: int,
    ) -> Region:
        return self._regions[index]

    # ----------------------------------------------------------------------
    def ExpectedErrorRegion(self) -> Region:
        assert self._expected_error is not None
        return self._expected_error
