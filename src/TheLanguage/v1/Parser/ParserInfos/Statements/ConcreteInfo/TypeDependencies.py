# ----------------------------------------------------------------------
# |
# |  TypeDependencies.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-07 08:04:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeDependencies object"""

import itertools
import os

from typing import Any, Callable, Generator, List, Optional, Set, Tuple

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .HierarchyInfo import Dependency


# ----------------------------------------------------------------------
# BugBug: Is it possible to move this class?
@dataclass(frozen=True)
class TypeDependencies(object):
    # ----------------------------------------------------------------------
    local: List[Dependency]                 # Items defined within the class
    augmented: List[Dependency]             # Items defined in a Concept or Mixin
    inherited: List[Dependency]             # Items defined in a base or Interface

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        local: List[Dependency],
        augmented: List[Dependency],
        inherited: List[Dependency],
        get_key_func: Callable[[Dependency], Any],
        postprocess_func: Optional[
            Callable[
                [
                    List[Dependency],
                    List[Dependency],
                    List[Dependency],
                ],
                Tuple[
                    List[Dependency],
                    List[Dependency],
                    List[Dependency],
                ],
            ]
        ]=None,
    ):
        lookup = set()

        local = cls._FilterCreateList(local, get_key_func, lookup)
        augmented = cls._FilterCreateList(augmented, get_key_func, lookup)
        inherited = cls._FilterCreateList(inherited, get_key_func, lookup)

        if postprocess_func:
            local, augmented, inherited = postprocess_func(local, augmented, inherited)

        return cls(local, augmented, inherited)

    # ----------------------------------------------------------------------
    def EnumItems(self) -> Generator[Dependency, None, None]:
        yield from itertools.chain(self.local, self.augmented, self.inherited)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _FilterCreateList(
        items: List[Dependency],
        get_key_func: Callable[[Dependency], Any],
        lookup: Set[Any],
    ) -> List[Dependency]:
        results: List[Dependency] = []

        for item in items:
            key = get_key_func(item)

            if key in lookup:
                continue

            lookup.add(key)
            results.append(item)

        return results
