# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-08 01:07:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Types and methods common across automatedunit tests"""

import asyncio
import os
import textwrap

from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from asynctest import CoroutineMock
import pytest

import CommonEnvironment
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = CoroutineMock()
    mock._thread_pool_executor = ThreadPoolExecutor(max_workers=10)

    # ----------------------------------------------------------------------
    def Enqueue(funcs):
        loop = asyncio.get_event_loop()

        return [
            loop.run_in_executor(mock._thread_pool_executor, func)
            for func in funcs
        ]

    # ----------------------------------------------------------------------

    mock.Enqueue = Enqueue

    mock.OnIndentAsync = CoroutineMock()
    mock.OnDedentAsync = CoroutineMock()
    mock.OnInternalPhraseAsync = CoroutineMock()

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

        if method_name == "StartPhrase":
            contents.append(
                "{}) {}, {}".format(
                    index,
                    method_name,
                    ", ".join(['"{}"'.format(phrase.Name) for phrase in method_call[1][1]]),
                ),
            )

        elif method_name == "EndPhrase":
            contents.append(
                "{}) {}, {}".format(
                    index,
                    method_name,
                    ", ".join(
                        [
                            '"{}" [{}]'.format(phrase.Name, result)
                            for phrase, result in method_call[1][1]
                        ],
                    ),
                ),
            )

        elif method_name == "OnPhraseCompleteAsync":
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

        elif method_name == "GetDynamicPhrases":
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
