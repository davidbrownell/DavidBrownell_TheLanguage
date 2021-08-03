# ----------------------------------------------------------------------
# |
# |  ComparisonMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 20:34:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ComparisonMethods object"""

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
class ComparisonMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        compareMethods: Optional[List[MethodDefinitionStatement]]=None,
        lessMethods: Optional[List[MethodDefinitionStatement]]=None,
        lessEqualMethods: Optional[List[MethodDefinitionStatement]]=None,
        greaterMethods: Optional[List[MethodDefinitionStatement]]=None,
        greaterEqualMethods: Optional[List[MethodDefinitionStatement]]=None,
        equalMethods: Optional[List[MethodDefinitionStatement]]=None,
        notEqualMethods: Optional[List[MethodDefinitionStatement]]=None,
    ):
        # BugBug: Describe that all can be implemented in terms of compareMethods
        # BugBug: Validate params

        self._compareMethods                = compareMethods
        self._lessMethods                   = lessMethods
        self._lessEqualMethods              = lessEqualMethods
        self._greaterMethods                = greaterMethods
        self._greaterEqualMethods           = greaterEqualMethods
        self._equalMethods                  = equalMethods
        self._notEqualMethods               = notEqualMethods

    # ----------------------------------------------------------------------
    def __class_init__(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        if not self._compareMethods:
            assert class_stmt != ClassType.Primitive, "'Compare' methods must be defined for primitives"

            self._compareMethods = [
                # BugBug
            ]

        if not self._lessMethods:
            self._lessMethods = [
                # BugBug
            ]

        if not self._lessEqualMethods:
            self._lessEqualMethods = [
                # BugBug
            ]

        if not self._greaterMethods:
            self._greaterMethods = [
                # BugBug
            ]

        if not self._greaterEqualMethods:
            self._greaterEqualMethods = [
                # BugBug
            ]

        if not self._equalMethods:
            self._equalMethods = [
                # BugBug
            ]

        if not self._notEqualMethods:
            self._notEqualMethods = [
                # BugBug
            ]

        self.CompareMethods: List[MethodDefinitionStatement] = self._compareMethods; del self._compareMethods
        self.LessMethods: List[MethodDefinitionStatement] = self._lessMethods; del self._lessMethods
        self.LessEqualMethods: List[MethodDefinitionStatement] = self._lessEqualMethods; del self._lessEqualMethods
        self.GreaterMethods: List[MethodDefinitionStatement] = self._greaterMethods; del self._greaterMethods
        self.GreaterEqualMethods: List[MethodDefinitionStatement] = self._greaterEqualMethods; del self._greaterEqualMethods
        self.EqualMethods: List[MethodDefinitionStatement] = self._equalMethods; del self._equalMethods
        self.NotEqualMethods: List[MethodDefinitionStatement] = self._notEqualMethods; del self._notEqualMethods
