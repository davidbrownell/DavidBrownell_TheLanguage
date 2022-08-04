# ----------------------------------------------------------------------
# |
# |  CreateDefaultExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-08-01 15:44:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used to create a default expression for a StatementParserInfo instance"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ....ParserInfos.ParserInfo import ParserInfoType
    from ....ParserInfos.Traits.NamedTrait import NamedTrait

    from ....ParserInfos.Statements.StatementParserInfo import StatementParserInfo


# ----------------------------------------------------------------------
def CreateDefaultExpressionParserInfo(
    parser_info: StatementParserInfo,
) -> FuncOrTypeExpressionParserInfo:
    assert isinstance(parser_info, NamedTrait), parser_info

    return FuncOrTypeExpressionParserInfo.Create(
        parser_info_type=ParserInfoType.Standard,
        regions=[
            parser_info.regions__.self__,
            parser_info.regions__.name,
            None,
        ],
        value=parser_info.name,
        templates=None,
        constraints=None,
        mutability_modifier=None,
    )
