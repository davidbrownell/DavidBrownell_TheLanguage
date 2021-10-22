# ----------------------------------------------------------------------
# |
# |  LiteralParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:13:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralParserInfo object"""

import os

from typing import Type

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LiteralParserInfo(ParserInfo, Interface.Interface):
    """Abstract base class for all literal parser info objects"""

    Value: Type[None]                       # To be overridden by derived class

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(LiteralParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Value"],
        )

        suffix = self.__class__.__name__
        assert suffix.endswith("ParserInfo"), suffix
        suffix = suffix[:-len("ParserInfo")]

        object.__setattr__(self, "_accept_func_name", "On{}".format(suffix))

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        return getattr(visitor, self._accept_func_name)(self, stack, *args, **kwargs)  # type: ignore  & pylint: disable=no-member
