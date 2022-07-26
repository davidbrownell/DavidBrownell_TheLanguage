# ----------------------------------------------------------------------
# |
# |  ClassContent.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-13 08:06:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassContent object"""

import itertools
import os

from typing import Any, Callable, Generator, Generic, List, Optional, Set, Tuple, TypeVar

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Dependency import Dependency


# ----------------------------------------------------------------------
ClassContentT                               = TypeVar("ClassContentT")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassContent(Generic[ClassContentT]):
    # ----------------------------------------------------------------------
    local: List[Dependency[ClassContentT]]              # Items defined within the class
    augmented: List[Dependency[ClassContentT]]          # Items defined in a Concept or Mixin
    inherited: List[Dependency[ClassContentT]]          # Items defined in a base or Interface

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        local: List[Dependency[ClassContentT]],
        augmented: List[Dependency[ClassContentT]],
        inherited: List[Dependency[ClassContentT]],
        get_key_func: Callable[[ClassContentT], Any],
        postprocess_func: Optional[
            Callable[
                [
                    List[Dependency[ClassContentT]],
                    List[Dependency[ClassContentT]],
                    List[Dependency[ClassContentT]],
                ],
                Tuple[
                    List[Dependency[ClassContentT]],
                    List[Dependency[ClassContentT]],
                    List[Dependency[ClassContentT]],
                ],
            ]
        ]=None,
    ):
        lookup = set()

        local = cls._FilterList(local, get_key_func, lookup)
        augmented = cls._FilterList(augmented, get_key_func, lookup)
        inherited = cls._FilterList(inherited, get_key_func, lookup)

        if postprocess_func:
            local, augmented, inherited = postprocess_func(local, augmented, inherited)

        return cls(local, augmented, inherited)

    # ----------------------------------------------------------------------
    def EnumContent(self) -> Generator[Dependency, None, None]:
        yield from itertools.chain(self.local, self.augmented, self.inherited)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _FilterList(
        dependencies: List[Dependency[ClassContentT]],
        get_key_func: Callable[[ClassContentT], Any],
        lookup: Set[Any],
    ) -> List[Dependency[ClassContentT]]:
        results: List[Dependency[ClassContentT]] = []

        for dependency in dependencies:
            resolved_info = dependency.ResolveDependencies()[1]

            key = get_key_func(resolved_info)

            if key in lookup:
                continue

            lookup.add(key)

            results.append(dependency)

        return results
