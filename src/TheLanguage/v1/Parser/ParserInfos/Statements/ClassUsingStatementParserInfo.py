# ----------------------------------------------------------------------
# |
# |  ClassUsingStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-20 09:35:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClasSUsingStatementParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfoType, ScopeFlag, StatementParserInfo, TranslationUnitRegion
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType
    from ..Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
InvalidUsingExpressionError                 = CreateError(
    "Invalid 'using' expression",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassUsingStatementParserInfo(StatementParserInfo):
    """Exposes statements from a base class within the scope of the current class"""

    # ----------------------------------------------------------------------
    class_capabilities: ClassCapabilities

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    type: BinaryExpressionParserInfo

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Class,
            ParserInfoType.TypeCustomization,           # type: ignore
            regions,                                    # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        super(ClassUsingStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "class_capabilities",
                "type",
            ],
            validate=False,
            **{
                "class_capabilities": lambda value: value.name,
            },
        )

        # Set defaults
        if visibility_param is None and self.class_capabilities.default_using_visibility is not None:
            visibility_param = self.class_capabilities.default_using_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        self.class_capabilities.ValidateUsingStatementCapabilities(self)

        errors: List[Error] = []

        if (
            not isinstance(self.type, BinaryExpressionParserInfo)
            or self.type.operator != BinaryExpressionOperatorType.Access
            or not isinstance(self.type.left_expression, FuncOrTypeExpressionParserInfo)
            or not isinstance(self.type.right_expression, FuncOrTypeExpressionParserInfo)
        ):
            errors.append(
                InvalidUsingExpressionError.Create(
                    region=self.type.regions__.self__,
                ),
            )

        if errors:
            raise ErrorException(*errors)
