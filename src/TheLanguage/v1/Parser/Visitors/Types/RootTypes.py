# ----------------------------------------------------------------------
# |
# |  RootTypes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 15:37:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the root type objects"""

import os

from typing import Generator

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeResolver import TypeResolver

    from ..Namespaces import ImportNamespace, ParsedNamespace

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.GenericType import GenericType

    # The following imports aren't used, but are necessary to work around wonkiness with circular dependencies
    from . import ClassTypes                # pylint: disable=unused-import
    from . import FuncDefinitionTypes       # pylint: disable=unused-import
    from . import TypeAliasTypes            # pylint: disable=unused-import


# ----------------------------------------------------------------------
class RootConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: TypeResolver,
        parser_info: RootStatementParserInfo,
    ):
        super(RootConcreteType, self).__init__(
            parser_info,
            is_default_initializable=True,
        )

        self._type_resolver                 = type_resolver

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> RootStatementParserInfo:
        assert isinstance(self._parser_info, RootStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsMatch(*args, **kwargs):
        raise Exception("This should never be invoked for this type")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsCovariant(*args, **kwargs):
        raise Exception("This should never be invoked for this type")

    # ----------------------------------------------------------------------
    def EnumGenericTypes(self) -> Generator[GenericType, None, None]:
        for namespace_or_namespaces in self._type_resolver.namespace.EnumChildren():
            if isinstance(namespace_or_namespaces, list):
                namespaces = namespace_or_namespaces
            else:
                namespaces = [namespace_or_namespaces, ]

            for namespace in namespaces:
                if isinstance(namespace, ImportNamespace):
                    continue

                assert isinstance(namespace, ParsedNamespace), namespace
                yield self._type_resolver.GetOrCreateNestedGenericTypeViaNamespace(namespace)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _FinalizePass1Impl() -> None:
        raise Exception("This should never be invoked for this type")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _FinalizePass2Impl() -> None:
        raise Exception("This should never be invoked for this type")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateConstrainedTypeImpl(*args, **kwargs) -> None:  # pylint: disable=unused-argument
        raise Exception("This should never be invoked for this type")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateDefaultConstrainedTypeImpl(*args, **kwargs) -> None:  # pylint: disable=unused-argument
        raise Exception("This should never be invoked for this type")
