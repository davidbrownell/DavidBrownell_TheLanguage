# ----------------------------------------------------------------------
# |
# |  FuncParametersPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:43:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about function parameters"""

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
    from ..Expressions.ExpressionPhrase import ExpressionPhrase
    from ..Types.TypePhrase import Phrase, Region, TypePhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParametersItemPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    type: TypePhrase
    is_variadic: Optional[bool]
    name: str
    default_value: Optional[ExpressionPhrase]

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
        super(FuncParametersItemPhrase, self).__init__(regions)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParametersPhrase(Phrase):
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List[FuncParametersItemPhrase]]
    any: Optional[List[FuncParametersItemPhrase]]
    keyword: Optional[List[FuncParametersItemPhrase]]

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
        super(FuncParametersPhrase, self).__init__(regions)
        assert self.positional or self.any or self.keyword
