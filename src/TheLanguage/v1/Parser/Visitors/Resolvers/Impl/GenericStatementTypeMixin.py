# ----------------------------------------------------------------------
# |
# |  GenericStatementTypeMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-29 09:12:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GenericStatementTypeMixin object"""

import os

from typing import Generic, TypeVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .GenericTypeResolver import GenericTypeResolver

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.GenericTypes import GenericStatementType


# ----------------------------------------------------------------------
MixinT                                      = TypeVar("MixinT")

class GenericStatementTypeMixin(GenericStatementType, Generic[MixinT]):  # pylint: disable=abstract-method
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_resolver: GenericTypeResolver,
    ):
        GenericStatementType.__init__(self, type_resolver.namespace.parser_info)  # type: ignore

        self._type_resolver                 = type_resolver

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> MixinT:
        return self._parser_info  # type: ignore

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(
        self,
        parser_info: MixinT,
    ) -> ConcreteType:
        return self._type_resolver.CreateConcreteType(parser_info)  # type: ignore
