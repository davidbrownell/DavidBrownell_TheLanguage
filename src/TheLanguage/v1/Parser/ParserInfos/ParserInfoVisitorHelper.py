# ----------------------------------------------------------------------
# |
# |  ParserInfoVisitorHelper.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-20 16:20:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParserInfoVisitorHelper object"""

import os
import types

from contextlib import contextmanager
from typing import List, TYPE_CHECKING, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    if TYPE_CHECKING:
        from .ParserInfo import ParserInfo


# ----------------------------------------------------------------------
class ParserInfoVisitorHelper(object):
    """Visitor that provides default implementations for all methods, each of which can be overloaded as needed"""

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnPhrase(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnPhraseDetails(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnPhraseChildren(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        if name.endswith("ParserInfo"):
            return self.__class__._DefaultParserInfoMethod  # pylint: disable=protected-access

        index = name.find("ParserInfo__")
        if index != -1 and index + len("ParserInfo__") + 1 < len(name):
            return types.MethodType(self.__class__._DefaultDetailMethod, self)  # pylint: disable=protected-access

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def _DefaultParserInfoMethod(*args, **kwargs):  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        parser_info_or_infos: Union["ParserInfo", List["ParserInfo"]],
        *,
        include_disabled: bool,
    ):
        if isinstance(parser_info_or_infos, list):
            for parser_info in parser_info_or_infos:
                parser_info.Accept(
                    self,
                    include_disabled=include_disabled,
                )
        else:
            parser_info_or_infos.Accept(
                self,
                include_disabled=include_disabled,
            )
