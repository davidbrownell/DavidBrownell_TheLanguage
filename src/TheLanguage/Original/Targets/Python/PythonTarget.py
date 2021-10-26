# ----------------------------------------------------------------------
# |
# |  PythonTarget.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-19 08:22:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PythonTarget object"""

import os

import CommonEnvironment
from CommonEnvironment import FileSystem
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .PythonVisitor import PythonVisitor
    from ..Target import RootParserInfo, SemVer, Target


# ----------------------------------------------------------------------
class PythonTarget(Target):
    Name                                    = Interface.DerivedProperty("Python")  # type: ignore
    Version                                 = Interface.DerivedProperty(SemVer.coerce("0.1.0"))  # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        output_dir: str,
    ):
        self._output_dir                    = output_dir

        FileSystem.MakeDirs(self._output_dir)

    # ----------------------------------------------------------------------
    @Interface.override
    def Invoke(
        self,
        fully_qualified_name: str,
        parser_info: RootParserInfo,
    ):
        output_filename = os.path.join(self._output_dir, "{}.py".format(os.path.basename(fully_qualified_name)))

        with open(output_filename, "w") as f:
            visitor = PythonVisitor(f)

            visitor.Accept(parser_info)
