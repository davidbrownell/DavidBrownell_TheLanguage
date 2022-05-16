# ----------------------------------------------------------------------
# |
# |  ImportStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 12:03:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ImportStatementParserInfo and ImportStatementItemParserInfo objects"""

import os

from enum import auto, Enum
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, ParserInfoType, Region, ScopeFlag, StatementParserInfo

    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ...Error import Error, ErrorException

    if TYPE_CHECKING:
        from ...NamespaceInfo import ParsedNamespaceInfo  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class ImportType(Enum):
    source_is_module                        = auto()
    source_is_directory                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementItemParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    name: str
    alias: Optional[str]

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
        super(ImportStatementItemParserInfo, self).__init__(
            ParserInfoType.Standard,
            regions,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def GetNameAndRegion(self) -> Tuple[Optional[str], Region]:
        if self.alias is not None:
            return self.alias, self.regions__.alias

        return super(ImportStatementItemParserInfo, self).GetNameAndRegion()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    ImportsType                             = Dict[str, "ParsedNamespaceInfo"]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    source_parts: List[str]
    import_items: List[ImportStatementItemParserInfo]

    import_type: ImportType

    # ----------------------------------------------------------------------
    # |
    # |  Public Members
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        super(ImportStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "import_items",
                "import_type",
            ],
            validate=False,
            imports__=None,                 # type: ignore
            is_imports__initialized__=None, # type: ignore
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = VisibilityModifier.private
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        # Validate
        self.ValidateRegions()

        errors: List[Error] = []

        if self.visibility == VisibilityModifier.protected:
            errors.append(
                InvalidProtectedError.Create(
                    region=self.regions__.visibility,
                ),
            )

        if errors:
            raise ErrorException(*errors)


    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("import_items", self.import_items),
            ],  # type: ignore
            children=None,
        )

    # ----------------------------------------------------------------------
    # This method is invoked during validation
    def InitImports(
        self,
        value: ImportsType,
    ) -> None:
        assert not self.is_imports__initialized__
        object.__setattr__(self, self.__class__._IMPORTS_ATTRIBUTE_NAME, value)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    @property
    def imports__(self) -> "ImportsType":
        return getattr(self, self.__class__._IMPORTS_ATTRIBUTE_NAME)  # pylint: disable=protected-access

    @property
    def is_imports__initialized__(self) -> bool:
        return hasattr(self, self.__class__._IMPORTS_ATTRIBUTE_NAME)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _IMPORTS_ATTRIBUTE_NAME                 = "_imports"
