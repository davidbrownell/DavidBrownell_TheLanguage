# ----------------------------------------------------------------------
# |
# |  ImportStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-17 09:37:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ImportStatement.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import PatchAndExecute
    from ..ImportStatement import *


# ----------------------------------------------------------------------
class TestStandard(object):
    # In _script_dir
    _filename                               = os.path.join(_script_dir, "filename.TheLanguage")
    _file1                                  = os.path.join(_script_dir, "File1.TheLanguage")

    # In _script_dir/../..
    _file2                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "File2.TheLanguage"))
    _file3                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "Dir1", "File3.TheLanguage"))

    # In _script_dir/dir2/dir3
    _file4                                  = os.path.join(_script_dir, "Dir2", "Dir3", "File4.TheLanguage")

    _root1                                  = os.path.realpath(os.path.join(_script_dir, ".."))
    _root2                                  = os.path.realpath(os.path.join(_script_dir, "..", ".."))
    _root3                                  = os.path.join(_script_dir, "Dir1")

    _root_file1                             = os.path.join(_root1, "File1.TheLanguage")
    _root_file2                             = os.path.join(_root2, "File2.TheLanguage")
    _root_file3                             = os.path.join(_root3, "File3.TheLanguage")
    _root_file4                             = os.path.join(_root3, "Dir1", "Dir2", "File4.TheLanguage")

    # ----------------------------------------------------------------------
    def test_SingleRelativeDirectory(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from . import File1
                from . import File1 as File1Decorated

                from ... import File2
                from ... import File2 as File2Decorated

                from ...Dir1 import File3
                from ...Dir1 import File3 as File3Decorated

                from .Dir2.Dir3 import File4
                from .Dir2.Dir3 import File4 as File4Decorated
                """,
            ),
            self._file1 : "pass",
            self._file2 : "pass",
            self._file3 : "pass",
            self._file4 : "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 6 -> 1, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 8 -> 1, 14]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='File1'>>> ws:(13, 14) [1, 15 -> 1, 20]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<19, 20>> ws:None [1, 20 -> 2, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(20, 24), match='from'>>> ws:None [2, 1 -> 2, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='.'>>> ws:(24, 25) [2, 6 -> 2, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(27, 33), match='import'>>> ws:(26, 27) [2, 8 -> 2, 14]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='File1'>>> ws:(33, 34) [2, 15 -> 2, 20]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(40, 42), match='as'>>> ws:(39, 40) [2, 21 -> 2, 23]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(43, 57), match='File1Decorated'>>> ws:(42, 43) [2, 24 -> 2, 38]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<57, 59>> ws:None [2, 38 -> 4, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(59, 63), match='from'>>> ws:None [4, 1 -> 4, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(64, 67), match='...'>>> ws:(63, 64) [4, 6 -> 4, 9]
                            'import' <<Regex: <_sre.SRE_Match object; span=(68, 74), match='import'>>> ws:(67, 68) [4, 10 -> 4, 16]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(75, 80), match='File2'>>> ws:(74, 75) [4, 17 -> 4, 22]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<80, 81>> ws:None [4, 22 -> 5, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(81, 85), match='from'>>> ws:None [5, 1 -> 5, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(86, 89), match='...'>>> ws:(85, 86) [5, 6 -> 5, 9]
                            'import' <<Regex: <_sre.SRE_Match object; span=(90, 96), match='import'>>> ws:(89, 90) [5, 10 -> 5, 16]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(97, 102), match='File2'>>> ws:(96, 97) [5, 17 -> 5, 22]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(103, 105), match='as'>>> ws:(102, 103) [5, 23 -> 5, 25]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(106, 120), match='File2Decorated'>>> ws:(105, 106) [5, 26 -> 5, 40]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<120, 122>> ws:None [5, 40 -> 7, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(122, 126), match='from'>>> ws:None [7, 1 -> 7, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(127, 134), match='...Dir1'>>> ws:(126, 127) [7, 6 -> 7, 13]
                            'import' <<Regex: <_sre.SRE_Match object; span=(135, 141), match='import'>>> ws:(134, 135) [7, 14 -> 7, 20]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(142, 147), match='File3'>>> ws:(141, 142) [7, 21 -> 7, 26]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<147, 148>> ws:None [7, 26 -> 8, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(148, 152), match='from'>>> ws:None [8, 1 -> 8, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(153, 160), match='...Dir1'>>> ws:(152, 153) [8, 6 -> 8, 13]
                            'import' <<Regex: <_sre.SRE_Match object; span=(161, 167), match='import'>>> ws:(160, 161) [8, 14 -> 8, 20]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(168, 173), match='File3'>>> ws:(167, 168) [8, 21 -> 8, 26]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(174, 176), match='as'>>> ws:(173, 174) [8, 27 -> 8, 29]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(177, 191), match='File3Decorated'>>> ws:(176, 177) [8, 30 -> 8, 44]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<191, 193>> ws:None [8, 44 -> 10, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(193, 197), match='from'>>> ws:None [10, 1 -> 10, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(198, 208), match='.Dir2.Dir3'>>> ws:(197, 198) [10, 6 -> 10, 16]
                            'import' <<Regex: <_sre.SRE_Match object; span=(209, 215), match='import'>>> ws:(208, 209) [10, 17 -> 10, 23]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(216, 221), match='File4'>>> ws:(215, 216) [10, 24 -> 10, 29]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<221, 222>> ws:None [10, 29 -> 11, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(222, 226), match='from'>>> ws:None [11, 1 -> 11, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(227, 237), match='.Dir2.Dir3'>>> ws:(226, 227) [11, 6 -> 11, 16]
                            'import' <<Regex: <_sre.SRE_Match object; span=(238, 244), match='import'>>> ws:(237, 238) [11, 17 -> 11, 23]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(245, 250), match='File4'>>> ws:(244, 245) [11, 24 -> 11, 29]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(251, 253), match='as'>>> ws:(250, 251) [11, 30 -> 11, 32]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(254, 268), match='File4Decorated'>>> ws:(253, 254) [11, 33 -> 11, 47]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<268, 269>> ws:None [11, 47 -> 12, 1]
            """,
        )

        assert len(result.Children) == 8

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[0].Children[0].Children[0].source_filename == self._file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "File1" : "File1",
        }

        assert result.Children[1].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[1].Children[0].Children[0].source_filename == self._file1
        assert result.Children[1].Children[0].Children[0].import_items == {
            "File1" : "File1Decorated",
        }

        assert result.Children[2].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[2].Children[0].Children[0].source_filename == self._file2
        assert result.Children[2].Children[0].Children[0].import_items == {
            "File2" : "File2",
        }

        assert result.Children[3].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[3].Children[0].Children[0].source_filename == self._file2
        assert result.Children[3].Children[0].Children[0].import_items == {
            "File2" : "File2Decorated",
        }

        assert result.Children[4].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[4].Children[0].Children[0].source_filename == self._file3
        assert result.Children[4].Children[0].Children[0].import_items == {
            "File3" : "File3",
        }

        assert result.Children[5].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[5].Children[0].Children[0].source_filename == self._file3
        assert result.Children[5].Children[0].Children[0].import_items == {
            "File3" : "File3Decorated",
        }

        assert result.Children[6].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[6].Children[0].Children[0].source_filename == self._file4
        assert result.Children[6].Children[0].Children[0].import_items == {
            "File4" : "File4",
        }

        assert result.Children[7].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[7].Children[0].Children[0].source_filename == self._file4
        assert result.Children[7].Children[0].Children[0].import_items == {
            "File4" : "File4Decorated",
        }

    # ----------------------------------------------------------------------
    def test_SingleRelativeFilename(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from .File1 import obj1
                from .File1 import obj1 as obj1Decorated

                from ...File2 import obj2
                from ...File2 import obj2 as obj2Decorated

                from ...Dir1.File3 import obj3
                from ...Dir1.File3 import obj3 as obj3Decorated

                from .Dir2.Dir3.File4 import obj4
                from .Dir2.Dir3.File4 import obj4 as obj4Decorated
                """,
            ),
            self._file1 : "pass",
            self._file2 : "pass",
            self._file3 : "pass",
            self._file4 : "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 11), match='.File1'>>> ws:(4, 5) [1, 6 -> 1, 12]
                            'import' <<Regex: <_sre.SRE_Match object; span=(12, 18), match='import'>>> ws:(11, 12) [1, 13 -> 1, 19]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:(18, 19) [1, 20 -> 1, 24]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<23, 24>> ws:None [1, 24 -> 2, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(24, 28), match='from'>>> ws:None [2, 1 -> 2, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(29, 35), match='.File1'>>> ws:(28, 29) [2, 6 -> 2, 12]
                            'import' <<Regex: <_sre.SRE_Match object; span=(36, 42), match='import'>>> ws:(35, 36) [2, 13 -> 2, 19]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(43, 47), match='obj1'>>> ws:(42, 43) [2, 20 -> 2, 24]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(48, 50), match='as'>>> ws:(47, 48) [2, 25 -> 2, 27]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(51, 64), match='obj1Decorated'>>> ws:(50, 51) [2, 28 -> 2, 41]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<64, 66>> ws:None [2, 41 -> 4, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(66, 70), match='from'>>> ws:None [4, 1 -> 4, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(71, 79), match='...File2'>>> ws:(70, 71) [4, 6 -> 4, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(80, 86), match='import'>>> ws:(79, 80) [4, 15 -> 4, 21]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(87, 91), match='obj2'>>> ws:(86, 87) [4, 22 -> 4, 26]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<91, 92>> ws:None [4, 26 -> 5, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(92, 96), match='from'>>> ws:None [5, 1 -> 5, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(97, 105), match='...File2'>>> ws:(96, 97) [5, 6 -> 5, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(106, 112), match='import'>>> ws:(105, 106) [5, 15 -> 5, 21]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(113, 117), match='obj2'>>> ws:(112, 113) [5, 22 -> 5, 26]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(118, 120), match='as'>>> ws:(117, 118) [5, 27 -> 5, 29]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(121, 134), match='obj2Decorated'>>> ws:(120, 121) [5, 30 -> 5, 43]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<134, 136>> ws:None [5, 43 -> 7, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(136, 140), match='from'>>> ws:None [7, 1 -> 7, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(141, 154), match='...Dir1.File3'>>> ws:(140, 141) [7, 6 -> 7, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(155, 161), match='import'>>> ws:(154, 155) [7, 20 -> 7, 26]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(162, 166), match='obj3'>>> ws:(161, 162) [7, 27 -> 7, 31]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<166, 167>> ws:None [7, 31 -> 8, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(167, 171), match='from'>>> ws:None [8, 1 -> 8, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(172, 185), match='...Dir1.File3'>>> ws:(171, 172) [8, 6 -> 8, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(186, 192), match='import'>>> ws:(185, 186) [8, 20 -> 8, 26]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(193, 197), match='obj3'>>> ws:(192, 193) [8, 27 -> 8, 31]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(198, 200), match='as'>>> ws:(197, 198) [8, 32 -> 8, 34]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(201, 214), match='obj3Decorated'>>> ws:(200, 201) [8, 35 -> 8, 48]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<214, 216>> ws:None [8, 48 -> 10, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(216, 220), match='from'>>> ws:None [10, 1 -> 10, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(221, 237), match='.Dir2.Dir3.File4'>>> ws:(220, 221) [10, 6 -> 10, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(238, 244), match='import'>>> ws:(237, 238) [10, 23 -> 10, 29]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(245, 249), match='obj4'>>> ws:(244, 245) [10, 30 -> 10, 34]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<249, 250>> ws:None [10, 34 -> 11, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(250, 254), match='from'>>> ws:None [11, 1 -> 11, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(255, 271), match='.Dir2.Dir3.File4'>>> ws:(254, 255) [11, 6 -> 11, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(272, 278), match='import'>>> ws:(271, 272) [11, 23 -> 11, 29]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(279, 283), match='obj4'>>> ws:(278, 279) [11, 30 -> 11, 34]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(284, 286), match='as'>>> ws:(283, 284) [11, 35 -> 11, 37]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(287, 300), match='obj4Decorated'>>> ws:(286, 287) [11, 38 -> 11, 51]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<300, 301>> ws:None [11, 51 -> 12, 1]
            """,
        )

        assert len(result.Children) == 8

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[0].Children[0].Children[0].source_filename == self._file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "obj1" : "obj1",
        }

        assert result.Children[1].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[1].Children[0].Children[0].source_filename == self._file1
        assert result.Children[1].Children[0].Children[0].import_items == {
            "obj1" : "obj1Decorated",
        }

        assert result.Children[2].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[2].Children[0].Children[0].source_filename == self._file2
        assert result.Children[2].Children[0].Children[0].import_items == {
            "obj2" : "obj2",
        }

        assert result.Children[3].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[3].Children[0].Children[0].source_filename == self._file2
        assert result.Children[3].Children[0].Children[0].import_items == {
            "obj2" : "obj2Decorated",
        }

        assert result.Children[4].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[4].Children[0].Children[0].source_filename == self._file3
        assert result.Children[4].Children[0].Children[0].import_items == {
            "obj3" : "obj3",
        }

        assert result.Children[5].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[5].Children[0].Children[0].source_filename == self._file3
        assert result.Children[5].Children[0].Children[0].import_items == {
            "obj3" : "obj3Decorated",
        }

        assert result.Children[6].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[6].Children[0].Children[0].source_filename == self._file4
        assert result.Children[6].Children[0].Children[0].import_items == {
            "obj4" : "obj4",
        }

        assert result.Children[7].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[7].Children[0].Children[0].source_filename == self._file4
        assert result.Children[7].Children[0].Children[0].import_items == {
            "obj4" : "obj4Decorated",
        }

    # ----------------------------------------------------------------------
    def test_SingleAbsoluteFilename(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import obj1
                from File1 import obj1 as obj1Decorated

                from File2 import obj2
                from File2 import obj2 as obj2Decorated

                from File3 import obj3
                from File3 import obj3 as obj3Decorated

                from Dir1.Dir2.File4 import obj4
                from Dir1.Dir2.File4 import obj4 as obj4Decorated
                """,
            ),
            self._root_file1 : "pass",
            self._root_file2 : "pass",
            self._root_file3 : "pass",
            self._root_file4 : "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [
                self._root1,
                self._root2,
                self._root3,
            ],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<22, 23>> ws:None [1, 23 -> 2, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(23, 27), match='from'>>> ws:None [2, 1 -> 2, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(28, 33), match='File1'>>> ws:(27, 28) [2, 6 -> 2, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(34, 40), match='import'>>> ws:(33, 34) [2, 12 -> 2, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='obj1'>>> ws:(40, 41) [2, 19 -> 2, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(46, 48), match='as'>>> ws:(45, 46) [2, 24 -> 2, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(49, 62), match='obj1Decorated'>>> ws:(48, 49) [2, 27 -> 2, 40]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<62, 64>> ws:None [2, 40 -> 4, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(64, 68), match='from'>>> ws:None [4, 1 -> 4, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(69, 74), match='File2'>>> ws:(68, 69) [4, 6 -> 4, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(75, 81), match='import'>>> ws:(74, 75) [4, 12 -> 4, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(82, 86), match='obj2'>>> ws:(81, 82) [4, 19 -> 4, 23]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<86, 87>> ws:None [4, 23 -> 5, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(87, 91), match='from'>>> ws:None [5, 1 -> 5, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(92, 97), match='File2'>>> ws:(91, 92) [5, 6 -> 5, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(98, 104), match='import'>>> ws:(97, 98) [5, 12 -> 5, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(105, 109), match='obj2'>>> ws:(104, 105) [5, 19 -> 5, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(110, 112), match='as'>>> ws:(109, 110) [5, 24 -> 5, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(113, 126), match='obj2Decorated'>>> ws:(112, 113) [5, 27 -> 5, 40]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<126, 128>> ws:None [5, 40 -> 7, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(128, 132), match='from'>>> ws:None [7, 1 -> 7, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(133, 138), match='File3'>>> ws:(132, 133) [7, 6 -> 7, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(139, 145), match='import'>>> ws:(138, 139) [7, 12 -> 7, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(146, 150), match='obj3'>>> ws:(145, 146) [7, 19 -> 7, 23]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<150, 151>> ws:None [7, 23 -> 8, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(151, 155), match='from'>>> ws:None [8, 1 -> 8, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(156, 161), match='File3'>>> ws:(155, 156) [8, 6 -> 8, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(162, 168), match='import'>>> ws:(161, 162) [8, 12 -> 8, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(169, 173), match='obj3'>>> ws:(168, 169) [8, 19 -> 8, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(174, 176), match='as'>>> ws:(173, 174) [8, 24 -> 8, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(177, 190), match='obj3Decorated'>>> ws:(176, 177) [8, 27 -> 8, 40]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<190, 192>> ws:None [8, 40 -> 10, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(192, 196), match='from'>>> ws:None [10, 1 -> 10, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(197, 212), match='Dir1.Dir2.File4'>>> ws:(196, 197) [10, 6 -> 10, 21]
                            'import' <<Regex: <_sre.SRE_Match object; span=(213, 219), match='import'>>> ws:(212, 213) [10, 22 -> 10, 28]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(220, 224), match='obj4'>>> ws:(219, 220) [10, 29 -> 10, 33]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<224, 225>> ws:None [10, 33 -> 11, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(225, 229), match='from'>>> ws:None [11, 1 -> 11, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(230, 245), match='Dir1.Dir2.File4'>>> ws:(229, 230) [11, 6 -> 11, 21]
                            'import' <<Regex: <_sre.SRE_Match object; span=(246, 252), match='import'>>> ws:(245, 246) [11, 22 -> 11, 28]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        Sequence: [<name>, 'as', <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(253, 257), match='obj4'>>> ws:(252, 253) [11, 29 -> 11, 33]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(258, 260), match='as'>>> ws:(257, 258) [11, 34 -> 11, 36]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(261, 274), match='obj4Decorated'>>> ws:(260, 261) [11, 37 -> 11, 50]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<274, 275>> ws:None [11, 50 -> 12, 1]
            """,
        )

        assert len(result.Children) == 8

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[0].Children[0].Children[0].source_filename == self._root_file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "obj1" : "obj1",
        }

        assert result.Children[1].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[1].Children[0].Children[0].source_filename == self._root_file1
        assert result.Children[1].Children[0].Children[0].import_items == {
            "obj1" : "obj1Decorated",
        }

        assert result.Children[2].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[2].Children[0].Children[0].source_filename == self._root_file2
        assert result.Children[2].Children[0].Children[0].import_items == {
            "obj2" : "obj2",
        }

        assert result.Children[3].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[3].Children[0].Children[0].source_filename == self._root_file2
        assert result.Children[3].Children[0].Children[0].import_items == {
            "obj2" : "obj2Decorated",
        }

        assert result.Children[4].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[4].Children[0].Children[0].source_filename == self._root_file3
        assert result.Children[4].Children[0].Children[0].import_items == {
            "obj3" : "obj3",
        }

        assert result.Children[5].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[5].Children[0].Children[0].source_filename == self._root_file3
        assert result.Children[5].Children[0].Children[0].import_items == {
            "obj3" : "obj3Decorated",
        }

        assert result.Children[6].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[6].Children[0].Children[0].source_filename == self._root_file4
        assert result.Children[6].Children[0].Children[0].import_items == {
            "obj4" : "obj4",
        }

        assert result.Children[7].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[7].Children[0].Children[0].source_filename == self._root_file4
        assert result.Children[7].Children[0].Children[0].import_items == {
            "obj4" : "obj4Decorated",
        }

    # ----------------------------------------------------------------------
    def test_MultipleSingleLine(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import obj1, obj2 as obj2Decorated, obj3 as obj3Decorated, obj4
                """,
            ),
            self._root_file1 : "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=','>>> ws:None [1, 23 -> 1, 24]
                                            Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                Sequence: [<name>, 'as', <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 28), match='obj2'>>> ws:(23, 24) [1, 25 -> 1, 29]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(29, 31), match='as'>>> ws:(28, 29) [1, 30 -> 1, 32]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(32, 45), match='obj2Decorated'>>> ws:(31, 32) [1, 33 -> 1, 46]
                                        Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [1, 46 -> 1, 47]
                                            Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                Sequence: [<name>, 'as', <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(47, 51), match='obj3'>>> ws:(46, 47) [1, 48 -> 1, 52]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(52, 54), match='as'>>> ws:(51, 52) [1, 53 -> 1, 55]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(55, 68), match='obj3Decorated'>>> ws:(54, 55) [1, 56 -> 1, 69]
                                        Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(68, 69), match=','>>> ws:None [1, 69 -> 1, 70]
                                            Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(70, 74), match='obj4'>>> ws:(69, 70) [1, 71 -> 1, 75]
                                    Repeat: (',', 0, 1)
                                        <No Children>
                            Newline+ <<74, 75>> ws:None [1, 75 -> 2, 1]
            """,
        )

        assert len(result.Children) == 1

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[0].Children[0].Children[0].source_filename == self._root_file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "obj1" : "obj1",
            "obj2" : "obj2Decorated",
            "obj3" : "obj3Decorated",
            "obj4" : "obj4",
        }

    # ----------------------------------------------------------------------
    def test_Grouping(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import (obj1, obj2 as obj2Decorated)

                from ...File2 import (
                    obj3 as obj3Decorated,
                    obj4,

                        obj5 as obj5Decorated,

                            obj6
                )
                """,
            ),
            self._root_file1 : "pass",
            self._file2: "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Grouped
                                    '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:(17, 18) [1, 19 -> 1, 20]
                                    Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                        Or: {Sequence: [<name>, 'as', <name>], <name>}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:None [1, 20 -> 1, 24]
                                        Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                            Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                                ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                                Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                    Sequence: [<name>, 'as', <name>]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='obj2'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                                        'as' <<Regex: <_sre.SRE_Match object; span=(30, 32), match='as'>>> ws:(29, 30) [1, 31 -> 1, 33]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(33, 46), match='obj2Decorated'>>> ws:(32, 33) [1, 34 -> 1, 47]
                                        Repeat: (',', 0, 1)
                                            <No Children>
                                    ')' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=')'>>> ws:None [1, 47 -> 1, 48]
                            Newline+ <<47, 49>> ws:None [1, 48 -> 3, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(49, 53), match='from'>>> ws:None [3, 1 -> 3, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(54, 62), match='...File2'>>> ws:(53, 54) [3, 6 -> 3, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(63, 69), match='import'>>> ws:(62, 63) [3, 15 -> 3, 21]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Grouped
                                    '(' <<Regex: <_sre.SRE_Match object; span=(70, 71), match='('>>> ws:(69, 70) [3, 22 -> 3, 23]
                                    Newline+ <<71, 72>> ws:None !Ignored! [3, 23 -> 4, 1]
                                    Indent <<72, 76, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                                    Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                        Or: {Sequence: [<name>, 'as', <name>], <name>}
                                            Sequence: [<name>, 'as', <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(76, 80), match='obj3'>>> ws:None [4, 5 -> 4, 9]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(81, 83), match='as'>>> ws:(80, 81) [4, 10 -> 4, 12]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(84, 97), match='obj3Decorated'>>> ws:(83, 84) [4, 13 -> 4, 26]
                                        Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                            Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                                ',' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=','>>> ws:None [4, 26 -> 4, 27]
                                                Newline+ <<98, 99>> ws:None !Ignored! [4, 27 -> 5, 1]
                                                Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(103, 107), match='obj4'>>> ws:None [5, 5 -> 5, 9]
                                            Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                                ',' <<Regex: <_sre.SRE_Match object; span=(107, 108), match=','>>> ws:None [5, 9 -> 5, 10]
                                                Newline+ <<108, 110>> ws:None !Ignored! [5, 10 -> 7, 1]
                                                Indent <<110, 118, (8)>> ws:None !Ignored! [7, 1 -> 7, 9]
                                                Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                    Sequence: [<name>, 'as', <name>]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(118, 122), match='obj5'>>> ws:None [7, 9 -> 7, 13]
                                                        'as' <<Regex: <_sre.SRE_Match object; span=(123, 125), match='as'>>> ws:(122, 123) [7, 14 -> 7, 16]
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(126, 139), match='obj5Decorated'>>> ws:(125, 126) [7, 17 -> 7, 30]
                                            Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                                ',' <<Regex: <_sre.SRE_Match object; span=(139, 140), match=','>>> ws:None [7, 30 -> 7, 31]
                                                Newline+ <<140, 142>> ws:None !Ignored! [7, 31 -> 9, 1]
                                                Indent <<142, 154, (12)>> ws:None !Ignored! [9, 1 -> 9, 13]
                                                Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(154, 158), match='obj6'>>> ws:None [9, 13 -> 9, 17]
                                        Newline+ <<158, 159>> ws:None !Ignored! [9, 17 -> 10, 1]
                                        Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                        Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                        Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                        Repeat: (',', 0, 1)
                                            <No Children>
                                    ')' <<Regex: <_sre.SRE_Match object; span=(159, 160), match=')'>>> ws:None [10, 1 -> 10, 2]
                            Newline+ <<160, 161>> ws:None [10, 2 -> 11, 1]
            """,
        )

        assert len(result.Children) == 2

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[0].Children[0].Children[0].source_filename == self._root_file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "obj1" : "obj1",
            "obj2" : "obj2Decorated",
        }

        assert result.Children[1].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[1].Children[0].Children[0].source_filename == self._file2
        assert result.Children[1].Children[0].Children[0].import_items == {
            "obj3" : "obj3Decorated",
            "obj4" : "obj4",
            "obj5" : "obj5Decorated",
            "obj6" : "obj6",
        }

    # ----------------------------------------------------------------------
    def test_TrailingCommas(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from . import File1,
                from ...File2 import obj1, obj2,

                from ...Dir1.File3 import (
                    obj3 as obj3Decorated,
                )

                from .Dir2.Dir3.File4 import (
                    obj4, obj5,
                )
                """,
            ),
            self._file1 : "pass",
            self._file2: "pass",
            self._file3: "pass",
            self._file4: "pass",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        assert len(result) == len(content)
        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 6 -> 1, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 8 -> 1, 14]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='File1'>>> ws:(13, 14) [1, 15 -> 1, 20]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        <No Children>
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [1, 20 -> 1, 21]
                            Newline+ <<20, 21>> ws:None [1, 21 -> 2, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='from'>>> ws:None [2, 1 -> 2, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(26, 34), match='...File2'>>> ws:(25, 26) [2, 6 -> 2, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(35, 41), match='import'>>> ws:(34, 35) [2, 15 -> 2, 21]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                    Or: {Sequence: [<name>, 'as', <name>], <name>}
                                        <name> <<Regex: <_sre.SRE_Match object; span=(42, 46), match='obj1'>>> ws:(41, 42) [2, 22 -> 2, 26]
                                    Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                        Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                            ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [2, 26 -> 2, 27]
                                            Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                <name> <<Regex: <_sre.SRE_Match object; span=(48, 52), match='obj2'>>> ws:(47, 48) [2, 28 -> 2, 32]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [2, 32 -> 2, 33]
                            Newline+ <<53, 55>> ws:None [2, 33 -> 4, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='from'>>> ws:None [4, 1 -> 4, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(60, 73), match='...Dir1.File3'>>> ws:(59, 60) [4, 6 -> 4, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(74, 80), match='import'>>> ws:(73, 74) [4, 20 -> 4, 26]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Grouped
                                    '(' <<Regex: <_sre.SRE_Match object; span=(81, 82), match='('>>> ws:(80, 81) [4, 27 -> 4, 28]
                                    Newline+ <<82, 83>> ws:None !Ignored! [4, 28 -> 5, 1]
                                    Indent <<83, 87, (4)>> ws:None !Ignored! [5, 1 -> 5, 5]
                                    Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                        Or: {Sequence: [<name>, 'as', <name>], <name>}
                                            Sequence: [<name>, 'as', <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(87, 91), match='obj3'>>> ws:None [5, 5 -> 5, 9]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(92, 94), match='as'>>> ws:(91, 92) [5, 10 -> 5, 12]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 108), match='obj3Decorated'>>> ws:(94, 95) [5, 13 -> 5, 26]
                                        Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                            <No Children>
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(108, 109), match=','>>> ws:None [5, 26 -> 5, 27]
                                    Newline+ <<109, 110>> ws:None !Ignored! [5, 27 -> 6, 1]
                                    Dedent <<>> ws:None !Ignored! [6, 1 -> 6, 1]
                                    ')' <<Regex: <_sre.SRE_Match object; span=(110, 111), match=')'>>> ws:None [6, 1 -> 6, 2]
                            Newline+ <<111, 113>> ws:None [6, 2 -> 8, 1]
                Dynamic Statements
                    1.0.0 Grammar
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(113, 117), match='from'>>> ws:None [8, 1 -> 8, 5]
                            <name> <<Regex: <_sre.SRE_Match object; span=(118, 134), match='.Dir2.Dir3.File4'>>> ws:(117, 118) [8, 6 -> 8, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(135, 141), match='import'>>> ws:(134, 135) [8, 23 -> 8, 29]
                            Or: {Grouped, Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]}
                                Grouped
                                    '(' <<Regex: <_sre.SRE_Match object; span=(142, 143), match='('>>> ws:(141, 142) [8, 30 -> 8, 31]
                                    Newline+ <<143, 144>> ws:None !Ignored! [8, 31 -> 9, 1]
                                    Indent <<144, 148, (4)>> ws:None !Ignored! [9, 1 -> 9, 5]
                                    Sequence: [Or: {Sequence: [<name>, 'as', <name>], <name>}, Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None), Repeat: (',', 0, 1)]
                                        Or: {Sequence: [<name>, 'as', <name>], <name>}
                                            <name> <<Regex: <_sre.SRE_Match object; span=(148, 152), match='obj4'>>> ws:None [9, 5 -> 9, 9]
                                        Repeat: (Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}], 0, None)
                                            Sequence: [',', Or: {Sequence: [<name>, 'as', <name>], <name>}]
                                                ',' <<Regex: <_sre.SRE_Match object; span=(152, 153), match=','>>> ws:None [9, 9 -> 9, 10]
                                                Or: {Sequence: [<name>, 'as', <name>], <name>}
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(154, 158), match='obj5'>>> ws:(153, 154) [9, 11 -> 9, 15]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(158, 159), match=','>>> ws:None [9, 15 -> 9, 16]
                                    Newline+ <<159, 160>> ws:None !Ignored! [9, 16 -> 10, 1]
                                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                    ')' <<Regex: <_sre.SRE_Match object; span=(160, 161), match=')'>>> ws:None [10, 1 -> 10, 2]
                            Newline+ <<161, 162>> ws:None [10, 2 -> 11, 1]
            """,
        )

        assert len(result.Children) == 4

        assert result.Children[0].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsDirectory
        assert result.Children[0].Children[0].Children[0].source_filename == self._file1
        assert result.Children[0].Children[0].Children[0].import_items == {
            "File1" : "File1",
        }

        assert result.Children[1].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[1].Children[0].Children[0].source_filename == self._file2
        assert result.Children[1].Children[0].Children[0].import_items == {
            "obj1" : "obj1",
            "obj2" : "obj2",
        }

        assert result.Children[2].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[2].Children[0].Children[0].source_filename == self._file3
        assert result.Children[2].Children[0].Children[0].import_items == {
            "obj3" : "obj3Decorated",
        }

        assert result.Children[3].Children[0].Children[0].import_type == ImportStatement.ImportType.SourceIsModule
        assert result.Children[3].Children[0].Children[0].source_filename == self._file4
        assert result.Children[3].Children[0].Children[0].import_items == {
            "obj4" : "obj4",
            "obj5" : "obj5",
        }

    # ----------------------------------------------------------------------
    def test_RelativePathError(self):
        # Create a relative path that is greater than the number of directories in the current path
        dots = "." * (_script_dir.count(os.path.sep) + 5)

        content = {
            self._filename : textwrap.dedent(
                """\
                from {} import File1
                """,
            ).format(dots),
        }

        with pytest.raises(InvalidRelativePathError) as ex:
            PatchAndExecute(
                content,
                [self._filename],
                [],
            )

        ex = ex.value

        assert str(ex) == "The relative path '{}' is not valid for the origin '{}'".format(dots, _script_dir)
        assert ex.Line == 1
        assert ex.Column == 6
        assert ex.LineEnd == 1
        assert ex.ColumnEnd == 6 + len(dots)
        assert ex.SourceName == dots
        assert ex.OriginName == _script_dir

    # ----------------------------------------------------------------------
    def test_BadFile(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from InvalidFile1 import (obj1, obj2)
                """,
            ),
        }

        with pytest.raises(UnknownSourceError) as ex:
            PatchAndExecute(
                content,
                [self._filename],
                [],
            )

        ex = ex.value

        assert str(ex) == "'InvalidFile1' could not be found"
        assert ex.FullyQualifiedName == self._filename
        assert ex.Line == 1
        assert ex.Column == 1
        assert ex.SourceName == "InvalidFile1"
