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
    from .VisitorImpl.Visitor import Visitor
    from ..Target import RootParserInfo, Target


# ----------------------------------------------------------------------
class PythonCodeTarget(Target):
    name                                    = Interface.DerivedProperty("PythonCode")   # type: ignore
    configurations                          = Interface.DerivedProperty([])             # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_dirs: List[str],
        output_dir: str,
    ):
        self.source_dirs                                = source_dirs
        self.output_dir                                 = output_dir

        self._outputs: List[Target.EnumResult]          = []

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PreInvoke(
        fully_qualified_names: List[str],
    ) -> None:
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def Invoke(
        self,
        fully_qualified_name: str,
        root: RootParserInfo,
    ) -> None:
        visitor = Visitor()

        root.Accept(visitor)

        output_name = os.path.splitext(fully_qualified_name)[0]

        if output_name in [
            "None",
            "True",
            "False",
        ]:
            output_name += "Type"

        self._outputs.append(
            Target.EnumResult.Create(
                fully_qualified_name,
                os.path.join(self.output_dir, "{}.py".format(output_name)),
                visitor.GetContent(),
            ),
        )

        # ----------------------------------------------------------------------
    @Interface.override
    def PostInvoke(
        self,
        fully_qualified_names: List[str],
    ) -> None:
        for output in self._outputs:
            output_dir = os.path.dirname(output.output_name)
            FileSystem.MakeDirs(output_dir)

            init_filename = os.path.join(output_dir, "__init__.py")
            if not os.path.isfile(init_filename):
                with open(init_filename, "w") as f:
                    pass

            with open(output.output_name, "w") as f:
                f.write(output.content)

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumOutputs(self) -> Generator[Target.EnumResult, None, None]:
        yield from self._outputs
