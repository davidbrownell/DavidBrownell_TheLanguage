# ----------------------------------------------------------------------
# |
# |  HierarchyInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-30 08:06:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used when generating information about class hierarchies"""

import os

from typing import Generator, Optional, Union, TYPE_CHECKING

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.VisibilityModifier import VisibilityModifier

    if TYPE_CHECKING:
        from ..ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
        from ..ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
        from ..FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
        from ..TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class HierarchyInfo(object):
    # ----------------------------------------------------------------------
    StatementParserInfoType                 = Union[
        "ClassAttributeStatementParserInfo",
        "ClassStatementParserInfo",
        "FuncDefinitionStatementParserInfo",
        "TypeAliasStatementParserInfo",
    ]

    # ----------------------------------------------------------------------
    visibility: Optional[VisibilityModifier] # None indicates that it isn't visible
    statement: "HierarchyInfo.StatementParserInfoType"


# ----------------------------------------------------------------------
class Dependency(Interface.Interface):
    # ----------------------------------------------------------------------
    # |  Public Types
    @dataclass(frozen=True)
    class EnumResult(HierarchyInfo):
        # ----------------------------------------------------------------------
        dependency_info: Union["ClassStatementParserInfo", "ClassStatementDependencyParserInfo"]

    # ----------------------------------------------------------------------
    # |  Public Methods
    @staticmethod
    @Interface.abstractmethod
    def EnumHierarchy() -> Generator["EnumResult", None, None]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def ResolveHierarchy(self) -> HierarchyInfo:
        *_, leaf = self.EnumHierarchy()
        return leaf


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyLeaf(Dependency):
    # ----------------------------------------------------------------------
    class_statement: "ClassStatementParserInfo"
    statement: HierarchyInfo.StatementParserInfoType

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumHierarchy(self) -> Generator[Dependency.EnumResult, None, None]:
        yield Dependency.EnumResult(
            self.statement.visibility,
            self.statement,
            self.class_statement,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyNode(Dependency):
    # ----------------------------------------------------------------------
    dependency: "ClassStatementDependencyParserInfo"
    next: Dependency

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumHierarchy(self) -> Generator[Dependency.EnumResult, None, None]:
        last_result: Optional[Dependency.EnumResult] = None

        for last_result in self.next.EnumHierarchy():
            yield last_result

        assert last_result is not None
        assert self.dependency.visibility is not None

        if last_result.visibility is None or last_result.visibility == VisibilityModifier.private:
            visibility = None
        else:
            visibility = VisibilityModifier(
                min(last_result.visibility.value, self.dependency.visibility.value),
            )

        yield Dependency.EnumResult(
            visibility,
            last_result.statement,
            self.dependency,
        )
