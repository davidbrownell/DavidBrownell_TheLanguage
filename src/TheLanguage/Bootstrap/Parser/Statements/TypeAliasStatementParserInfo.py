# ----------------------------------------------------------------------
# |
# |  TypeAliasStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 13:20:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatementParserInfo object"""

import os

from typing import Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo
    from ..Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo
    from ..Common.TemplateParametersParserInfo import TemplateParametersParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Common.VisitorTools import StackHelper
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeAliasStatementParserInfo(StatementParserInfo):
    visibility: InitVar[Optional[VisibilityModifier]]
    Visibility: VisibilityModifier                      = field(init=False)

    Name: str
    Templates: Optional[TemplateParametersParserInfo]
    Constraints: Optional[ConstraintParametersParserInfo]

    Type: TypeParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility):
        super(TypeAliasStatementParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        if visibility is None:
            visibility = VisibilityModifier.private # TODO: Hard coded
            object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        object.__setattr__(self, "Visibility", visibility)

        self.Validate()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                self.Type.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Templates is not None:
                with helper["Templates"]:
                    self.Templates.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Constraints is not None:
                with helper["Constraints"]:
                    self.Constraints.Accept(visitor, helper.stack, *args, **kwargs)
