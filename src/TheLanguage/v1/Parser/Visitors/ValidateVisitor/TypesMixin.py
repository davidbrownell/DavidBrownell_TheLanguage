# ----------------------------------------------------------------------
# |
# |  TypesMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 13:45:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypesMixin object"""

import os

from contextlib import contextmanager

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...ParserInfos.Types.StandardTypeParserInfo import StandardTypeParserInfo, StandardTypeItemParserInfo
    from ...ParserInfos.Types.TupleTypeParserInfo import TupleTypeParserInfo
    from ...ParserInfos.Types.VariantTypeParserInfo import VariantTypeParserInfo


# ----------------------------------------------------------------------
class TypesMixin(BaseMixin):
    # ----------------------------------------------------------------------
    # |  StandardTypeParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnStandardTypeParserInfo(
        self,
        parser_info: StandardTypeParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStandardTypeItemParserInfo(
        self,
        parser_info: StandardTypeItemParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  TupleTypeParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleTypeParserInfo(
        self,
        parser_info: TupleTypeParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  VariantTypeParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantTypeParserInfo(
        self,
        parser_info: VariantTypeParserInfo,
    ):
        yield
