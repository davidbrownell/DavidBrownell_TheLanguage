# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------
"""\
Contains the Error interface.
"""


import copy
from enum import auto, Enum

from CommonEnvironmentEx.Package import InitRelativeImports

with InitRelativeImports():
    from ..CommonLibrary import HashLib_TheLanguage as HashLib
    from ..CommonLibrary.Int_TheLanguage import *
    from ..CommonLibrary.List_TheLanguage import List
    # from ..CommonLibrary.Num_TheLanguage import Num
    # from ..CommonLibrary.Queue_TheLanguage import Queue
    from ..CommonLibrary.Range_TheLanguage import *
    from ..CommonLibrary.Set_TheLanguage import Set
    from ..CommonLibrary.Stack_TheLanguage import Stack
    from ..CommonLibrary.String_TheLanguage import String



# Visibility: public
# ClassModifier: immutable
# ClassType: Exception
class Error(Exception):
    """\
    Base class for all lexer-related errors.
    """

    def __init__(self, *args, **kwargs):
        Error._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # line, column

        # No bases

        # line
        if "line" in kwargs:
            self.line = kwargs.pop("line")
        elif args:
            self.line = args.pop(0)
        else:
            raise Exception("line was not provided")

        # column
        if "column" in kwargs:
            self.column = kwargs.pop("column")
        elif args:
            self.column = args.pop(0)
        else:
            raise Exception("column was not provided")

        self._Init_d8d2baa6dc334a219a57995ee9bd8c42_()

    def __eq__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) == 0

    def __ne__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other) != 0

    def __lt__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) < 0

    def __le__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) <= 0

    def __gt__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) > 0

    def __ge__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) >= 0

    @classmethod
    def __Compare__(cls, a, b):
        # No bases

        result = cls.__CompareItem__(a.line, b.line)
        if result is not None: return result

        result = cls.__CompareItem__(a.column, b.column)
        if result is not None: return result

        return 0

    @classmethod
    def __CompareItem__(cls, a, b):
        if a is None and b is None:
            return None

        if a is None: return -1
        if b is None: return 1

        try:
            if a < b: return -1
            if a > b: return 1
        except TypeError:
            a = id(a)
            b = id(b)

            if a < b: return -1
            if a > b: return 1

        return None

    def _Init_d8d2baa6dc334a219a57995ee9bd8c42_(self):
        pass

    # Return Type: String
    def _ToString_d8d2baa6dc334a219a57995ee9bd8c42_(self):
        return self._GetMessageTemplate().format(**self.__dict__, )

    # Return Type: String
    def _GetMessageTemplate(self):
        raise Exception("Abstract/Deferred method")

    @property
    def Line(self): return self.line
    @property
    def Column(self): return self.column
    def __str__(self):
        return self._ToString_d8d2baa6dc334a219a57995ee9bd8c42_()
