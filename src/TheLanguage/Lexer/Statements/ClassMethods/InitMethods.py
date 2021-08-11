# ----------------------------------------------------------------------
# |
# |  InitMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 19:51:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementMethods object"""

import os

from typing import Any, cast, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import MethodDefinitionStatement


# ----------------------------------------------------------------------
class InitMethods(object):
    """\
    TODO: Describe
    """

    # BugBug: Add destructor method

    # ----------------------------------------------------------------------
    def __init__(
        self,
        preInitMethod: Optional[MethodDefinitionStatement]=None,
        postInitMethod: Optional[MethodDefinitionStatement]=None,
    ):
        # BugBug: Validate params

        if preInitMethod:
            assert not preInitMethod.ReturnType

            assert not preInitMethod.PositionalParameters
            assert not preInitMethod.AnyParameters
            assert not preInitMethod.KeywordParameters

        if postInitMethod:
            assert not postInitMethod.ReturnType

            assert not postInitMethod.PositionalParameters
            assert not postInitMethod.AnyParameters
            assert not postInitMethod.KeywordParameters

        self._preInitMethod                 = preInitMethod
        self._postInitMethod                = postInitMethod

    # ----------------------------------------------------------------------
    def Init(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        if self._preInitMethod or self._postInitMethod:
            assert class_stmt.Type in [
                ClassType.Primitive,
                ClassType.Class,
                ClassType.Mixin,
                ClassType.Exception,
            ], (
                "'PreInitMethod' and 'PostInitMethod' can not be defined for this class type",
                class_stmt.ClassType,
            )

        self.PreInitMethod: Optional[MethodDefinitionStatement] = self._preInitMethod; del self._preInitMethod
        self.PostInitMethod: Optional[MethodDefinitionStatement] = self._postInitMethod; del self._postInitMethod
