# ----------------------------------------------------------------------
# |
# |  ImportStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-31 20:49:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration test for ImportStatement.py"""

import os
import textwrap

from contextlib import contextmanager
from io import StringIO
from typing import Dict
from unittest.mock import patch

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ImportStatement import *
    from ....Parse import Parse


# ----------------------------------------------------------------------
@contextmanager
def Patcher(
    content_dict: Dict[str, str],
):
    # ----------------------------------------------------------------------
    def IsFile(filename):
        return filename in content_dict

    # ----------------------------------------------------------------------
    def IsDir(dirname):
        for key in content_dict.keys():
            if dirname == os.path.dirname(key):
                return True

        return False

    # ----------------------------------------------------------------------

    with                                                                                            \
        patch("os.path.isfile", side_effect=IsFile),                                                \
        patch("os.path.isdir", side_effect=IsDir),                                                  \
        patch("builtins.open", side_effect=lambda filename: StringIO(content_dict[filename]))       \
    :
        yield


# ----------------------------------------------------------------------
class TestStandard(object):
    _filename                               = os.path.join(_script_dir, "filename.TheLanguage")
    _file1                                  = os.path.join(_script_dir, "file1.TheLanguage")
    _file2                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "file2.TheLanguage"))
    _file3                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "dir1", "file3.TheLanguage"))
    _file4                                  = os.path.join(_script_dir, "dir2", "dir3", "file4.TheLanguage")

    _root1                                  = os.path.realpath(os.path.join(_script_dir, ".."))
    _root2                                  = os.path.realpath(os.path.join(_script_dir, "..", ".."))
    _root3                                  = os.path.join(_script_dir, "dir1")

    _root_file1                             = os.path.join(_root1, "File1.TheLanguage")
    _root_file2                             = os.path.join(_root2, "File2.TheLanguage")
    _root_file3                             = os.path.join(_root3, "File3.TheLanguage")
    _root_file4                             = os.path.join(_root3, "Dir1", "Dir2", "File4.TheLanguage")

    # ----------------------------------------------------------------------
    def test_SingleRelativeDirectory(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from . import file1
                from . import file1 as File1

                from ... import file2
                from ... import file2 as File2

                from ...dir1 import file3
                from ...dir1 import file3 as File3

                from .dir2.dir3 import file4
                from .dir2.dir3 import file4 as File4
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [],
            )

            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 14]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='file1'>>> ws:(13, 14) [1, 20]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<19, 20>> ws:None [2, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(20, 24), match='from'>>> ws:None [2, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='.'>>> ws:(24, 25) [2, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(27, 33), match='import'>>> ws:(26, 27) [2, 14]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='file1'>>> ws:(33, 34) [2, 20]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(40, 42), match='as'>>> ws:(39, 40) [2, 23]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(43, 48), match='File1'>>> ws:(42, 43) [2, 29]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<48, 50>> ws:None [4, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(50, 54), match='from'>>> ws:None [4, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(55, 58), match='...'>>> ws:(54, 55) [4, 9]
                            'import' <<Regex: <_sre.SRE_Match object; span=(59, 65), match='import'>>> ws:(58, 59) [4, 16]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(66, 71), match='file2'>>> ws:(65, 66) [4, 22]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<71, 72>> ws:None [5, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(72, 76), match='from'>>> ws:None [5, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(77, 80), match='...'>>> ws:(76, 77) [5, 9]
                            'import' <<Regex: <_sre.SRE_Match object; span=(81, 87), match='import'>>> ws:(80, 81) [5, 16]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(88, 93), match='file2'>>> ws:(87, 88) [5, 22]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(94, 96), match='as'>>> ws:(93, 94) [5, 25]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(97, 102), match='File2'>>> ws:(96, 97) [5, 31]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<102, 104>> ws:None [7, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(104, 108), match='from'>>> ws:None [7, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(109, 116), match='...dir1'>>> ws:(108, 109) [7, 13]
                            'import' <<Regex: <_sre.SRE_Match object; span=(117, 123), match='import'>>> ws:(116, 117) [7, 20]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(124, 129), match='file3'>>> ws:(123, 124) [7, 26]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<129, 130>> ws:None [8, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(130, 134), match='from'>>> ws:None [8, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(135, 142), match='...dir1'>>> ws:(134, 135) [8, 13]
                            'import' <<Regex: <_sre.SRE_Match object; span=(143, 149), match='import'>>> ws:(142, 143) [8, 20]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(150, 155), match='file3'>>> ws:(149, 150) [8, 26]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(156, 158), match='as'>>> ws:(155, 156) [8, 29]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(159, 164), match='File3'>>> ws:(158, 159) [8, 35]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<164, 166>> ws:None [10, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(166, 170), match='from'>>> ws:None [10, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(171, 181), match='.dir2.dir3'>>> ws:(170, 171) [10, 16]
                            'import' <<Regex: <_sre.SRE_Match object; span=(182, 188), match='import'>>> ws:(181, 182) [10, 23]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(189, 194), match='file4'>>> ws:(188, 189) [10, 29]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<194, 195>> ws:None [11, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(195, 199), match='from'>>> ws:None [11, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(200, 210), match='.dir2.dir3'>>> ws:(199, 200) [11, 16]
                            'import' <<Regex: <_sre.SRE_Match object; span=(211, 217), match='import'>>> ws:(210, 211) [11, 23]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(218, 223), match='file4'>>> ws:(217, 218) [11, 29]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(224, 226), match='as'>>> ws:(223, 224) [11, 32]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(227, 232), match='File4'>>> ws:(226, 227) [11, 38]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<232, 233>> ws:None [12, 1]
                """,
            )

            assert len(result.Children) == 16

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._file1
            assert result.Children[0].Children[0].import_items == {
                "file1" : "file1",
            }

            assert len(result.Children[2].Children) == 1
            assert result.Children[2].Children[0].source_filename == self._file1
            assert result.Children[2].Children[0].import_items == {
                "file1" : "File1",
            }

            assert len(result.Children[4].Children) == 1
            assert result.Children[4].Children[0].source_filename == self._file2
            assert result.Children[4].Children[0].import_items == {
                "file2" : "file2",
            }

            assert len(result.Children[6].Children) == 1
            assert result.Children[6].Children[0].source_filename == self._file2
            assert result.Children[6].Children[0].import_items == {
                "file2" : "File2",
            }

            assert len(result.Children[8].Children) == 1
            assert result.Children[8].Children[0].source_filename == self._file3
            assert result.Children[8].Children[0].import_items == {
                "file3" : "file3",
            }

            assert len(result.Children[10].Children) == 1
            assert result.Children[10].Children[0].source_filename == self._file3
            assert result.Children[10].Children[0].import_items == {
                "file3" : "File3",
            }

            assert len(result.Children[12].Children) == 1
            assert result.Children[12].Children[0].source_filename == self._file4
            assert result.Children[12].Children[0].import_items == {
                "file4" : "file4",
            }

            assert len(result.Children[14].Children) == 1
            assert result.Children[14].Children[0].source_filename == self._file4
            assert result.Children[14].Children[0].import_items == {
                "file4" : "File4",
            }

    # ----------------------------------------------------------------------
    def test_SingleRelativeFilename(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from .file1 import obj1
                from .file1 import obj1 as Obj1

                from ...file2 import obj2
                from ...file2 import obj2 as Obj2

                from ...dir1.file3 import obj3
                from ...dir1.file3 import obj3 as Obj3

                from .dir2.dir3.file4 import obj4
                from .dir2.dir3.file4 import obj4 as Obj4
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [],
            )

            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 11), match='.file1'>>> ws:(4, 5) [1, 12]
                            'import' <<Regex: <_sre.SRE_Match object; span=(12, 18), match='import'>>> ws:(11, 12) [1, 19]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:(18, 19) [1, 24]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<23, 24>> ws:None [2, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(24, 28), match='from'>>> ws:None [2, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(29, 35), match='.file1'>>> ws:(28, 29) [2, 12]
                            'import' <<Regex: <_sre.SRE_Match object; span=(36, 42), match='import'>>> ws:(35, 36) [2, 19]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(43, 47), match='obj1'>>> ws:(42, 43) [2, 24]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(48, 50), match='as'>>> ws:(47, 48) [2, 27]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='Obj1'>>> ws:(50, 51) [2, 32]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<55, 57>> ws:None [4, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(57, 61), match='from'>>> ws:None [4, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(62, 70), match='...file2'>>> ws:(61, 62) [4, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(71, 77), match='import'>>> ws:(70, 71) [4, 21]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(78, 82), match='obj2'>>> ws:(77, 78) [4, 26]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<82, 83>> ws:None [5, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(83, 87), match='from'>>> ws:None [5, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(88, 96), match='...file2'>>> ws:(87, 88) [5, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(97, 103), match='import'>>> ws:(96, 97) [5, 21]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='obj2'>>> ws:(103, 104) [5, 26]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(109, 111), match='as'>>> ws:(108, 109) [5, 29]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(112, 116), match='Obj2'>>> ws:(111, 112) [5, 34]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<116, 118>> ws:None [7, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(118, 122), match='from'>>> ws:None [7, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(123, 136), match='...dir1.file3'>>> ws:(122, 123) [7, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(137, 143), match='import'>>> ws:(136, 137) [7, 26]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(144, 148), match='obj3'>>> ws:(143, 144) [7, 31]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<148, 149>> ws:None [8, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(149, 153), match='from'>>> ws:None [8, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(154, 167), match='...dir1.file3'>>> ws:(153, 154) [8, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(168, 174), match='import'>>> ws:(167, 168) [8, 26]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(175, 179), match='obj3'>>> ws:(174, 175) [8, 31]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(180, 182), match='as'>>> ws:(179, 180) [8, 34]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(183, 187), match='Obj3'>>> ws:(182, 183) [8, 39]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<187, 189>> ws:None [10, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(189, 193), match='from'>>> ws:None [10, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(194, 210), match='.dir2.dir3.file4'>>> ws:(193, 194) [10, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(211, 217), match='import'>>> ws:(210, 211) [10, 29]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(218, 222), match='obj4'>>> ws:(217, 218) [10, 34]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<222, 223>> ws:None [11, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(223, 227), match='from'>>> ws:None [11, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(228, 244), match='.dir2.dir3.file4'>>> ws:(227, 228) [11, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(245, 251), match='import'>>> ws:(244, 245) [11, 29]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(252, 256), match='obj4'>>> ws:(251, 252) [11, 34]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(257, 259), match='as'>>> ws:(256, 257) [11, 37]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(260, 264), match='Obj4'>>> ws:(259, 260) [11, 42]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<264, 265>> ws:None [12, 1]
                """,
            )

            assert len(result.Children) == 16

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._file1
            assert result.Children[0].Children[0].import_items == {
                "obj1" : "obj1",
            }

            assert len(result.Children[2].Children) == 1
            assert result.Children[2].Children[0].source_filename == self._file1
            assert result.Children[2].Children[0].import_items == {
                "obj1" : "Obj1",
            }

            assert len(result.Children[4].Children) == 1
            assert result.Children[4].Children[0].source_filename == self._file2
            assert result.Children[4].Children[0].import_items == {
                "obj2" : "obj2",
            }

            assert len(result.Children[6].Children) == 1
            assert result.Children[6].Children[0].source_filename == self._file2
            assert result.Children[6].Children[0].import_items == {
                "obj2" : "Obj2",
            }

            assert len(result.Children[8].Children) == 1
            assert result.Children[8].Children[0].source_filename == self._file3
            assert result.Children[8].Children[0].import_items == {
                "obj3" : "obj3",
            }

            assert len(result.Children[10].Children) == 1
            assert result.Children[10].Children[0].source_filename == self._file3
            assert result.Children[10].Children[0].import_items == {
                "obj3" : "Obj3",
            }

            assert len(result.Children[12].Children) == 1
            assert result.Children[12].Children[0].source_filename == self._file4
            assert result.Children[12].Children[0].import_items == {
                "obj4" : "obj4",
            }

            assert len(result.Children[14].Children) == 1
            assert result.Children[14].Children[0].source_filename == self._file4
            assert result.Children[14].Children[0].import_items == {
                "obj4" : "Obj4",
            }

    # ----------------------------------------------------------------------
    def test_SingleAbsoluteFilename(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import obj1
                from File1 import obj1 as Obj1

                from File2 import obj2
                from File2 import obj2 as Obj2

                from File3 import obj3
                from File3 import obj3 as Obj3

                from Dir1.Dir2.File4 import obj4
                from Dir1.Dir2.File4 import obj4 as Obj4
                """,
            ),
            self._root_file1 : "",
            self._root_file2 : "",
            self._root_file3 : "",
            self._root_file4 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [self._root1, self._root2, self._root3],
            )

            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 23]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<22, 23>> ws:None [2, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(23, 27), match='from'>>> ws:None [2, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(28, 33), match='File1'>>> ws:(27, 28) [2, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(34, 40), match='import'>>> ws:(33, 34) [2, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='obj1'>>> ws:(40, 41) [2, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(46, 48), match='as'>>> ws:(45, 46) [2, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(49, 53), match='Obj1'>>> ws:(48, 49) [2, 31]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<53, 55>> ws:None [4, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='from'>>> ws:None [4, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(60, 65), match='File2'>>> ws:(59, 60) [4, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(66, 72), match='import'>>> ws:(65, 66) [4, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(73, 77), match='obj2'>>> ws:(72, 73) [4, 23]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<77, 78>> ws:None [5, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(78, 82), match='from'>>> ws:None [5, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(83, 88), match='File2'>>> ws:(82, 83) [5, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(89, 95), match='import'>>> ws:(88, 89) [5, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(96, 100), match='obj2'>>> ws:(95, 96) [5, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(101, 103), match='as'>>> ws:(100, 101) [5, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='Obj2'>>> ws:(103, 104) [5, 31]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<108, 110>> ws:None [7, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(110, 114), match='from'>>> ws:None [7, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(115, 120), match='File3'>>> ws:(114, 115) [7, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(121, 127), match='import'>>> ws:(120, 121) [7, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(128, 132), match='obj3'>>> ws:(127, 128) [7, 23]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<132, 133>> ws:None [8, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(133, 137), match='from'>>> ws:None [8, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(138, 143), match='File3'>>> ws:(137, 138) [8, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(144, 150), match='import'>>> ws:(143, 144) [8, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(151, 155), match='obj3'>>> ws:(150, 151) [8, 23]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(156, 158), match='as'>>> ws:(155, 156) [8, 26]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(159, 163), match='Obj3'>>> ws:(158, 159) [8, 31]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<163, 165>> ws:None [10, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(165, 169), match='from'>>> ws:None [10, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(170, 185), match='Dir1.Dir2.File4'>>> ws:(169, 170) [10, 21]
                            'import' <<Regex: <_sre.SRE_Match object; span=(186, 192), match='import'>>> ws:(185, 186) [10, 28]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(193, 197), match='obj4'>>> ws:(192, 193) [10, 33]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<197, 198>> ws:None [11, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(198, 202), match='from'>>> ws:None [11, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(203, 218), match='Dir1.Dir2.File4'>>> ws:(202, 203) [11, 21]
                            'import' <<Regex: <_sre.SRE_Match object; span=(219, 225), match='import'>>> ws:(218, 219) [11, 28]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(226, 230), match='obj4'>>> ws:(225, 226) [11, 33]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(231, 233), match='as'>>> ws:(230, 231) [11, 36]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(234, 238), match='Obj4'>>> ws:(233, 234) [11, 41]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<238, 239>> ws:None [12, 1]
                """,
            )

            assert len(result.Children) == 16

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._root_file1
            assert result.Children[0].Children[0].import_items == {
                "obj1" : "obj1",
            }

            assert len(result.Children[2].Children) == 1
            assert result.Children[2].Children[0].source_filename == self._root_file1
            assert result.Children[2].Children[0].import_items == {
                "obj1" : "Obj1",
            }

            assert len(result.Children[4].Children) == 1
            assert result.Children[4].Children[0].source_filename == self._root_file2
            assert result.Children[4].Children[0].import_items == {
                "obj2" : "obj2",
            }

            assert len(result.Children[6].Children) == 1
            assert result.Children[6].Children[0].source_filename == self._root_file2
            assert result.Children[6].Children[0].import_items == {
                "obj2" : "Obj2",
            }

            assert len(result.Children[8].Children) == 1
            assert result.Children[8].Children[0].source_filename == self._root_file3
            assert result.Children[8].Children[0].import_items == {
                "obj3" : "obj3",
            }

            assert len(result.Children[10].Children) == 1
            assert result.Children[10].Children[0].source_filename == self._root_file3
            assert result.Children[10].Children[0].import_items == {
                "obj3" : "Obj3",
            }

            assert len(result.Children[12].Children) == 1
            assert result.Children[12].Children[0].source_filename == self._root_file4
            assert result.Children[12].Children[0].import_items == {
                "obj4" : "obj4",
            }

            assert len(result.Children[14].Children) == 1
            assert result.Children[14].Children[0].source_filename == self._root_file4
            assert result.Children[14].Children[0].import_items == {
                "obj4" : "Obj4",
            }

    # ----------------------------------------------------------------------
    def test_MultipleSingleLine(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import obj1, obj2 as Obj2, obj3 as Obj3, obj4
                """,
            ),
            self._root_file1 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [self._root1],
            )

            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 18]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 23]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=','>>> ws:None [1, 24]
                                            Or: [Renamed, <name>]
                                                Renamed
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(24, 28), match='obj2'>>> ws:(23, 24) [1, 29]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(29, 31), match='as'>>> ws:(28, 29) [1, 32]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(32, 36), match='Obj2'>>> ws:(31, 32) [1, 37]
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=','>>> ws:None [1, 38]
                                            Or: [Renamed, <name>]
                                                Renamed
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(38, 42), match='obj3'>>> ws:(37, 38) [1, 43]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(43, 45), match='as'>>> ws:(42, 43) [1, 46]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(46, 50), match='Obj3'>>> ws:(45, 46) [1, 51]
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(50, 51), match=','>>> ws:None [1, 52]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(52, 56), match='obj4'>>> ws:(51, 52) [1, 57]
                                    Repeat: (Comma, 0, 1)
                                        <No children>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<56, 57>> ws:None [2, 1]
                """,
            )

            assert len(result.Children) == 2

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._root_file1
            assert result.Children[0].Children[0].import_items == {
                "obj1" : "obj1",
                "obj2" : "Obj2",
                "obj3" : "Obj3",
                "obj4" : "obj4",
            }

    # ----------------------------------------------------------------------
    def test_Grouping(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import (obj1, obj2)

                from ...file2 import (
                    obj3 as Obj3,
                    obj4,

                        obj5
                )
                """,
            ),
            self._root_file1 : "",
            self._file2 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [self._root1],
            )

            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 11]
                            'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 18]
                            Or: [Grouped Items, Items]
                                Grouped Items
                                    '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:(17, 18) [1, 20]
                                    Items
                                        Or: [Renamed, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:None [1, 24]
                                        Repeat: (Comma and Statement, 0, None)
                                            Comma and Statement
                                                ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 25]
                                                Or: [Renamed, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='obj2'>>> ws:(24, 25) [1, 30]
                                        Repeat: (Comma, 0, 1)
                                            <No children>
                                    ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 31]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<30, 32>> ws:None [3, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(32, 36), match='from'>>> ws:None [3, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(37, 45), match='...file2'>>> ws:(36, 37) [3, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(46, 52), match='import'>>> ws:(45, 46) [3, 21]
                            Or: [Grouped Items, Items]
                                Grouped Items
                                    '(' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='('>>> ws:(52, 53) [3, 23]
                                    Newline+ <<54, 55>> ws:None !Ignored! [4, 1]
                                    Indent <<55, 59, (4)>> ws:None !Ignored! [4, 5]
                                    Items
                                        Or: [Renamed, <name>]
                                            Renamed
                                                <name> <<Regex: <_sre.SRE_Match object; span=(59, 63), match='obj3'>>> ws:None [4, 9]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(64, 66), match='as'>>> ws:(63, 64) [4, 12]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(67, 71), match='Obj3'>>> ws:(66, 67) [4, 17]
                                        Repeat: (Comma and Statement, 0, None)
                                            Comma and Statement
                                                ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [4, 18]
                                                Newline+ <<72, 73>> ws:None !Ignored! [5, 1]
                                                Or: [Renamed, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(77, 81), match='obj4'>>> ws:None [5, 9]
                                            Comma and Statement
                                                ',' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=','>>> ws:None [5, 10]
                                                Newline+ <<82, 84>> ws:None !Ignored! [7, 1]
                                                Indent <<84, 92, (8)>> ws:None !Ignored! [7, 9]
                                                Or: [Renamed, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(92, 96), match='obj5'>>> ws:None [7, 13]
                                        Newline+ <<96, 97>> ws:None !Ignored! [8, 1]
                                        Dedent <<>> ws:None !Ignored! [8, 1]
                                        Dedent <<>> ws:None !Ignored! [8, 1]
                                        Repeat: (Comma, 0, 1)
                                            <No children>
                                    ')' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=')'>>> ws:None [8, 2]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<98, 99>> ws:None [9, 1]
                """,
            )

            assert len(result.Children) == 4

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._root_file1
            assert result.Children[0].Children[0].import_items == {
                "obj1" : "obj1",
                "obj2" : "obj2",
            }

            assert len(result.Children[2].Children) == 1
            assert result.Children[2].Children[0].source_filename == self._file2
            assert result.Children[2].Children[0].import_items == {
                "obj3" : "Obj3",
                "obj4" : "obj4",
                "obj5" : "obj5",
            }

    # ----------------------------------------------------------------------
    def test_TrailingCommas(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from . import file1,
                from ...file2 import obj1, obj2,

                from ...dir1.file3 import (
                    obj3 as Obj3,
                )

                from .dir2.dir3.file4 import (
                    obj4, obj5,
                )
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [],
            )


            assert len(result) == len(content)
            for name in result.keys():
                assert name in content

            result = result[self._filename]

            assert str(result) == textwrap.dedent(
                """\
                <Root>
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 7]
                            'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 14]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='file1'>>> ws:(13, 14) [1, 20]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (Comma, 0, 1)
                                        Comma
                                            ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [1, 21]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<20, 21>> ws:None [2, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='from'>>> ws:None [2, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(26, 34), match='...file2'>>> ws:(25, 26) [2, 14]
                            'import' <<Regex: <_sre.SRE_Match object; span=(35, 41), match='import'>>> ws:(34, 35) [2, 21]
                            Or: [Grouped Items, Items]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(42, 46), match='obj1'>>> ws:(41, 42) [2, 26]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [2, 27]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(48, 52), match='obj2'>>> ws:(47, 48) [2, 32]
                                    Repeat: (Comma, 0, 1)
                                        Comma
                                            ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [2, 33]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<53, 55>> ws:None [4, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='from'>>> ws:None [4, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(60, 73), match='...dir1.file3'>>> ws:(59, 60) [4, 19]
                            'import' <<Regex: <_sre.SRE_Match object; span=(74, 80), match='import'>>> ws:(73, 74) [4, 26]
                            Or: [Grouped Items, Items]
                                Grouped Items
                                    '(' <<Regex: <_sre.SRE_Match object; span=(81, 82), match='('>>> ws:(80, 81) [4, 28]
                                    Newline+ <<82, 83>> ws:None !Ignored! [5, 1]
                                    Indent <<83, 87, (4)>> ws:None !Ignored! [5, 5]
                                    Items
                                        Or: [Renamed, <name>]
                                            Renamed
                                                <name> <<Regex: <_sre.SRE_Match object; span=(87, 91), match='obj3'>>> ws:None [5, 9]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(92, 94), match='as'>>> ws:(91, 92) [5, 12]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(95, 99), match='Obj3'>>> ws:(94, 95) [5, 17]
                                        Repeat: (Comma and Statement, 0, None)
                                            <No children>
                                        Repeat: (Comma, 0, 1)
                                            Comma
                                                ',' <<Regex: <_sre.SRE_Match object; span=(99, 100), match=','>>> ws:None [5, 18]
                                    Newline+ <<100, 101>> ws:None !Ignored! [6, 1]
                                    Dedent <<>> ws:None !Ignored! [6, 1]
                                    ')' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=')'>>> ws:None [6, 2]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<102, 104>> ws:None [8, 1]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Import
                            'from' <<Regex: <_sre.SRE_Match object; span=(104, 108), match='from'>>> ws:None [8, 5]
                            <source> <<Regex: <_sre.SRE_Match object; span=(109, 125), match='.dir2.dir3.file4'>>> ws:(108, 109) [8, 22]
                            'import' <<Regex: <_sre.SRE_Match object; span=(126, 132), match='import'>>> ws:(125, 126) [8, 29]
                            Or: [Grouped Items, Items]
                                Grouped Items
                                    '(' <<Regex: <_sre.SRE_Match object; span=(133, 134), match='('>>> ws:(132, 133) [8, 31]
                                    Newline+ <<134, 135>> ws:None !Ignored! [9, 1]
                                    Indent <<135, 139, (4)>> ws:None !Ignored! [9, 5]
                                    Items
                                        Or: [Renamed, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(139, 143), match='obj4'>>> ws:None [9, 9]
                                        Repeat: (Comma and Statement, 0, None)
                                            Comma and Statement
                                                ',' <<Regex: <_sre.SRE_Match object; span=(143, 144), match=','>>> ws:None [9, 10]
                                                Or: [Renamed, <name>]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(145, 149), match='obj5'>>> ws:(144, 145) [9, 15]
                                        Repeat: (Comma, 0, 1)
                                            Comma
                                                ',' <<Regex: <_sre.SRE_Match object; span=(149, 150), match=','>>> ws:None [9, 16]
                                    Newline+ <<150, 151>> ws:None !Ignored! [10, 1]
                                    Dedent <<>> ws:None !Ignored! [10, 1]
                                    ')' <<Regex: <_sre.SRE_Match object; span=(151, 152), match=')'>>> ws:None [10, 2]
                    Or: [Set Syntax, Import, Vertical Whitespace]
                        Vertical Whitespace
                            Newline+ <<152, 153>> ws:None [11, 1]
                """,
            )

            assert len(result.Children) == 8

            assert len(result.Children[0].Children) == 1
            assert result.Children[0].Children[0].source_filename == self._file1
            assert result.Children[0].Children[0].import_items == {
                "file1" : "file1",
            }

            assert len(result.Children[2].Children) == 1
            assert result.Children[2].Children[0].source_filename == self._file2
            assert result.Children[2].Children[0].import_items == {
                "obj1" : "obj1",
                "obj2" : "obj2",
            }

            assert len(result.Children[4].Children) == 1
            assert result.Children[4].Children[0].source_filename == self._file3
            assert result.Children[4].Children[0].import_items == {
                "obj3" : "Obj3",
            }

            assert len(result.Children[6].Children) == 1
            assert result.Children[6].Children[0].source_filename == self._file4
            assert result.Children[6].Children[0].import_items == {
                "obj4" : "obj4",
                "obj5" : "obj5",
            }

    # ----------------------------------------------------------------------
    def test_RelativePathError(self):
        # Create a realtive path that is greater than the number of directories in the current path
        dots = "." * (_script_dir.count(os.path.sep) + 5)

        content = {
            self._filename : textwrap.dedent(
                """\
                from {} import file1
                """,
            ).format(dots),
        }

        with Patcher(content):
            result = Parse(
                [self._filename],
                [],
            )

            assert isinstance(result, list)
            assert len(result) == 1
            result = result[0]

            assert str(result) == "The relative path '{}' is not valid with the origin '{}'".format(dots, _script_dir)
            assert result.Line == 1
            assert result.Column == 6 + len(dots)
            assert result.SourceName == dots
            assert result.OriginName == _script_dir
