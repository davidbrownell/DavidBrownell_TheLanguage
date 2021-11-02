# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:10:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Types and methods common across automated unit tests"""

import os
import textwrap

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
    from ..ThreadPool import CreateThreadPool


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock():
    mock = CoroutineMock()
    mock._thread_pool = CreateThreadPool(20)

    # ----------------------------------------------------------------------
    def GetParentStatementNode(node):
        if (
            node is None
            or node.Type is None
            or "Statement" in node.Type.Name
        ):
            return node

        return node.Parent

    # ----------------------------------------------------------------------

    mock.GetParentStatementNode = GetParentStatementNode

    mock.Enqueue = mock._thread_pool.EnqueueAsync

    mock.OnPushScopeAsync = CoroutineMock()
    mock.OnPopScopeAsync = CoroutineMock()
    mock.OnInternalPhraseAsync = CoroutineMock()

    return mock


# ----------------------------------------------------------------------
def CreateIterator(
    content: str,
) -> NormalizedIterator:
    # ----------------------------------------------------------------------
    def SuppressIndentation(offset_start, offset_end, content_start, content_end):
        return (
            content_start != content_end
            and content[content_start] == "#"
        )

    # ----------------------------------------------------------------------

    return NormalizedIterator.FromNormalizedContent(
        Normalize(
            content,
            suppress_indentation_func=SuppressIndentation,
        ),
    )


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
                '{}) {}, "{}"'.format(
                    index,
                    method_name,
                    method_call[1][1].Name,
                ),
            )

        elif method_name == "EndPhrase":
            contents.append(
                '{}) {}, "{}" [{}]'.format(
                    index,
                    method_name,
                    method_call[1][1].Name,
                    method_call[1][2],
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
                    StringHelpers.LeftJustify(method_call[1][1].ToYamlString(), 4),
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
                    StringHelpers.LeftJustify(method_call[0][0].ToYamlString(), 4),
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
                    StringHelpers.LeftJustify(method_call[1][0].ToYamlString().rstrip(), 4),
                ).rstrip(),
            )

    return "{}\n".format("\n".join(contents))
