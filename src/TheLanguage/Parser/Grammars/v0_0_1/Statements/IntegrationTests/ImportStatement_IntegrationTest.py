# ----------------------------------------------------------------------
# |
# |  ImportStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-15 10:03:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for ImportStatement.py"""

import os
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ImportStatement import *
    from ...Common.AutomatedTests import PatchAndExecute


# ----------------------------------------------------------------------
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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(result) \
            .replace(
                self._root2,
                "<generic_root>",
            ) \
            .replace(
                os.path.sep,
                "/",
            ) == ResultsFromFile()

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

        assert str(ex) == "The relative path '{}' is not valid for the origin '{}'.".format(dots, _script_dir)
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
