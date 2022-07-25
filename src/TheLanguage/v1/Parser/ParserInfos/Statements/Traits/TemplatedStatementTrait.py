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

from typing import Any, Callable, Dict, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.TemplateParametersParserInfo import TemplateParametersParserInfo


# ----------------------------------------------------------------------
# TODO: This should be based on NamedTrait

@dataclass(frozen=True, repr=False)
class TemplatedStatementTrait(Interface.Interface):
    """Apply to statements that can have templates"""

    # ----------------------------------------------------------------------
    templates_param: InitVar[Optional[TemplateParametersParserInfo]]
    templates: Optional[TemplateParametersParserInfo]   = field(init=False, default=None)

    is_default_initializable: bool                      = field(init=False, default=False)

    # ----------------------------------------------------------------------
    def __post_init__(self, templates_param):
        object.__setattr__(self, "templates", templates_param)

        object.__setattr__(
            self,
            "is_default_initializable",
            not self.templates or self.templates.is_default_initializable,  # pylint: disable=no-member
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "templates",
            "is_default_initializable",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {
            "is_default_initializable": None,
        }
