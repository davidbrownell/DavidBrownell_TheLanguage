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

from typing import Any, cast, Dict, List, Tuple

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

sys.stdout.write("Importing content...")
with StreamDecorator(
    sys.stdout,
).DoneManager() as dm:
    dm.stream.flush()

    with InitRelativeImports():
        from .AllGrammars import Grammar, GrammarCommentToken, LexObserver, ParseObserver
        from .Lexer.Lexer import AST, Lex, Prune

        from .Parser.Parser import (
            IntegerType,
            MiniLanguageType,
            NoneType,
            Parse,
            RootParserInfo,
            Validate,
            VariantType,
        )

        from .Targets.Python.PythonTarget import PythonTarget
        from .Targets.PythonCode.PythonCodeTarget import PythonCodeTarget


# ----------------------------------------------------------------------
inflect                                     = inflect_mod.engine()

_TARGETS                                    = {
    "Python": PythonTarget,
    "PythonCode": PythonCodeTarget,
}


# ----------------------------------------------------------------------
@CommandLine.EntryPoint()                                                   # type: ignore
@CommandLine.Constraints(                                                   # type: ignore
    target=CommandLine.EnumTypeInfo(
        list(_TARGETS.keys()),
    ),
    output_directory=CommandLine.DirectoryTypeInfo(
        ensure_exists=False,
    ),
    input_directory_or_filename=CommandLine.FilenameTypeInfo(
        match_any=True,
        arity="+",
    ),
    configuration=CommandLine.EnumTypeInfo(
        values=["Debug", "ReleaseNoOptimizations", "Release"],
        arity="?",
    ),
    max_num_threads=CommandLine.IntTypeInfo(
        min=1,
        arity="?",
    ),
    output_stream=None,
)
def Execute(
    target,
    output_directory,
    input_directory_or_filename,
    configuration="Debug",
    max_num_threads=None,
    output_stream=sys.stdout,
):
    input_directory_or_filename_items = input_directory_or_filename
    del input_directory_or_filename

    max_num_threads = 1

    with StreamDecorator(output_stream).DoneManager(
        line_prefix="",
        prefix="\nResults: ",
        suffix="\n",
    ) as dm:
        workspaces: Dict[str, List[str]] = {}
        num_files = 0

        dm.stream.write("Gathering input...")
        with dm.stream.DoneManager(
            done_suffixes=[
                lambda: "{} found".format(inflect.no("workspace", len(workspaces))),
                lambda: "{} found".format(inflect.no("file", num_files)),
            ],
        ):
            for input_directory_or_filename in input_directory_or_filename_items:
                if os.path.isfile(input_directory_or_filename):
                    dirname, basename = os.path.split(os.path.realpath(input_directory_or_filename))

                    workspaces.setdefault(dirname, []).append(basename)
                    num_files += 1

                elif os.path.isdir(input_directory_or_filename):
                    input_directory_or_filename = os.path.realpath(input_directory_or_filename)

                    relative_paths: List[str] = []

                    for filename in FileSystem.WalkFiles(
                        input_directory_or_filename,
                        include_file_extensions=[".TheLanguage", ],
                    ):
                        relative_paths.append(FileSystem.TrimPath(filename, input_directory_or_filename))


                    num_files += len(relative_paths)
                    workspaces[input_directory_or_filename] = relative_paths

                else:
                    assert False, input_directory_or_filename  # pragma: no cover

        if num_files == 0:
            return dm.result

        dm.stream.write("\nLexing...\n\n")
        with dm.stream.DoneManager() as lex_dm:
            lex_result = Lex(
                GrammarCommentToken,
                Grammar,
                workspaces,
                LexObserver(list(workspaces.keys())),
                max_num_threads=max_num_threads,
            )

            if isinstance(lex_result, list):
                for error in lex_result:
                    lex_dm.stream.write("{}\n{}\n\n".format(error.fully_qualified_name, error))  # type: ignore

                    if not str(error) or isinstance(error, AssertionError):
                        lex_dm.stream.write("{}\n\n".format(error.traceback))  # type: ignore

                lex_dm.result = -1
                return lex_dm.result

            assert lex_result is not None
            lex_result = cast(Dict[str, Dict[str, AST.Node]], lex_result)

            lex_dm.stream.write("\n")

        dm.stream.write("\nPruning...")
        with dm.stream.DoneManager():
            Prune(
                lex_result,
                max_num_threads=max_num_threads,
            )

        dm.stream.write("\nParsing...")
        with dm.stream.DoneManager() as parse_dm:
            parse_result = Parse(
                lex_result,
                ParseObserver(),
                max_num_threads=max_num_threads,
            )

            assert parse_result is not None

            for workspace, results in parse_result.items():
                for relative_path, result in results.items():
                    if isinstance(result, list):
                        for error in result:
                            parse_dm.stream.write(
                                "{} [{}]\n{}\n\n".format(
                                    os.path.join(workspace, relative_path),
                                    error.region,
                                    error,
                                ),
                            )

                        parse_dm.result = -1

            if parse_dm.result != 0:
                return parse_dm.result

            parse_result = cast(Dict[str, Dict[str, RootParserInfo]], parse_result)

        dm.stream.write("\nValidating...")
        with dm.stream.DoneManager() as validate_dm:
            configuration_values: Dict[str, Tuple[MiniLanguageType, Any]] = {
                "__architecture_bytes!": (IntegerType(), 8),
            }

            validate_result = Validate(
                parse_result,
                configuration_values,
                max_num_threads=max_num_threads,
            )

            assert validate_result is not None

            for workspace, results in validate_result.items():
                for relative_path, result in results.items():
                    if isinstance(result, list):
                        for error in result:
                            validate_dm.stream.write(
                                "{} [{}]\n{}\n\n".format(
                                    os.path.join(workspace, relative_path),
                                    error.region,
                                    error,
                                ),
                            )

                        validate_dm.result = -1

            if validate_dm.result != 0:
                return validate_dm.result

            validate_result = parse_result

        dm.stream.write("\nGenerating output...")
        with dm.stream.DoneManager() as target_dm:
            target = _TARGETS[target](validate_result, output_directory)

            for output in target.EnumOutputs():
                target_dm.stream.write(
                    "{:<130} -> {}\n".format(
                        output.fully_qualified_name,
                        output.output_name,
                    ),
                )

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
