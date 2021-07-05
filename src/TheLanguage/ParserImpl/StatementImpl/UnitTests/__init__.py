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

import pytest

from asynctest import CoroutineMock

import CommonEnvironment

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
def MethodCallsToString(parse_mock) -> str:
    return textwrap.dedent(
        """\
        {}
        """,
    ).format(
        "\n".join(
            [
                "{}, {}, {}".format(
                    index,
                    method_call[0],
                    str(method_call[1][0]),
                )
                for index, method_call in enumerate(parse_mock.method_calls)
            ],
        ),
    )

# ----------------------------------------------------------------------
def InternalStatementMethodCallToTuple(
    parse_mock,
    index,
    use_statement_name=False,
):
    return (
        parse_mock.method_calls[index][1][1].Name if use_statement_name else parse_mock.method_calls[index][1][1],
        parse_mock.method_calls[index][1][2],
        parse_mock.method_calls[index][1][3].Offset,
        parse_mock.method_calls[index][1][4].Offset,
    )
