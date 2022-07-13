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

from typing import Any, Callable, Generator, List, Optional, Set, Tuple

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
@dataclass(frozen=True)
class ClassContent(object):
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

        local = cls._FilterList(local, get_key_func, lookup)
        augmented = cls._FilterList(augmented, get_key_func, lookup)
        inherited = cls._FilterList(inherited, get_key_func, lookup)

        if postprocess_func:
            local, augmented, inherited = postprocess_func(local, augmented, inherited)

        return cls(local, augmented, inherited)

    # ----------------------------------------------------------------------
    def EnumDependencies(self) -> Generator[Dependency, None, None]:
        yield from itertools.chain(self.local, self.augmented, self.inherited)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _FilterList(
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
