# ----------------------------------------------------------------------
# |
# |  ContainerMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 20:22:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ContainerMethods object"""

import os

from typing import Any, cast

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..MethodDefinitionStatement import MethodDefinitionStatement


# ----------------------------------------------------------------------
class ContainerMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        containsMethod: MethodDefinitionStatement=None,
        lenMethod: MethodDefinitionStatement=None,
        iterMethod: MethodDefinitionStatement=None,
        atIterEndMethod: MethodDefinitionStatement=None,
    ):
        # BugBug: Validate params

        self._containsMethod                = containsMethod
        self._lenMethod                     = lenMethod
        self._iterMethod                    = iterMethod
        self._atIterEndMethod               = atIterEndMethod

    # ----------------------------------------------------------------------
    def Init(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        assert class_stmt.Type in [
            ClassType.Class,
        ], (
            "ContainerMethods can only be provided for classes",
            class_stmt.ClassType,
        )

        self.ContainsMethod: MethodDefinitionStatement = self._containsMethod; del self._containsMethod
        self.LenMethod: MethodDefinitionStatement = self._lenMethod; del self._lenMethod
        self.IterMethod: MethodDefinitionStatement = self._iterMethod; del self._iterMethod
        self.AtIterEndMethod: MethodDefinitionStatement = self._atIterEndMethod; del self._atIterEndMethod
