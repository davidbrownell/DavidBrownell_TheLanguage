# ----------------------------------------------------------------------
# |
# |  RequiredMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 17:23:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RequiredMethods object"""

import os

from typing import Any, cast, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CreateMethod

    from ..MethodDefinitionStatement import MethodDefinitionStatement, MethodType


# ----------------------------------------------------------------------
class RequiredMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        toBoolMethod: Optional[MethodDefinitionStatement]=None,
        toStringMethod: Optional[MethodDefinitionStatement]=None,
        reprMethod: Optional[MethodDefinitionStatement]=None,
        cloneMethod: Optional[MethodDefinitionStatement]=None,
        serializeMethod: Optional[MethodDefinitionStatement]=None,
    ):
        # BugBug: Validate params

        self._toBoolMethod                  = toBoolMethod
        self._toStringMethod                = toStringMethod
        self._reprMethod                    = reprMethod
        self._cloneMethod                   = cloneMethod
        self._serializeMethod               = serializeMethod

    # ----------------------------------------------------------------------
    def __class_init__(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        if self._toBoolMethod is None:
            assert class_stmt.Type != ClassType.Primitive, "Primitive classes must define this value"

            self._toBoolMethod = CreateMethod(
                "ToBool",
                "bool",
                [], # BugBug
                [], # BugBug
                is_mutable=False,
            )

        if self._toStringMethod is None:
            assert class_stmt.Type != ClassType.Primitive, "Primitive classes must define this value"

            pass # BugBug

        if self._reprMethod is None:
            assert class_stmt.Type != ClassType.Primitive, "Primitive classes must define this value"

            pass # BugBug

        if self._cloneMethod is None:
            assert class_stmt.Type != ClassType.Primitive, "Primitive classes must define this value"

            pass # BugBug

        if self._serializeMethod is None:
            assert class_stmt.Type != ClassType.Primitive, "Primitive classes must define this value"

            pass # BugBug

        self.ToBoolMethod: MethodDefinitionStatement = self._toBoolMethod; del self._toBoolMethod
        self.ToStringMethod: MethodDefinitionStatement = self._toStringMethod; del self._toStringMethod
        self.ReprMethod: MethodDefinitionStatement = self._reprMethod; del self._reprMethod
        self.CloneMethod: MethodDefinitionStatement = self._cloneMethod; del self._cloneMethod
        self.SerializeMethod: MethodDefinitionStatement = self._serializeMethod; del self._serializeMethod
