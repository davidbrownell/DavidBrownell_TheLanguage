# ----------------------------------------------------------------------
# |
# |  PythonTarget.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 10:44:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PythonTarget object"""

import os

from typing import Generator, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.Visitor import Visitor

    from ..Target import RootParserInfo, Target


# ----------------------------------------------------------------------
class PythonTarget(Target):
    name                                    = Interface.DerivedProperty("Python")               # type: ignore
    configurations                          = Interface.DerivedProperty(["Debug", "Release"])   # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_dirs: List[str],
        indent_spaces: Optional[int]=None,
    ):
        indent_spaces = indent_spaces or 4

        self._indent_spaces                             = indent_spaces
        self._source_dirs                               = source_dirs
        self._outputs: List[Target.EnumResult]          = []

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PreInvoke(
        fully_qualified_names: List[str],
    ) -> None:
        pass # Nothong to do here

    # ----------------------------------------------------------------------
    @Interface.override
    def Invoke(
        self,
        fully_qualified_name: str,
        root: RootParserInfo,
    ) -> None:
        visitor = Visitor(
            indent_spaces=self._indent_spaces,
        )

        root.Accept(visitor)

        self._outputs.append(
            Target.EnumResult.Create(
                fully_qualified_name,
                fully_qualified_name, # TODO: Fix this
                visitor.GetContent(),
            ),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def PostInvoke(
        self,
        fully_qualified_names: List[str],
    ) -> None:
        pass # TODO

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumOutputs(self) -> Generator[Target.EnumResult, None, None]:
        yield from self._outputs
