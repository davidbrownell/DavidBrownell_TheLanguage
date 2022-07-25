# ----------------------------------------------------------------------
# |
# |  NoneTypes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 14:01:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains None-related types"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from .....ParserInfos.Types.ConcreteType import ConcreteType
    from .....ParserInfos.Types.ConstrainedType import ConstrainedType
    from .....ParserInfos.Types.GenericType import GenericType


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class GenericNoneType(GenericType):
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        parser_info: NoneExpressionParserInfo,
    ):
        return cls(parser_info)

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> NoneExpressionParserInfo:
        result = super(GenericNoneType, self).parser_info
        assert isinstance(result, NoneExpressionParserInfo), result

        return result

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> "ConcreteNoneType":
        return ConcreteNoneType(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteNoneType(ConcreteType):
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> "ConstrainedNoneType":
        return ConstrainedNoneType(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConstrainedNoneType(ConstrainedType):
    pass
