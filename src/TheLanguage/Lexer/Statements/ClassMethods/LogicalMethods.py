# ----------------------------------------------------------------------
# |
# |  LogicalMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 20:07:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LogicalMethods object"""

import os

from typing import Any, cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import MethodDefinitionStatement


# ----------------------------------------------------------------------
class LogicalMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        andMethods: Optional[List[MethodDefinitionStatement]]=None,
        orMethods: Optional[List[MethodDefinitionStatement]]=None,
        notMethod: Optional[MethodDefinitionStatement]=None,
    ):
        # BugBug: Validate params

        self._andMethods                    = andMethods
        self._orMethods                     = orMethods
        self._notMethod                     = notMethod

    # ----------------------------------------------------------------------
    def Init(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        if not self._andMethods:
            assert class_stmt.Type in [
                ClassType.Primitive,
                ClassType.Class,
                ClassType.Mixin,
                ClassType.Exception,
            ], (
                "'AndMethod' can not be defined for this class type",
                class_stmt.ClassType,
            )

            self._andMethods = [
                # BugBug
            ]

        if not self._orMethods:
            assert class_stmt.Type in [
                ClassType.Primitive,
                ClassType.Class,
                ClassType.Mixin,
                ClassType.Exception,
            ], (
                "'OrMethod' can not be defined for this class type",
                class_stmt.ClassType,
            )

            self._orMethods = [
                # BugBug
            ]

        if not self._notMethod:
            assert class_stmt.Type in [
                ClassType.Primitive,
                ClassType.Class,
                ClassType.Mixin,
                ClassType.Exception,
            ], (
                "'NotMethod' can not be defined for this class type",
                class_stmt.ClassType,
            )

            self._notMethod = None # BugBug

        self.AndMethods: List[MethodDefinitionStatement] = self._andMethods; del self._andMethods
        self.OrMethods: List[MethodDefinitionStatement] = self._orMethods; del self._orMethods
        self.NotMethod: MethodDefinitionStatement = self._notMethod; del self._notMethod
