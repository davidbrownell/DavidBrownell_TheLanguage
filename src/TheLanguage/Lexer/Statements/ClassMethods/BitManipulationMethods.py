# ----------------------------------------------------------------------
# |
# |  BitManipulationMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 21:08:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BitManipulationMethods object"""

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
class BitManipulationMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,

        bitShiftLeftMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitShiftRightMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitAndMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitOrMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitXorMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitComplimentMethod: Optional[MethodDefinitionStatement]=None,

        bitShiftLeftInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitShiftRightInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitAndInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitOrInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        bitXorInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
    ):
        # BugBug: Validate params

        self._bitShiftLeftMethods           = bitShiftLeftMethods
        self._bitShiftRightMethods          = bitShiftRightMethods
        self._bitAndMethods                 = bitAndMethods
        self._bitOrMethods                  = bitOrMethods
        self._bitXorMethods                 = bitXorMethods
        self._bitComplimentMethod           = bitComplimentMethod

        self._bitShiftLeftInplaceMethods    = bitShiftLeftInplaceMethods
        self._bitShiftRightInplaceMethods   = bitShiftRightInplaceMethods
        self._bitAndInplaceMethods          = bitAndInplaceMethods
        self._bitOrInplaceMethods           = bitOrInplaceMethods
        self._bitXorInplaceMethods          = bitXorInplaceMethods

    # ----------------------------------------------------------------------
    def __class_init__(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        # BugBug: For which types is this OK?

        if not self._bitShiftLeftInplaceMethods and self._bitShiftLeftMethods:
            pass # BugBug

        if not self._bitShiftRightInplaceMethods and self._bitShiftRightMethods:
            pass # BugBug

        if not self._bitAndInplaceMethods and self._bitAndMethods:
            pass # BugBug

        if not self._bitOrInplaceMethods and self._bitOrMethods:
            pass # BugBug

        if not self._bitXorInplaceMethods and self._bitXorMethods:
            pass # BugBug

        self.BitShiftLeftMethods = self._bitShiftLeftMethods; del self._bitShiftLeftMethods
        self.BitShiftRightMethods = self._bitShiftRightMethods; del self._bitShiftRightMethods
        self.BitAndMethods = self._bitAndMethods; del self._bitAndMethods
        self.BitOrMethods = self._bitOrMethods; del self._bitOrMethods
        self.BitXorMethods = self._bitXorMethods; del self._bitXorMethods
        self.BitComplimentMethod = self._bitComplimentMethod; del self._bitComplimentMethod

        self.BitShiftLeftInplaceMethods = self._bitShiftLeftInplaceMethods; del self._bitShiftLeftInplaceMethods
        self.BitShiftRightInplaceMethods = self._bitShiftRightInplaceMethods; del self._bitShiftRightInplaceMethods
        self.BitAndInplaceMethods = self._bitAndInplaceMethods; del self._bitAndInplaceMethods
        self.BitOrInplaceMethods = self._bitOrInplaceMethods; del self._bitOrInplaceMethods
        self.BitXorInplaceMethods = self._bitXorInplaceMethods; del self._bitXorInplaceMethods
