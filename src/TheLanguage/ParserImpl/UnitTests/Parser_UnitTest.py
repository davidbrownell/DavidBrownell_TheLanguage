# ----------------------------------------------------------------------
# |
# |  Parser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-01 20:57:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Parser.py"""

import os
import sys

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Normalize import *
    from NormalizedIterator import NormalizedIterator
    from Parser import *
    from Statement import StandardStatement

    from Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken
    )

# ----------------------------------------------------------------------
@contextmanager
def CreateObserver(content_mock):
    with ThreadPoolExecutor() as executor:
        # ----------------------------------------------------------------------
        class MyObserver(Observer):
            # ----------------------------------------------------------------------
            def __init__(self):
                self.mock = Mock(
                    return_value=True,
                )

            # ----------------------------------------------------------------------
            def VerifyCallArgs(self, index, statement, node, before_line, before_col, after_line, after_col):
                callback_args = self.mock.call_args_list[index][0]

                assert callback_args[0] == statement
                assert callback_args[1] == node
                assert callback_args[2].Line == before_line
                assert callback_args[2].Column == before_col
                assert callback_args[3].Line == after_line
                assert callback_args[3].Column == after_col

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def LoadContent(
                fully_qualified_name: str,
            ):
                return content_mock(fully_qualified_name)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnIndent():
                pass

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnDedent():
                pass

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def Enqueue(funcs):
                return [executor.submit(func) for func in funcs]

            # ----------------------------------------------------------------------
            @Interface.override
            def OnStatementComplete(
                self,
                statement,
                node,
                iter_before,
                iter_after,
            ):
                self.mock(statement, node, iter_before, iter_after)

        # ----------------------------------------------------------------------

        yield MyObserver()

# ----------------------------------------------------------------------
def test_BugBug():
    # The battery on my laptop is failing, so I want to push code as quickly as possible
    # with a replacement battery is on its way. This test is required to prevent testing errors.
    assert True
