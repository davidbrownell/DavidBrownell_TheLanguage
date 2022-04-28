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
from CommonEnvironment import FileSystem
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Visitor import Visitor

    from ..Target import RootParserInfo, Target


# ----------------------------------------------------------------------
class PythonTarget(Target):
    name                                    = Interface.DerivedProperty("Python")               # type: ignore
    configurations                          = Interface.DerivedProperty(["Debug", "Release"])   # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_dirs: List[str],
        output_dir: Optional[str],
        indent_spaces: Optional[int]=None,
    ):
        indent_spaces = indent_spaces or 4

        self.source_dirs                    = source_dirs
        self.output_dir                     = output_dir

        self._indent_spaces                             = indent_spaces
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

        output_name: Optional[str] = None

        for source_dir in self.source_dirs:
            if fully_qualified_name.startswith(source_dir):
                output_name = FileSystem.TrimPath(fully_qualified_name, source_dir)
                break

        if output_name is None:
            assert self.output_dir is None, self.output_dir
            output_name = fully_qualified_name
        else:
            assert self.output_dir is not None, self.output_dir
            output_name = os.path.join(self.output_dir, output_name)

        assert output_name is not None

        self._outputs.append(
            Target.EnumResult.Create(
                fully_qualified_name,
                output_name,
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
