# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 07:38:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Types and Methods common across unit tests"""

import os
import textwrap

from typing import Optional

import pytest

from asynctest import CoroutineMock

import CommonEnvironment
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Statement import Statement

    from ...Normalize import Normalize
    from ...NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = CoroutineMock()

    mock.OnIndentAsync = CoroutineMock()
    mock.OnDedentAsync = CoroutineMock()
    mock.OnInternalStatementAsync = CoroutineMock()

    return mock


# ----------------------------------------------------------------------
def CreateIterator(
    content: str,
) -> NormalizedIterator:
    return NormalizedIterator(Normalize(content))


# ----------------------------------------------------------------------
def MethodCallsToString(
    parse_mock,
    attribute_name: Optional[str]=None,
) -> str:
    if attribute_name is None:
        attribute_name = "method_calls"
        get_method_name = True
    else:
        get_method_name = False

    contents = []

    for index, method_call in enumerate(getattr(parse_mock, attribute_name)):
        method_name = None

        if get_method_name:
            method_name = method_call[0]

        if method_name == "StartStatement":
            contents.append(
                "{}) {}, {}".format(
                    index,
                    method_name,
                    ", ".join(['"{}"'.format(statement.Name) for statement in method_call[1][1]]),
                ),
            )

        elif method_name == "EndStatement":
            contents.append(
                "{}) {}, {}".format(
                    index,
                    method_name,
                    ", ".join(
                        [
                            '"{}" [{}]'.format(statement.Name, result)
                            for statement, result in method_call[1][1]
                        ],
                    ),
                ),
            )

        elif method_name == "OnStatementCompleteAsync":
            contents.append(
                textwrap.dedent(
                    """\
                    {}) {}, {}, {}, {}
                        {}
                    """,
                ).format(
                    index,
                    method_name,
                    method_call[1][0].Name,
                    method_call[1][2].Offset,
                    method_call[1][3].Offset,
                    StringHelpers.LeftJustify(method_call[1][1].ToString(), 4),
                ).rstrip(),
            )

        elif method_name == "GetDynamicStatements":
            contents.append(
                textwrap.dedent(
                    """\
                    {}) {}, {}
                    """,
                ).format(
                    index,
                    method_name,
                    method_call[0][1],
                ).rstrip(),
            )

        elif method_name is None:
            contents.append(
                textwrap.dedent(
                    """\
                    {}) {}, {}
                        {}
                    """,
                ).format(
                    index,
                    method_call[0][1].Offset,
                    method_call[0][2].Offset,
                    StringHelpers.LeftJustify(method_call[0][0].ToString(), 4),
                ).rstrip(),
            )

        else:
            contents.append(
                textwrap.dedent(
                    """\
                    {}) {}, {}, {}
                        {}
                    """,
                ).format(
                    index,
                    method_name,
                    method_call[1][1].Offset,
                    method_call[1][2].Offset,
                    StringHelpers.LeftJustify(
                        "\n".join([data_item.ToString().rstrip() for data_item in method_call[1][0]]),
                        4,
                    ),
                ).rstrip(),
            )

    return "{}\n".format("\n".join(contents))
