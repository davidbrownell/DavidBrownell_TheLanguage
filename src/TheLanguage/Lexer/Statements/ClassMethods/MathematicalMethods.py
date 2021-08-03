# ----------------------------------------------------------------------
# |
# |  MathematicalMethods.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-02 20:51:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MathematicalMethods object"""

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
class MathematicalMethods(object):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,

        addMethods: Optional[List[MethodDefinitionStatement]]=None,
        subtractMethods: Optional[List[MethodDefinitionStatement]]=None,
        multiplyMethods: Optional[List[MethodDefinitionStatement]]=None,
        divideDecimalMethods: Optional[List[MethodDefinitionStatement]]=None,
        divideIntegerMethods: Optional[List[MethodDefinitionStatement]]=None,
        powerMethods: Optional[List[MethodDefinitionStatement]]=None,
        moduloMethods: Optional[List[MethodDefinitionStatement]]=None,
        positiveMethod: Optional[MethodDefinitionStatement]=None,
        negativeMethod: Optional[MethodDefinitionStatement]=None,

        addInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        subtractInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        multiplyInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        divideDecimalInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        divideIntegerInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        powerInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
        moduloInplaceMethods: Optional[List[MethodDefinitionStatement]]=None,
    ):
        # BugBug: Validate params
        self._addMethods                    = addMethods
        self._subtractMethods               = subtractMethods
        self._multiplyMethods               = multiplyMethods
        self._divideDecimalMethods          = divideDecimalMethods
        self._divideIntegerMethods          = divideIntegerMethods
        self._powerMethods                  = powerMethods
        self._moduloMethods                 = moduloMethods
        self._positiveMethod                = positiveMethod
        self._negativeMethod                = negativeMethod

        self._addInplaceMethods             = addInplaceMethods
        self._subtractInplaceMethods        = subtractInplaceMethods
        self._multiplyInplaceMethods        = multiplyInplaceMethods
        self._divideDecimalInplaceMethods   = divideDecimalInplaceMethods
        self._divideIntegerInplaceMethods   = divideIntegerInplaceMethods
        self._powerInplaceMethods           = powerInplaceMethods
        self._moduloInplaceMethods          = moduloInplaceMethods

    # ----------------------------------------------------------------------
    def __class_init__(
        self,
        class_stmt: Any, # Not 'ClassStatement' to avoid circular imports
    ):
        with InitRelativeImports():
            from ..ClassStatement import ClassStatement, ClassType

        class_stmt = cast(ClassStatement, class_stmt)

        # BugBug: For which types is this OK?

        if not self._addInplaceMethods and self._addMethods:
            pass # BugBug

        if not self._subtractInplaceMethods and self._subtractMethods:
            pass # BugBug

        if not self._multiplyInplaceMethods and self._multiplyMethods:
            pass # BugBug

        if not self._divideDecimalInplaceMethods and self._divideDecimalMethods:
            pass # BugBug

        if not self._divideIntegerInplaceMethods and self._divideIntegerMethods:
            pass # BugBug

        if not self._powerInplaceMethods and self._powerMethods:
            pass # BugBug

        if not self._moduloInplaceMethods and self._moduloMethods:
            pass # BugBug

        self.AddMethods = self._addMethods; del self._addMethods
        self.SubtractMethods = self._subtractMethods; del self._subtractMethods
        self.MultiplyMethods = self._multiplyMethods; del self._multiplyMethods
        self.DivideDecimalMethods = self._divideDecimalMethods; del self._divideDecimalMethods
        self.DivideIntegerMethods = self._divideIntegerMethods; del self._divideIntegerMethods
        self.PowerMethods = self._powerMethods; del self._powerMethods
        self.ModuloMethods = self._moduloMethods; del self._moduloMethods
        self.PositiveMethod = self._positiveMethod; del self._positiveMethod
        self.NegativeMethod = self._negativeMethod; del self._negativeMethod

        self.AddInplaceMethods = self._addInplaceMethods; del self._addInplaceMethods
        self.SubtractInplaceMethods = self._subtractInplaceMethods; del self._subtractInplaceMethods
        self.MultiplyInplaceMethods = self._multiplyInplaceMethods; del self._multiplyInplaceMethods
        self.DivideDecimalInplaceMethods = self._divideDecimalInplaceMethods; del self._divideDecimalInplaceMethods
        self.DivideIntegerInplaceMethods = self._divideIntegerInplaceMethods; del self._divideIntegerInplaceMethods
        self.PowerInplaceMethods = self._powerInplaceMethods; del self._powerInplaceMethods
        self.ModuloInplaceMethods = self._moduloInplaceMethods; del self._moduloInplaceMethods
