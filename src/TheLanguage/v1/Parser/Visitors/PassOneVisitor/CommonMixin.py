# ----------------------------------------------------------------------
# |
# |  CommonMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-15 07:25:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CommonMixin object"""

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

    from ...ParserInfos.ParserInfo import ParserInfoType

    from ...ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo


# ----------------------------------------------------------------------
class CommonMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnConstraintParametersParserInfo(
        self,
        parser_info: ConstraintParametersParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.Configuration, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.Configuration, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        yield
