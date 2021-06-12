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
    _filename                               = os.path.join(_script_dir, "filename.TheLanguage")
    _file1                                  = os.path.join(_script_dir, "File1.TheLanguage")
    _file2                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "File2.TheLanguage"))
    _file3                                  = os.path.realpath(os.path.join(_script_dir, "..", "..", "dir1", "File3.TheLanguage"))
    _file4                                  = os.path.join(_script_dir, "dir2", "dir3", "File4.TheLanguage")

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
                from . import File1
                from . import File1 as File1Decorated

                from ... import File2
                from ... import File2 as File2Decorated

                from ...dir1 import File3
                from ...dir1 import File3 as File3Decorated

                from .dir2.dir3 import File4
                from .dir2.dir3 import File4 as File4Decorated
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 6 -> 1, 7]
                        'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 8 -> 1, 14]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='File1'>>> ws:(13, 14) [1, 15 -> 1, 20]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<19, 20>> ws:None !Ignored! [1, 20 -> 2, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(20, 24), match='from'>>> ws:None [2, 1 -> 2, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(25, 26), match='.'>>> ws:(24, 25) [2, 6 -> 2, 7]
                        'import' <<Regex: <_sre.SRE_Match object; span=(27, 33), match='import'>>> ws:(26, 27) [2, 8 -> 2, 14]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(34, 39), match='File1'>>> ws:(33, 34) [2, 15 -> 2, 20]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(40, 42), match='as'>>> ws:(39, 40) [2, 21 -> 2, 23]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(43, 57), match='File1Decorated'>>> ws:(42, 43) [2, 24 -> 2, 38]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<57, 59>> ws:None !Ignored! [2, 38 -> 4, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(59, 63), match='from'>>> ws:None [4, 1 -> 4, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(64, 67), match='...'>>> ws:(63, 64) [4, 6 -> 4, 9]
                        'import' <<Regex: <_sre.SRE_Match object; span=(68, 74), match='import'>>> ws:(67, 68) [4, 10 -> 4, 16]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(75, 80), match='File2'>>> ws:(74, 75) [4, 17 -> 4, 22]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<80, 81>> ws:None !Ignored! [4, 22 -> 5, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(81, 85), match='from'>>> ws:None [5, 1 -> 5, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(86, 89), match='...'>>> ws:(85, 86) [5, 6 -> 5, 9]
                        'import' <<Regex: <_sre.SRE_Match object; span=(90, 96), match='import'>>> ws:(89, 90) [5, 10 -> 5, 16]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(97, 102), match='File2'>>> ws:(96, 97) [5, 17 -> 5, 22]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(103, 105), match='as'>>> ws:(102, 103) [5, 23 -> 5, 25]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(106, 120), match='File2Decorated'>>> ws:(105, 106) [5, 26 -> 5, 40]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<120, 122>> ws:None !Ignored! [5, 40 -> 7, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(122, 126), match='from'>>> ws:None [7, 1 -> 7, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(127, 134), match='...dir1'>>> ws:(126, 127) [7, 6 -> 7, 13]
                        'import' <<Regex: <_sre.SRE_Match object; span=(135, 141), match='import'>>> ws:(134, 135) [7, 14 -> 7, 20]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(142, 147), match='File3'>>> ws:(141, 142) [7, 21 -> 7, 26]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<147, 148>> ws:None !Ignored! [7, 26 -> 8, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(148, 152), match='from'>>> ws:None [8, 1 -> 8, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(153, 160), match='...dir1'>>> ws:(152, 153) [8, 6 -> 8, 13]
                        'import' <<Regex: <_sre.SRE_Match object; span=(161, 167), match='import'>>> ws:(160, 161) [8, 14 -> 8, 20]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(168, 173), match='File3'>>> ws:(167, 168) [8, 21 -> 8, 26]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(174, 176), match='as'>>> ws:(173, 174) [8, 27 -> 8, 29]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(177, 191), match='File3Decorated'>>> ws:(176, 177) [8, 30 -> 8, 44]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<191, 193>> ws:None !Ignored! [8, 44 -> 10, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(193, 197), match='from'>>> ws:None [10, 1 -> 10, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(198, 208), match='.dir2.dir3'>>> ws:(197, 198) [10, 6 -> 10, 16]
                        'import' <<Regex: <_sre.SRE_Match object; span=(209, 215), match='import'>>> ws:(208, 209) [10, 17 -> 10, 23]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(216, 221), match='File4'>>> ws:(215, 216) [10, 24 -> 10, 29]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<221, 222>> ws:None !Ignored! [10, 29 -> 11, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(222, 226), match='from'>>> ws:None [11, 1 -> 11, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(227, 237), match='.dir2.dir3'>>> ws:(226, 227) [11, 6 -> 11, 16]
                        'import' <<Regex: <_sre.SRE_Match object; span=(238, 244), match='import'>>> ws:(237, 238) [11, 17 -> 11, 23]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(245, 250), match='File4'>>> ws:(244, 245) [11, 24 -> 11, 29]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(251, 253), match='as'>>> ws:(250, 251) [11, 30 -> 11, 32]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(254, 268), match='File4Decorated'>>> ws:(253, 254) [11, 33 -> 11, 47]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<268, 269>> ws:None !Ignored! [11, 47 -> 12, 1]
            """,
        )

        assert len(result.Children) == 16

        assert len(result.Children[0].Children) == 1
        assert result.Children[0].Children[0].source_filename == self._file1
        assert result.Children[0].Children[0].import_items == {
            "File1" : "File1",
        }

        assert len(result.Children[2].Children) == 1
        assert result.Children[2].Children[0].source_filename == self._file1
        assert result.Children[2].Children[0].import_items == {
            "File1" : "File1Decorated",
        }

        assert len(result.Children[4].Children) == 1
        assert result.Children[4].Children[0].source_filename == self._file2
        assert result.Children[4].Children[0].import_items == {
            "File2" : "File2",
        }

        assert len(result.Children[6].Children) == 1
        assert result.Children[6].Children[0].source_filename == self._file2
        assert result.Children[6].Children[0].import_items == {
            "File2" : "File2Decorated",
        }

        assert len(result.Children[8].Children) == 1
        assert result.Children[8].Children[0].source_filename == self._file3
        assert result.Children[8].Children[0].import_items == {
            "File3" : "File3",
        }

        assert len(result.Children[10].Children) == 1
        assert result.Children[10].Children[0].source_filename == self._file3
        assert result.Children[10].Children[0].import_items == {
            "File3" : "File3Decorated",
        }

        assert len(result.Children[12].Children) == 1
        assert result.Children[12].Children[0].source_filename == self._file4
        assert result.Children[12].Children[0].import_items == {
            "File4" : "File4",
        }

        assert len(result.Children[14].Children) == 1
        assert result.Children[14].Children[0].source_filename == self._file4
        assert result.Children[14].Children[0].import_items == {
            "File4" : "File4Decorated",
        }

    # ----------------------------------------------------------------------
    def test_SingleRelativeFilename(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from .File1 import obj1
                from .File1 import obj1 as Obj1

                from ...File2 import obj2
                from ...File2 import obj2 as Obj2

                from ...dir1.File3 import obj3
                from ...dir1.File3 import obj3 as Obj3

                from .dir2.dir3.File4 import obj4
                from .dir2.dir3.File4 import obj4 as Obj4
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 11), match='.File1'>>> ws:(4, 5) [1, 6 -> 1, 12]
                        'import' <<Regex: <_sre.SRE_Match object; span=(12, 18), match='import'>>> ws:(11, 12) [1, 13 -> 1, 19]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:(18, 19) [1, 20 -> 1, 24]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<23, 24>> ws:None !Ignored! [1, 24 -> 2, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(24, 28), match='from'>>> ws:None [2, 1 -> 2, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(29, 35), match='.File1'>>> ws:(28, 29) [2, 6 -> 2, 12]
                        'import' <<Regex: <_sre.SRE_Match object; span=(36, 42), match='import'>>> ws:(35, 36) [2, 13 -> 2, 19]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(43, 47), match='obj1'>>> ws:(42, 43) [2, 20 -> 2, 24]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(48, 50), match='as'>>> ws:(47, 48) [2, 25 -> 2, 27]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(51, 55), match='Obj1'>>> ws:(50, 51) [2, 28 -> 2, 32]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<55, 57>> ws:None !Ignored! [2, 32 -> 4, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(57, 61), match='from'>>> ws:None [4, 1 -> 4, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(62, 70), match='...File2'>>> ws:(61, 62) [4, 6 -> 4, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(71, 77), match='import'>>> ws:(70, 71) [4, 15 -> 4, 21]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(78, 82), match='obj2'>>> ws:(77, 78) [4, 22 -> 4, 26]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<82, 83>> ws:None !Ignored! [4, 26 -> 5, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(83, 87), match='from'>>> ws:None [5, 1 -> 5, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(88, 96), match='...File2'>>> ws:(87, 88) [5, 6 -> 5, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(97, 103), match='import'>>> ws:(96, 97) [5, 15 -> 5, 21]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='obj2'>>> ws:(103, 104) [5, 22 -> 5, 26]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(109, 111), match='as'>>> ws:(108, 109) [5, 27 -> 5, 29]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(112, 116), match='Obj2'>>> ws:(111, 112) [5, 30 -> 5, 34]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<116, 118>> ws:None !Ignored! [5, 34 -> 7, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(118, 122), match='from'>>> ws:None [7, 1 -> 7, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(123, 136), match='...dir1.File3'>>> ws:(122, 123) [7, 6 -> 7, 19]
                        'import' <<Regex: <_sre.SRE_Match object; span=(137, 143), match='import'>>> ws:(136, 137) [7, 20 -> 7, 26]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(144, 148), match='obj3'>>> ws:(143, 144) [7, 27 -> 7, 31]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<148, 149>> ws:None !Ignored! [7, 31 -> 8, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(149, 153), match='from'>>> ws:None [8, 1 -> 8, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(154, 167), match='...dir1.File3'>>> ws:(153, 154) [8, 6 -> 8, 19]
                        'import' <<Regex: <_sre.SRE_Match object; span=(168, 174), match='import'>>> ws:(167, 168) [8, 20 -> 8, 26]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(175, 179), match='obj3'>>> ws:(174, 175) [8, 27 -> 8, 31]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(180, 182), match='as'>>> ws:(179, 180) [8, 32 -> 8, 34]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(183, 187), match='Obj3'>>> ws:(182, 183) [8, 35 -> 8, 39]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<187, 189>> ws:None !Ignored! [8, 39 -> 10, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(189, 193), match='from'>>> ws:None [10, 1 -> 10, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(194, 210), match='.dir2.dir3.File4'>>> ws:(193, 194) [10, 6 -> 10, 22]
                        'import' <<Regex: <_sre.SRE_Match object; span=(211, 217), match='import'>>> ws:(210, 211) [10, 23 -> 10, 29]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(218, 222), match='obj4'>>> ws:(217, 218) [10, 30 -> 10, 34]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<222, 223>> ws:None !Ignored! [10, 34 -> 11, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(223, 227), match='from'>>> ws:None [11, 1 -> 11, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(228, 244), match='.dir2.dir3.File4'>>> ws:(227, 228) [11, 6 -> 11, 22]
                        'import' <<Regex: <_sre.SRE_Match object; span=(245, 251), match='import'>>> ws:(244, 245) [11, 23 -> 11, 29]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(252, 256), match='obj4'>>> ws:(251, 252) [11, 30 -> 11, 34]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(257, 259), match='as'>>> ws:(256, 257) [11, 35 -> 11, 37]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(260, 264), match='Obj4'>>> ws:(259, 260) [11, 38 -> 11, 42]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<264, 265>> ws:None !Ignored! [11, 42 -> 12, 1]
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

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1, self._root2, self._root3],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<22, 23>> ws:None !Ignored! [1, 23 -> 2, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(23, 27), match='from'>>> ws:None [2, 1 -> 2, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(28, 33), match='File1'>>> ws:(27, 28) [2, 6 -> 2, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(34, 40), match='import'>>> ws:(33, 34) [2, 12 -> 2, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(41, 45), match='obj1'>>> ws:(40, 41) [2, 19 -> 2, 23]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(46, 48), match='as'>>> ws:(45, 46) [2, 24 -> 2, 26]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(49, 53), match='Obj1'>>> ws:(48, 49) [2, 27 -> 2, 31]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<53, 55>> ws:None !Ignored! [2, 31 -> 4, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='from'>>> ws:None [4, 1 -> 4, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(60, 65), match='File2'>>> ws:(59, 60) [4, 6 -> 4, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(66, 72), match='import'>>> ws:(65, 66) [4, 12 -> 4, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(73, 77), match='obj2'>>> ws:(72, 73) [4, 19 -> 4, 23]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<77, 78>> ws:None !Ignored! [4, 23 -> 5, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(78, 82), match='from'>>> ws:None [5, 1 -> 5, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(83, 88), match='File2'>>> ws:(82, 83) [5, 6 -> 5, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(89, 95), match='import'>>> ws:(88, 89) [5, 12 -> 5, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(96, 100), match='obj2'>>> ws:(95, 96) [5, 19 -> 5, 23]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(101, 103), match='as'>>> ws:(100, 101) [5, 24 -> 5, 26]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(104, 108), match='Obj2'>>> ws:(103, 104) [5, 27 -> 5, 31]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<108, 110>> ws:None !Ignored! [5, 31 -> 7, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(110, 114), match='from'>>> ws:None [7, 1 -> 7, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(115, 120), match='File3'>>> ws:(114, 115) [7, 6 -> 7, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(121, 127), match='import'>>> ws:(120, 121) [7, 12 -> 7, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(128, 132), match='obj3'>>> ws:(127, 128) [7, 19 -> 7, 23]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<132, 133>> ws:None !Ignored! [7, 23 -> 8, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(133, 137), match='from'>>> ws:None [8, 1 -> 8, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(138, 143), match='File3'>>> ws:(137, 138) [8, 6 -> 8, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(144, 150), match='import'>>> ws:(143, 144) [8, 12 -> 8, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(151, 155), match='obj3'>>> ws:(150, 151) [8, 19 -> 8, 23]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(156, 158), match='as'>>> ws:(155, 156) [8, 24 -> 8, 26]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(159, 163), match='Obj3'>>> ws:(158, 159) [8, 27 -> 8, 31]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<163, 165>> ws:None !Ignored! [8, 31 -> 10, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(165, 169), match='from'>>> ws:None [10, 1 -> 10, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(170, 185), match='Dir1.Dir2.File4'>>> ws:(169, 170) [10, 6 -> 10, 21]
                        'import' <<Regex: <_sre.SRE_Match object; span=(186, 192), match='import'>>> ws:(185, 186) [10, 22 -> 10, 28]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(193, 197), match='obj4'>>> ws:(192, 193) [10, 29 -> 10, 33]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<197, 198>> ws:None !Ignored! [10, 33 -> 11, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(198, 202), match='from'>>> ws:None [11, 1 -> 11, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(203, 218), match='Dir1.Dir2.File4'>>> ws:(202, 203) [11, 6 -> 11, 21]
                        'import' <<Regex: <_sre.SRE_Match object; span=(219, 225), match='import'>>> ws:(218, 219) [11, 22 -> 11, 28]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    Renamed
                                        <name> <<Regex: <_sre.SRE_Match object; span=(226, 230), match='obj4'>>> ws:(225, 226) [11, 29 -> 11, 33]
                                        'as' <<Regex: <_sre.SRE_Match object; span=(231, 233), match='as'>>> ws:(230, 231) [11, 34 -> 11, 36]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(234, 238), match='Obj4'>>> ws:(233, 234) [11, 37 -> 11, 41]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<238, 239>> ws:None !Ignored! [11, 41 -> 12, 1]
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

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='obj1'>>> ws:(17, 18) [1, 19 -> 1, 23]
                                Repeat: (Comma and Statement, 0, None)
                                    Comma and Statement
                                        ',' <<Regex: <_sre.SRE_Match object; span=(22, 23), match=','>>> ws:None [1, 23 -> 1, 24]
                                        Or: [Renamed, <name>]
                                            Renamed
                                                <name> <<Regex: <_sre.SRE_Match object; span=(24, 28), match='obj2'>>> ws:(23, 24) [1, 25 -> 1, 29]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(29, 31), match='as'>>> ws:(28, 29) [1, 30 -> 1, 32]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(32, 36), match='Obj2'>>> ws:(31, 32) [1, 33 -> 1, 37]
                                    Comma and Statement
                                        ',' <<Regex: <_sre.SRE_Match object; span=(36, 37), match=','>>> ws:None [1, 37 -> 1, 38]
                                        Or: [Renamed, <name>]
                                            Renamed
                                                <name> <<Regex: <_sre.SRE_Match object; span=(38, 42), match='obj3'>>> ws:(37, 38) [1, 39 -> 1, 43]
                                                'as' <<Regex: <_sre.SRE_Match object; span=(43, 45), match='as'>>> ws:(42, 43) [1, 44 -> 1, 46]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(46, 50), match='Obj3'>>> ws:(45, 46) [1, 47 -> 1, 51]
                                    Comma and Statement
                                        ',' <<Regex: <_sre.SRE_Match object; span=(50, 51), match=','>>> ws:None [1, 51 -> 1, 52]
                                        Or: [Renamed, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(52, 56), match='obj4'>>> ws:(51, 52) [1, 53 -> 1, 57]
                                Repeat: (',', 0, 1)
                                    <No children>
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<56, 57>> ws:None !Ignored! [1, 57 -> 2, 1]
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

                from ...File2 import (
                    obj3 as Obj3,
                    obj4,

                        obj5
                )
                """,
            ),
            self._root_file1 : "",
            self._file2 : "",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:(17, 18) [1, 19 -> 1, 20]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:None [1, 20 -> 1, 24]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='obj2'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 30 -> 1, 31]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<30, 32>> ws:None !Ignored! [1, 31 -> 3, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(32, 36), match='from'>>> ws:None [3, 1 -> 3, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(37, 45), match='...File2'>>> ws:(36, 37) [3, 6 -> 3, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(46, 52), match='import'>>> ws:(45, 46) [3, 15 -> 3, 21]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='('>>> ws:(52, 53) [3, 22 -> 3, 23]
                                Newline+ <<54, 55>> ws:None !Ignored! [3, 23 -> 4, 1]
                                Indent <<55, 59, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(59, 63), match='obj3'>>> ws:None [4, 5 -> 4, 9]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(64, 66), match='as'>>> ws:(63, 64) [4, 10 -> 4, 12]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(67, 71), match='Obj3'>>> ws:(66, 67) [4, 13 -> 4, 17]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(71, 72), match=','>>> ws:None [4, 17 -> 4, 18]
                                            Newline+ <<72, 73>> ws:None !Ignored! [4, 18 -> 5, 1]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(77, 81), match='obj4'>>> ws:None [5, 5 -> 5, 9]
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(81, 82), match=','>>> ws:None [5, 9 -> 5, 10]
                                            Newline+ <<82, 84>> ws:None !Ignored! [5, 10 -> 7, 1]
                                            Indent <<84, 92, (8)>> ws:None !Ignored! [7, 1 -> 7, 9]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(92, 96), match='obj5'>>> ws:None [7, 9 -> 7, 13]
                                    Newline+ <<96, 97>> ws:None !Ignored! [7, 13 -> 8, 1]
                                    Dedent <<>> ws:None !Ignored! [8, 1 -> 8, 1]
                                    Dedent <<>> ws:None !Ignored! [8, 1 -> 8, 1]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(97, 98), match=')'>>> ws:None [8, 1 -> 8, 2]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<98, 99>> ws:None !Ignored! [8, 2 -> 9, 1]
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
                from . import File1,
                from ...File2 import obj1, obj2,

                from ...dir1.File3 import (
                    obj3 as Obj3,
                )

                from .dir2.dir3.File4 import (
                    obj4, obj5,
                )
                """,
            ),
            self._file1 : "",
            self._file2 : "",
            self._file3 : "",
            self._file4 : "",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 6), match='.'>>> ws:(4, 5) [1, 6 -> 1, 7]
                        'import' <<Regex: <_sre.SRE_Match object; span=(7, 13), match='import'>>> ws:(6, 7) [1, 8 -> 1, 14]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(14, 19), match='File1'>>> ws:(13, 14) [1, 15 -> 1, 20]
                                Repeat: (Comma and Statement, 0, None)
                                    <No children>
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(19, 20), match=','>>> ws:None [1, 20 -> 1, 21]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<20, 21>> ws:None !Ignored! [1, 21 -> 2, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(21, 25), match='from'>>> ws:None [2, 1 -> 2, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(26, 34), match='...File2'>>> ws:(25, 26) [2, 6 -> 2, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(35, 41), match='import'>>> ws:(34, 35) [2, 15 -> 2, 21]
                        Or: [Grouped Items, Items]
                            Items
                                Or: [Renamed, <name>]
                                    <name> <<Regex: <_sre.SRE_Match object; span=(42, 46), match='obj1'>>> ws:(41, 42) [2, 22 -> 2, 26]
                                Repeat: (Comma and Statement, 0, None)
                                    Comma and Statement
                                        ',' <<Regex: <_sre.SRE_Match object; span=(46, 47), match=','>>> ws:None [2, 26 -> 2, 27]
                                        Or: [Renamed, <name>]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(48, 52), match='obj2'>>> ws:(47, 48) [2, 28 -> 2, 32]
                                Repeat: (',', 0, 1)
                                    ',' <<Regex: <_sre.SRE_Match object; span=(52, 53), match=','>>> ws:None [2, 32 -> 2, 33]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<53, 55>> ws:None !Ignored! [2, 33 -> 4, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(55, 59), match='from'>>> ws:None [4, 1 -> 4, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(60, 73), match='...dir1.File3'>>> ws:(59, 60) [4, 6 -> 4, 19]
                        'import' <<Regex: <_sre.SRE_Match object; span=(74, 80), match='import'>>> ws:(73, 74) [4, 20 -> 4, 26]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(81, 82), match='('>>> ws:(80, 81) [4, 27 -> 4, 28]
                                Newline+ <<82, 83>> ws:None !Ignored! [4, 28 -> 5, 1]
                                Indent <<83, 87, (4)>> ws:None !Ignored! [5, 1 -> 5, 5]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(87, 91), match='obj3'>>> ws:None [5, 5 -> 5, 9]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(92, 94), match='as'>>> ws:(91, 92) [5, 10 -> 5, 12]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(95, 99), match='Obj3'>>> ws:(94, 95) [5, 13 -> 5, 17]
                                    Repeat: (Comma and Statement, 0, None)
                                        <No children>
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(99, 100), match=','>>> ws:None [5, 17 -> 5, 18]
                                Newline+ <<100, 101>> ws:None !Ignored! [5, 18 -> 6, 1]
                                Dedent <<>> ws:None !Ignored! [6, 1 -> 6, 1]
                                ')' <<Regex: <_sre.SRE_Match object; span=(101, 102), match=')'>>> ws:None [6, 1 -> 6, 2]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<102, 104>> ws:None !Ignored! [6, 2 -> 8, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(104, 108), match='from'>>> ws:None [8, 1 -> 8, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(109, 125), match='.dir2.dir3.File4'>>> ws:(108, 109) [8, 6 -> 8, 22]
                        'import' <<Regex: <_sre.SRE_Match object; span=(126, 132), match='import'>>> ws:(125, 126) [8, 23 -> 8, 29]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(133, 134), match='('>>> ws:(132, 133) [8, 30 -> 8, 31]
                                Newline+ <<134, 135>> ws:None !Ignored! [8, 31 -> 9, 1]
                                Indent <<135, 139, (4)>> ws:None !Ignored! [9, 1 -> 9, 5]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(139, 143), match='obj4'>>> ws:None [9, 5 -> 9, 9]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(143, 144), match=','>>> ws:None [9, 9 -> 9, 10]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(145, 149), match='obj5'>>> ws:(144, 145) [9, 11 -> 9, 15]
                                    Repeat: (',', 0, 1)
                                        ',' <<Regex: <_sre.SRE_Match object; span=(149, 150), match=','>>> ws:None [9, 15 -> 9, 16]
                                Newline+ <<150, 151>> ws:None !Ignored! [9, 16 -> 10, 1]
                                Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                ')' <<Regex: <_sre.SRE_Match object; span=(151, 152), match=')'>>> ws:None [10, 1 -> 10, 2]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<152, 153>> ws:None !Ignored! [10, 2 -> 11, 1]
            """,
        )

        assert len(result.Children) == 8

        assert len(result.Children[0].Children) == 1
        assert result.Children[0].Children[0].source_filename == self._file1
        assert result.Children[0].Children[0].import_items == {
            "File1" : "File1",
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

        result = ex.value

        assert str(result) == "The relative path '{}' is not valid for the origin '{}'".format(dots, _script_dir)
        assert result.Line == 1
        assert result.Column == 6
        assert result.LineEnd == 1
        assert result.ColumnEnd == 6 + len(dots)
        assert result.SourceName == dots
        assert result.OriginName == _script_dir

    # ----------------------------------------------------------------------
    def test_Comments(self):
        content = {
            self._filename : textwrap.dedent(
                """\
                from File1 import (obj1, obj2)

                from ...File2 import (      # Comment 1
                    obj3 as Obj3,           # Comment 2
                    obj4,

                        obj5                # Comment 4
                        as                  # Comment 5
                        Obj5                # Comment 6
                )
                """,
            ),
            self._root_file1 : "",
            self._file2 : "",
        }

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:(17, 18) [1, 19 -> 1, 20]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:None [1, 20 -> 1, 24]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='obj2'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 30 -> 1, 31]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<30, 32>> ws:None !Ignored! [1, 31 -> 3, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(32, 36), match='from'>>> ws:None [3, 1 -> 3, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(37, 45), match='...File2'>>> ws:(36, 37) [3, 6 -> 3, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(46, 52), match='import'>>> ws:(45, 46) [3, 15 -> 3, 21]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='('>>> ws:(52, 53) [3, 22 -> 3, 23]
                                Comment <<Regex: <_sre.SRE_Match object; span=(60, 71), match='# Comment 1'>>> ws:(54, 60) !Ignored! [3, 29 -> 3, 40]
                                Newline+ <<71, 72>> ws:None !Ignored! [3, 40 -> 4, 1]
                                Indent <<72, 76, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(76, 80), match='obj3'>>> ws:None [4, 5 -> 4, 9]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(81, 83), match='as'>>> ws:(80, 81) [4, 10 -> 4, 12]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 88), match='Obj3'>>> ws:(83, 84) [4, 13 -> 4, 17]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=','>>> ws:None [4, 17 -> 4, 18]
                                            Comment <<Regex: <_sre.SRE_Match object; span=(100, 111), match='# Comment 2'>>> ws:(89, 100) !Ignored! [4, 29 -> 4, 40]
                                            Newline+ <<111, 112>> ws:None !Ignored! [4, 40 -> 5, 1]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(116, 120), match='obj4'>>> ws:None [5, 5 -> 5, 9]
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(120, 121), match=','>>> ws:None [5, 9 -> 5, 10]
                                            Newline+ <<121, 123>> ws:None !Ignored! [5, 10 -> 7, 1]
                                            Indent <<123, 131, (8)>> ws:None !Ignored! [7, 1 -> 7, 9]
                                            Or: [Renamed, <name>]
                                                Renamed
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(131, 135), match='obj5'>>> ws:None [7, 9 -> 7, 13]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(151, 162), match='# Comment 4'>>> ws:(135, 151) !Ignored! [7, 29 -> 7, 40]
                                                    Newline+ <<162, 163>> ws:None !Ignored! [7, 40 -> 8, 1]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(171, 173), match='as'>>> ws:None [8, 9 -> 8, 11]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(191, 202), match='# Comment 5'>>> ws:(173, 191) !Ignored! [8, 29 -> 8, 40]
                                                    Newline+ <<202, 203>> ws:None !Ignored! [8, 40 -> 9, 1]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(211, 215), match='Obj5'>>> ws:None [9, 9 -> 9, 13]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(231, 242), match='# Comment 6'>>> ws:(215, 231) !Ignored! [9, 29 -> 9, 40]
                                    Newline+ <<242, 243>> ws:None !Ignored! [9, 40 -> 10, 1]
                                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(243, 244), match=')'>>> ws:None [10, 1 -> 10, 2]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<244, 245>> ws:None !Ignored! [10, 2 -> 11, 1]
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
            "obj5" : "Obj5",
        }

    # ----------------------------------------------------------------------
    def test_StandaloneComments(self):
        content = {
                self._filename : textwrap.dedent(
                    """\
                    from File1 import (obj1, obj2)

                    from ...File2 import (      # Comment 1
                        obj3 as Obj3,           # Comment 2
                        obj4,
                                                # Comment 3
                        obj5                    # Comment 4
                        as                      # Comment 5
                        Obj5                    # Comment 6
                    )
                    """,
                ),
                self._root_file1 : "",
                self._file2 : "",
            }

        result = PatchAndExecute(
            content,
            [self._filename],
            [self._root1],
        )

        result = result[self._filename]

        assert str(result) == textwrap.dedent(
            """\
            <Root>
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(0, 4), match='from'>>> ws:None [1, 1 -> 1, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(5, 10), match='File1'>>> ws:(4, 5) [1, 6 -> 1, 11]
                        'import' <<Regex: <_sre.SRE_Match object; span=(11, 17), match='import'>>> ws:(10, 11) [1, 12 -> 1, 18]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(18, 19), match='('>>> ws:(17, 18) [1, 19 -> 1, 20]
                                Items
                                    Or: [Renamed, <name>]
                                        <name> <<Regex: <_sre.SRE_Match object; span=(19, 23), match='obj1'>>> ws:None [1, 20 -> 1, 24]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=','>>> ws:None [1, 24 -> 1, 25]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(25, 29), match='obj2'>>> ws:(24, 25) [1, 26 -> 1, 30]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(29, 30), match=')'>>> ws:None [1, 30 -> 1, 31]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<30, 32>> ws:None !Ignored! [1, 31 -> 3, 1]
                1.0.0 Grammar
                    Import
                        'from' <<Regex: <_sre.SRE_Match object; span=(32, 36), match='from'>>> ws:None [3, 1 -> 3, 5]
                        <name> <<Regex: <_sre.SRE_Match object; span=(37, 45), match='...File2'>>> ws:(36, 37) [3, 6 -> 3, 14]
                        'import' <<Regex: <_sre.SRE_Match object; span=(46, 52), match='import'>>> ws:(45, 46) [3, 15 -> 3, 21]
                        Or: [Grouped Items, Items]
                            Grouped Items
                                '(' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='('>>> ws:(52, 53) [3, 22 -> 3, 23]
                                Comment <<Regex: <_sre.SRE_Match object; span=(60, 71), match='# Comment 1'>>> ws:(54, 60) !Ignored! [3, 29 -> 3, 40]
                                Newline+ <<71, 72>> ws:None !Ignored! [3, 40 -> 4, 1]
                                Indent <<72, 76, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                                Items
                                    Or: [Renamed, <name>]
                                        Renamed
                                            <name> <<Regex: <_sre.SRE_Match object; span=(76, 80), match='obj3'>>> ws:None [4, 5 -> 4, 9]
                                            'as' <<Regex: <_sre.SRE_Match object; span=(81, 83), match='as'>>> ws:(80, 81) [4, 10 -> 4, 12]
                                            <name> <<Regex: <_sre.SRE_Match object; span=(84, 88), match='Obj3'>>> ws:(83, 84) [4, 13 -> 4, 17]
                                    Repeat: (Comma and Statement, 0, None)
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(88, 89), match=','>>> ws:None [4, 17 -> 4, 18]
                                            Comment <<Regex: <_sre.SRE_Match object; span=(100, 111), match='# Comment 2'>>> ws:(89, 100) !Ignored! [4, 29 -> 4, 40]
                                            Newline+ <<111, 112>> ws:None !Ignored! [4, 40 -> 5, 1]
                                            Or: [Renamed, <name>]
                                                <name> <<Regex: <_sre.SRE_Match object; span=(116, 120), match='obj4'>>> ws:None [5, 5 -> 5, 9]
                                        Comma and Statement
                                            ',' <<Regex: <_sre.SRE_Match object; span=(120, 121), match=','>>> ws:None [5, 9 -> 5, 10]
                                            Newline+ <<121, 122>> ws:None !Ignored! [5, 10 -> 6, 1]
                                            Indent <<122, 150, (28)>> ws:None !Ignored! [6, 1 -> 6, 29]
                                            Comment <<Regex: <_sre.SRE_Match object; span=(150, 161), match='# Comment 3'>>> ws:None !Ignored! [6, 29 -> 6, 40]
                                            Newline+ <<161, 162>> ws:None !Ignored! [6, 40 -> 7, 1]
                                            Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 5]
                                            Or: [Renamed, <name>]
                                                Renamed
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(166, 170), match='obj5'>>> ws:None [7, 5 -> 7, 9]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(190, 201), match='# Comment 4'>>> ws:(170, 190) !Ignored! [7, 29 -> 7, 40]
                                                    Newline+ <<201, 202>> ws:None !Ignored! [7, 40 -> 8, 1]
                                                    'as' <<Regex: <_sre.SRE_Match object; span=(206, 208), match='as'>>> ws:None [8, 5 -> 8, 7]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(230, 241), match='# Comment 5'>>> ws:(208, 230) !Ignored! [8, 29 -> 8, 40]
                                                    Newline+ <<241, 242>> ws:None !Ignored! [8, 40 -> 9, 1]
                                                    <name> <<Regex: <_sre.SRE_Match object; span=(246, 250), match='Obj5'>>> ws:None [9, 5 -> 9, 9]
                                                    Comment <<Regex: <_sre.SRE_Match object; span=(270, 281), match='# Comment 6'>>> ws:(250, 270) !Ignored! [9, 29 -> 9, 40]
                                    Newline+ <<281, 282>> ws:None !Ignored! [9, 40 -> 10, 1]
                                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                                    Repeat: (',', 0, 1)
                                        <No children>
                                ')' <<Regex: <_sre.SRE_Match object; span=(282, 283), match=')'>>> ws:None [10, 1 -> 10, 2]
                1.0.0 Grammar
                    Vertical Whitespace
                        Newline+ <<283, 284>> ws:None !Ignored! [10, 2 -> 11, 1]
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
            "obj5" : "Obj5",
        }
