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

from typing import Generator, Generic, Optional, Tuple, TypeVar, Union

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
    from ....Statements.ClassStatementParserInfo import ClassStatementDependencyParserInfo


# ----------------------------------------------------------------------
DependencyValueT                            = TypeVar("DependencyValueT")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyEnumResult(Generic[DependencyValueT]):
    # ----------------------------------------------------------------------
    visibility: Optional[VisibilityModifier]            # None indicates that it isn't visible
    value: Union[DependencyValueT, "ClassStatementDependencyParserInfo"]


# ----------------------------------------------------------------------
class Dependency(Interface.Interface, Generic[DependencyValueT]):
    """Abstract base class for DependencyNode and DependencyLeaf objects"""

    # TODO: Create a wrapper, where the actual dependency can only be used within a generator, where
    #       any exceptions are decorated with all of the dependencies. Should be impossible to use the
    #       underlying dependency outside of that generator.

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def EnumDependencies() -> Generator[DependencyEnumResult[DependencyValueT], None, None]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def ResolveDependencies(self) -> Tuple[Optional[VisibilityModifier], DependencyValueT]:
        *_, last = self.EnumDependencies()

        assert last.value.__class__.__name__ != "ClassStatementDependencyParserInfo", last.value
        return last.visibility, last.value  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyNode(Dependency[DependencyValueT]):
    # ----------------------------------------------------------------------
    dependency: "ClassStatementDependencyParserInfo"
    next: Dependency[DependencyValueT]

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumDependencies(self) -> Generator[DependencyEnumResult[DependencyValueT], None, None]:
        last_result: Optional[DependencyEnumResult] = None

        for last_result in self.next.EnumDependencies():
            yield last_result

        assert last_result is not None

        yield DependencyEnumResult(last_result.visibility, self.dependency)

        assert self.dependency.visibility is not None

        if last_result.visibility is None or last_result.visibility == VisibilityModifier.private:
            visibility = None
        else:
            visibility = VisibilityModifier(
                min(last_result.visibility.value, self.dependency.visibility.value),
            )

        yield DependencyEnumResult(visibility, last_result.value)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DependencyLeaf(Dependency[DependencyValueT]):
    # ----------------------------------------------------------------------
    value: DependencyValueT

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumDependencies(self) -> Generator[DependencyEnumResult[DependencyValueT], None, None]:
        yield DependencyEnumResult(VisibilityModifier.public, self.value)
