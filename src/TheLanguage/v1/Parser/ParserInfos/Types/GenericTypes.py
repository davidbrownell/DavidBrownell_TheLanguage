# ----------------------------------------------------------------------
# |
# |  GenericType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 13:48:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericType object"""

import os

from typing import Optional, TYPE_CHECKING

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType

    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait

    if TYPE_CHECKING:
        from .ConcreteType import ConcreteType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class GenericType(Interface.Interface):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ParserInfo,
        is_default_initializable: bool,
    ):
        self._parser_info                   = parser_info
        self.is_default_initializable       = is_default_initializable

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def parser_info(self):
        """Returns the parser info with the correct type"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsSameType(
        other: "GenericType",
    ) -> bool:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def CreateDefaultConcreteType(self) -> "ConcreteType":
        assert self.is_default_initializable
        return self._CreateDefaultConcreteTypeImpl()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def CreateConcreteType(
        parser_info: ExpressionParserInfo,
    ) -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateDefaultConcreteTypeImpl() -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class GenericExpressionType(GenericType):
    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> "ConcreteType":
        assert parser_info is self.parser_info, (parser_info, self.parser_info)
        return self._CreateConcreteTypeImpl()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> "ConcreteType":
        return self.CreateConcreteType(
            self.parser_info,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteTypeImpl() -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class GenericStatementType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: StatementParserInfo,
    ):
        super(GenericStatementType, self).__init__(
            parser_info,
            (
                not isinstance(parser_info, TemplatedStatementTrait)
                or parser_info.templates is None
                or parser_info.templates.is_default_initializable
            ),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> "ConcreteType":
        assert isinstance(parser_info, FuncOrTypeExpressionParserInfo), parser_info
        return self._CreateConcreteTypeImpl(parser_info)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> "ConcreteType":
        assert self.is_default_initializable
        assert isinstance(self._parser_info, NamedTrait), self._parser_info

        return self.CreateConcreteType(
            FuncOrTypeExpressionParserInfo.Create(
                parser_info_type=ParserInfoType.Standard,
                regions=[
                    self._parser_info.regions__.self__,
                    self._parser_info.regions__.name,
                    None,
                ],
                value=self._parser_info.name,
                templates=None,
                constraints=None,
                mutability_modifier=None,
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _CreateConcreteTypeImpl(
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> "ConcreteType":
        raise Exception("Abstract method")  # pragma: no cover
