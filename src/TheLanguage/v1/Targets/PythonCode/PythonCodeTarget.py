# ----------------------------------------------------------------------
# |
# |  PythonCodeTarget.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-25 08:09:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PythonCodeTarget object"""

import os

from typing import Generator, Dict, List

import CommonEnvironment
from CommonEnvironment import FileSystem
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .VisitorImpl.Visitor import Visitor
    from ..Target import RootParserInfo, Target


# ----------------------------------------------------------------------
class PythonCodeTarget(Target):
    name                                    = Interface.DerivedProperty("PythonCode")   # type: ignore
    configurations                          = Interface.DerivedProperty([])             # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        workspaces: Dict[
            str,                            # workspace name
            Dict[
                str,                        # relative path
                RootParserInfo,
            ],
        ],
        output_dir: str,
    ):
        self._workspaces                    = workspaces
        self._output_dir                    = output_dir

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumOutputs(self) -> Generator[Target.EnumResult, None, None]:
        for workspace_name, workspace_items in self._workspaces.items():
            for relative_path, root in workspace_items.items():
                visitor = Visitor()

                root.Accept(
                    visitor,
                    include_disabled=True,
                )

                relative_name = os.path.splitext(relative_path)[0]
                relative_name, basename = os.path.split(relative_name)

                if basename in [
                    "None",
                    "True",
                    "False",
                ]:
                    basename += "Type"

                output_filename = os.path.join(self._output_dir, relative_name, "{}.py".format(basename))
                content = visitor.GetContent()

                FileSystem.MakeDirs(os.path.dirname(output_filename))

                with open(output_filename, "w") as output_file:
                    output_file.write(content)

                yield Target.EnumResult.Create(
                    os.path.join(workspace_name, relative_path),
                    output_filename,
                    content,
                )
