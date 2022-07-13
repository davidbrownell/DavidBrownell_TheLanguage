# ----------------------------------------------------------------------
# |
# |  Dependency.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-13 08:08:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that tracks dependencies within a class hierarchy"""

import os

from typing import Generator, Optional, Tuple, TYPE_CHECKING, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Common.VisibilityModifier import VisibilityModifier

    if TYPE_CHECKING:
        from ...ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo  # pylint: disable=unused-import
        from ...ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo  # pylint: disable=unused-import
        from ...FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo  # pylint: disable=unused-import
        from ...TypeAliasStatementParserInfo import TypeAliasStatementParserInfo  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class Dependency(Interface.Interface):
    """Abstract base class for DependencyNode and DependencyLeaf objects"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    StatementParserInfoType                 = Union[
        "ClassAttributeStatementParserInfo",
        "ClassStatementParserInfo",
        "FuncDefinitionStatementParserInfo",
        "TypeAliasStatementParserInfo",
    ]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class EnumResult(object):
        visibility: Optional[VisibilityModifier] # None indicates that it isn't visible
        statement: "Dependency.StatementParserInfoType"
        dependency_info: Union["ClassStatementParserInfo", "ClassStatementDependencyParserInfo"]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EnumDependencies() -> Generator["Dependency.EnumResult", None, None]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def ResolveDependencies(self) -> Tuple[
        Optional[VisibilityModifier],
        "Dependency.StatementParserInfoType",
    ]:
        *_, last = self.EnumDependencies()

        return last.visibility, last.statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyNode(Dependency):
    # ----------------------------------------------------------------------
    dependency: "ClassStatementDependencyParserInfo"
    next: Dependency

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumDependencies(self) -> Generator[Dependency.EnumResult, None, None]:
        last_result: Optional[Dependency.EnumResult] = None

        for last_result in self.next.EnumDependencies():
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


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyLeaf(Dependency):
    # ----------------------------------------------------------------------
    class_statement: "ClassStatementParserInfo"
    statement: Dependency.StatementParserInfoType

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumDependencies(self) -> Generator[Dependency.EnumResult, None, None]:
        yield Dependency.EnumResult(
            self.statement.visibility,
            self.statement,
            self.class_statement,
        )
