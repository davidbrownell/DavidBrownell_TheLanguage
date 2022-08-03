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

from typing import Generator, Dict, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Visitor import Visitor

    from ..Target import RootStatementParserInfo, Target


# ----------------------------------------------------------------------
class PythonTarget(Target):
    name                                    = Interface.DerivedProperty("Python")               # type: ignore
    configurations                          = Interface.DerivedProperty(["Debug", "Release"])   # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        workspaces: Dict[
            str,
            Dict[
                str,
                RootStatementParserInfo,
            ],
        ],
        output_dir: Optional[str],
        indent_spaces: Optional[int]=None,
    ):
        indent_spaces = indent_spaces or 4

        self._workspaces                    = workspaces
        self._output_dir                    = output_dir

        self._indent_spaces                             = indent_spaces

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumOutputs(self) -> Generator[Target.EnumResult, None, None]:
        for workspace_name, workspace_items in self._workspaces.items():
            for relative_path, root in workspace_items.items():
                visitor = Visitor(
                    indent_spaces=self._indent_spaces,
                )

                root.Accept(
                    visitor,
                    include_disabled=True,
                )

                yield Target.EnumResult.Create(
                    os.path.join(workspace_name, relative_path),
                    os.path.join(self._output_dir or "", relative_path),
                    visitor.GetContent(),
                )
