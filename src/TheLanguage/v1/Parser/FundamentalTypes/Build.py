# ----------------------------------------------------------------------
# |
# |  Build.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-25 07:56:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Builds content in this directory; output is generated in ./GeneratedCode"""

# CONFIGURATIONS
# --------------
# If configurations are supported, search for and uncomment all sections with
# the header/prefix "<<<Configuration Support>>>"

# OUTPUT DIRECTORY
# ----------------
# If output directories are required, search for and uncomment all sections with
# the header/prefix "<<<Output Directory Support>>>"


# ----------------------------------------------------------------------
import os
import sys

import CommonEnvironment
from CommonEnvironment import BuildImpl
from CommonEnvironment import CommandLine
from CommonEnvironment import FileSystem
from CommonEnvironment import Process
from CommonEnvironment.StreamDecorator import StreamDecorator

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

_OUTPUT_DIR                                 = os.path.join(_script_dir, "GeneratedCode")


# ----------------------------------------------------------------------
@CommandLine.EntryPoint
@CommandLine.Constraints(                   # type: ignore
    output_stream=None,
)
def Build(
    verbose=False,
    output_stream=sys.stdout,
):
    with StreamDecorator(output_stream).DoneManager(
        line_prefix="",
        prefix="\nResults: ",
        suffix="\n",
    ) as dm:
        main_script = os.path.realpath(os.path.join(_script_dir, "..", "..", "__main__.py"))
        assert os.path.isfile(main_script), main_script

        command_line = 'python "{script}" "{input_dir}" "{output_dir}" PythonCode'.format(
            script=os.path.dirname(main_script),
            input_dir=os.path.join(_script_dir, "TheLanguage"),
            output_dir=os.path.join(_script_dir, "GeneratedCode"),
        )

        if verbose:
            dm.stream.write("{}\n\n".format(command_line))

        dm.result = Process.Execute(command_line, dm.stream)

        return dm.result


# ----------------------------------------------------------------------
@CommandLine.EntryPoint
@CommandLine.Constraints(                   # type: ignore
    output_stream=None,
)
def Clean(
    output_stream=sys.stdout,
):
    with StreamDecorator(output_stream).DoneManager(
        line_prefix="",
        prefix="\nResults: ",
        suffix="\n",
    ) as dm:
        if not os.path.isdir(_OUTPUT_DIR):
            dm.stream.write("The output directory '{}' does not exist.\n".format(_OUTPUT_DIR))
            dm.result = 1
        else:
            dm.stream.write("Removing '{}'...".format(_OUTPUT_DIR))
            with dm.stream.DoneManager():
                FileSystem.RemoveTree(_OUTPUT_DIR)

        return dm.result


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        sys.exit(
            BuildImpl.Main(
                BuildImpl.Configuration(
                    name="Fundamental Types",
                    requires_output_dir=False,
                ),
            ),
        )
    except KeyboardInterrupt:
        pass
