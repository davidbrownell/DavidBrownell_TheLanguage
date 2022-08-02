# ----------------------------------------------------------------------
# |
# |  ConstrainedFuncDefinitionType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-08-02 08:23:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConstrainedFuncDefinitionType object"""

import os

from typing import List, Optional, Tuple, TYPE_CHECKING

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ConstrainedType import ConstrainedType

    from ...Common.MutabilityModifier import MutabilityModifier

    from ....Error import Error, ErrorException

    if TYPE_CHECKING:
        from .ConcreteFuncDefinitionType import ConcreteFuncDefinitionType  # pylint: disable=unused-import


# ----------------------------------------------------------------------
class ConstrainedFuncDefinitionType(ConstrainedType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_type: "ConcreteFuncDefinitionType",
    ):
        super(ConstrainedFuncDefinitionType, self).__init__(concrete_type, None)

        errors: List[Error] = []

        # Return Type
        return_type_info: Optional[Tuple[ConstrainedType, Optional[MutabilityModifier]]] = None

        if concrete_type.return_type_info is not None:
            try:
                assert concrete_type.parser_info.return_type is not None
                return_type_info = (
                    concrete_type.return_type_info[0].CreateConstrainedType(concrete_type.parser_info.return_type),
                    concrete_type.return_type_info[1],
                )

            except ErrorException as ex:
                errors += ex.errors

        # Parameters
        parameter_infos: Optional[List[Tuple[ConstrainedType, Optional[MutabilityModifier]]]] = None

        if concrete_type.parameter_infos is not None:
            parameter_infos = []

            assert not isinstance(concrete_type.parser_info.parameters, bool)

            for concrete_parameter_info, parameter_parser_info in zip(
                concrete_type.parameter_infos,
                concrete_type.parser_info.parameters.EnumParameters(),
            ):
                try:
                    parameter_infos.append(
                        (
                            concrete_parameter_info[0].CreateConstrainedType(parameter_parser_info.type),
                            concrete_parameter_info[1],
                        ),
                    )
                except ErrorException as ex:
                    errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        # Commit
        self.return_type_info = return_type_info
        self.parameter_infos = parameter_infos
