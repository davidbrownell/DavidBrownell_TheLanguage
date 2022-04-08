# ----------------------------------------------------------------------
# |
# |  __main__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 09:36:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Compiles TheLanguage source files"""

import os
import sys
import threading

import inflect as inflect_mod

import CommonEnvironment
from CommonEnvironment import CommandLine
from CommonEnvironment import FileSystem
from CommonEnvironment.StreamDecorator import StreamDecorator

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
inflect                                     = inflect_mod.engine()


# ----------------------------------------------------------------------
@CommandLine.EntryPoint()                                                   # type: ignore
@CommandLine.Constraints(                                                   # type: ignore
    input_directory_or_filename=CommandLine.FilenameTypeInfo(
        match_any=True,
    ),
    output_directory=CommandLine.DirectoryTypeInfo(
        ensure_exists=False,
    ),
    configuration=CommandLine.EnumTypeInfo(
        values=["Debug", "ReleaseNoOptimizations", "Release"],
        arity="?",
    ),
    output_stream=None,
)
def Execute(
    input_directory_or_filename,
    output_directory,
    configuration="Debug",
    output_stream=sys.stdout,
):
    with StreamDecorator(output_stream).DoneManager(
        line_prefix="",
        prefix="\nResults: ",
        suffix="\n",
    ) as dm:
        filenames = []

        dm.stream.write("Gathering input...")
        with dm.stream.DoneManager(
            done_suffix=lambda: "{} found".format(inflect.no("file", len(filenames))),
        ):
            if os.path.isfile(input_directory_or_filename):
                filenames.append(input_directory_or_filename)
                input_dir = os.path.dirname(input_directory_or_filename)
            elif os.path.isdir(input_directory_or_filename):
                filenames = list(FileSystem.WalkFiles(
                    input_directory_or_filename,
                    include_file_extensions=[".TheLanguage"],
                ))

                input_dir = input_directory_or_filename
            else:
                assert False, input_directory_or_filename  # pragma: no cover

        if not filenames:
            return dm.result

        dm.stream.write("Importing content...")
        with dm.stream.DoneManager():
            with InitRelativeImports():
                from .Lexer.Grammar.All import GrammarPhrases

        cancellation_event = threading.Event()
        configurations = Configurations[configuration]

        return dm.result

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        sys.exit(
            CommandLine.Main()
        )
    except KeyboardInterrupt:
        pass
