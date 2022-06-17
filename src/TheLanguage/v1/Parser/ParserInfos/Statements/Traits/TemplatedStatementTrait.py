# ----------------------------------------------------------------------
# |
# |  TemplatedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 12:59:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TemplatedStatementTrait object"""

import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.TemplateParametersParserInfo import TemplateParametersParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplatedStatementTrait(object):
    """Apply to statements that may have templates"""

    # ----------------------------------------------------------------------
    templates_param: InitVar[Optional[TemplateParametersParserInfo]]
    templates: Optional[TemplateParametersParserInfo]   = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self, templates_param):
        object.__setattr__(self, "templates", templates_param)

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "templates",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {}
