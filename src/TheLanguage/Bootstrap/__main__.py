# ----------------------------------------------------------------------
# |
# |  __main__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-27 12:42:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
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
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import CommandLine
from CommonEnvironment import FileSystem
from CommonEnvironment.StreamDecorator import StreamDecorator

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

inflect                                     = inflect_mod.engine()


# ----------------------------------------------------------------------
@CommandLine.EntryPoint
@CommandLine.Constraints(
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
                filenames = [input_directory_or_filename]
                input_dir = os.path.dirname(input_directory_or_filename)

            elif os.path.isdir(input_directory_or_filename):
                filenames = list(FileSystem.WalkFiles(
                    input_directory_or_filename,
                    include_file_extensions=[".TheLanguage"],
                ))

                filenames = [ r"C:\Code\v3\DavidBrownell\TheLanguage\src\TheLanguage\Bootstrap\TheLanguage\Lexer\Components\NormalizedIterator.TheLanguage", ] # BugBug
                input_dir = input_directory_or_filename
            else:
                assert False, input_directory_or_filename  # pragma: no cover

        if not filenames:
            return dm.result

        dm.stream.write("Importing content...")
        with dm.stream.DoneManager():
            sys.path.insert(0, _script_dir)
            with CallOnExit(lambda: sys.path.pop(0)):
                from AllGrammars import Configurations, Lex, Prune, Parse, InvokeTarget, Validate
                from Lexer.TranslationUnitLexer import SyntaxInvalidError
                from Targets.Python.PythonTarget import PythonTarget

        cancellation_event = threading.Event()
        configuration = Configurations[configuration]
        target = PythonTarget(input_dir, output_directory)

        # ----------------------------------------------------------------------
        def ProcessExceptions(dm, exceptions) -> int:
            for ex in exceptions:
                if hasattr(ex, "FullyQualifiedName"):
                    dm.stream.write("*** {} ***\n\n".format(ex.FullyQualifiedName))

                dm.stream.write(str(ex))

                if not isinstance(ex, SyntaxInvalidError):
                    if hasattr(ex, "Line") and hasattr(ex, "Column"):
                        dm.stream.write(" [Ln {}, Col {}]".format(ex.Line, ex.Column))
                    elif hasattr(ex, "Region"):
                        dm.stream.write(" {}".format(ex.Region.ToString()))

                    dm.stream.write("\n")

                    if hasattr(ex, "Traceback"):
                        dm.stream.write(ex.Traceback)
                        dm.stream.write("\n")

            dm.result = -1
            return dm.result

        # ----------------------------------------------------------------------

        max_num_threads = 1 # TODO: There is a problem when there are multiple threads

        dm.stream.write("Lexing...")
        with dm.stream.DoneManager() as lex_dm:
            result = Lex(
                cancellation_event,
                configuration,
                target.Name,
                filenames,
                [_script_dir],
                max_num_threads=max_num_threads,
            )

            if isinstance(result, list):
                return ProcessExceptions(lex_dm, result)

            assert result is not None

        dm.stream.write("Pruning...")
        with dm.stream.DoneManager():
            Prune(
                result,
                max_num_threads=max_num_threads,
            )

        dm.stream.write("Parsing...")
        with dm.stream.DoneManager() as parse_dm:
            result = Parse(
                cancellation_event,
                result,
                max_num_threads=max_num_threads,
            )
            if isinstance(result, list):
                return ProcessExceptions(parse_dm, result)

            assert result is not None

        dm.stream.write("Validating...")
        with dm.stream.DoneManager() as validate_dm:
            result = Validate(
                cancellation_event,
                result,
                max_num_threads=max_num_threads,
            )
            if isinstance(result, list):
                return ProcessExceptions(validate_dm, result)

            assert result is not None

        dm.stream.write("Invoking Target...")
        with dm.stream.DoneManager() as target_dm:
            result = InvokeTarget(
                cancellation_event,
                result,
                target,
                max_num_threads=max_num_threads,
            )
            if isinstance(result, list):
                return ProcessExceptions(target_dm, result)

            assert result is not None

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
