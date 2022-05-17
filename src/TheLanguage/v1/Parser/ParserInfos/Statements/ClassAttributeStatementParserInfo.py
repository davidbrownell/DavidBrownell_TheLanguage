# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 11:53:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassAttributeStatementParserInfo object"""

import os

from typing import List, Optional, TYPE_CHECKING

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfoType, Region, ScopeFlag, StatementParserInfo
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Error import Error, ErrorException

    if TYPE_CHECKING:
        from ...NamespaceInfo import ParsedNamespaceInfo  # pylint: disable=unused-import


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassAttributeStatementParserInfo(StatementParserInfo):
    """Attribute of a class"""

    # ----------------------------------------------------------------------
    class_capabilities: ClassCapabilities

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    type: ExpressionParserInfo

    name: str
    documentation: Optional[str]

    initialized_value: Optional[ExpressionParserInfo]

    keyword_initialization: Optional[bool]
    no_initialization: Optional[bool]
    no_serialize: Optional[bool]
    no_compare: Optional[bool]
    is_override: Optional[bool]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Class,
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        super(ClassAttributeStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "class_capabilities",
                "type",
                "initialized_value",
            ],
            validate=False,
            class_capabilities=lambda value: value.name,
            type__=None,                    # type: ignore
            is_type__initialized__=None,    # type: ignore
        )

        # Set defaults
        if visibility_param is None and self.class_capabilities.default_attribute_visibility is not None:
            visibility_param = self.class_capabilities.default_attribute_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        for func in [
            # TODO: lambda: self.class_capabilities.ValidateClassAttributeStatementCapabilities(self),
            lambda: self.type.ValidateAsType(self.parser_info_type__),
            self.initialized_value.ValidateAsExpression if self.initialized_value is not None else lambda: None,
        ]:
            try:
                func()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # This method is invoked during validation
    def InitType(
        self,
        value: "ParsedNamespaceInfo",
    ) -> None:
        assert not self.is_type__initialized__
        object.__setattr__(self, self.__class__._TYPE_ATTRIBUTE_NAME, value)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    @property
    def type__(self) -> "ParsedNamespaceInfo":
        return getattr(self, self.__class__._TYPE_ATTRIBUTE_NAME)  # pylint: disable=protected-access

    @property
    def is_type__initialized__(self) -> bool:
        return hasattr(self, self.__class__._TYPE_ATTRIBUTE_NAME)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _TYPE_ATTRIBUTE_NAME                    = "_type"
