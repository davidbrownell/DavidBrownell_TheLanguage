# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------
"""\
Contains the `Phrase` object
"""


import copy
from enum import auto, Enum

from CommonEnvironmentEx.Package import InitRelativeImports

with InitRelativeImports():
    from ...CommonLibrary import HashLib_TheLanguage as HashLib
    from ...CommonLibrary.Int_TheLanguage import *
    from ...CommonLibrary.List_TheLanguage import List
    # from ...CommonLibrary.Num_TheLanguage import Num
    # from ...CommonLibrary.Queue_TheLanguage import Queue
    from ...CommonLibrary.Range_TheLanguage import *
    from ...CommonLibrary.Set_TheLanguage import Set
    from ...CommonLibrary.Stack_TheLanguage import Stack
    from ...CommonLibrary.String_TheLanguage import String

    from .Normalize_TheLanguage import LineInfo
    from .NormalizedIterator_TheLanguage import NormalizedIterator
    from .Token_TheLanguage import Token

# Visibility: public
# ClassModifier: immutable
# ClassType: Enum
class DynamicPhrasesType(Enum):
    """\
    BugBug
    """

    Attributes = auto()
    Expressions = auto()
    Names = auto()
    Statements = auto()
    Types = auto()
    TemplateDecoratorExpressions = auto()
    TemplateDecoratorTypes = auto()
# Visibility: public
# ClassModifier: immutable
# ClassType: Enum
class Continuation(Enum):
    """\
    BugBug
    """

    Continue = auto()
    Terminate = auto()
# Visibility: public
# ClassModifier: mutable
# ClassType: Class
class Phrase(object):
    """\
    BugBug
    """

    def __init__(self, *args, **kwargs):
        Phrase._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # _name_

        # No bases

        # _name_
        if "_name_" in kwargs:
            self._name_ = kwargs.pop("_name_")
        elif args:
            self._name_ = args.pop(0)
        else:
            raise Exception("_name_ was not provided")

        # _parent
        self._parent = None

        # _is_populated
        self._is_populated = False

        self._Init_a10c8c63384e4b81895db600499f6d5d_()

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

        result = cls.__CompareItem__(a._name_, b._name_)
        if result is not None: return result

        result = cls.__CompareItem__(a._parent, b._parent)
        if result is not None: return result

        result = cls.__CompareItem__(a._is_populated, b._is_populated)
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

    def _Init_a10c8c63384e4b81895db600499f6d5d_(self):
        pass

    NormalizedIterator = NormalizedIterator
    EnqueueAsyncItemType = None
    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class NormalizedIteratorRange(object):
        def __init__(self, *args, **kwargs):
            Phrase.NormalizedIteratorRange._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # begin, end

            # No bases

            # begin
            if "begin" in kwargs:
                self.begin = kwargs.pop("begin")
            elif args:
                self.begin = args.pop(0)
            else:
                raise Exception("begin was not provided")

            # end
            if "end" in kwargs:
                self.end = kwargs.pop("end")
            elif args:
                self.end = args.pop(0)
            else:
                raise Exception("end was not provided")

            self._Init_a088c1e73ba6461180ce0fe3343ccdba_()

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

            result = cls.__CompareItem__(a.begin, b.begin)
            if result is not None: return result

            result = cls.__CompareItem__(a.end, b.end)
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

        # Return Type: None
        def _Init_a088c1e73ba6461180ce0fe3343ccdba_(self):
            assert self.begin <= self.end

    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Struct
    class LexResult(object):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.LexResult._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # success, range, data

            # No bases

            # success
            if "success" in kwargs:
                self.success = kwargs.pop("success")
            elif args:
                self.success = args.pop(0)
            else:
                raise Exception("success was not provided")

            # range
            if "range" in kwargs:
                self.range = kwargs.pop("range")
            elif args:
                self.range = args.pop(0)
            else:
                raise Exception("range was not provided")

            # data
            if "data" in kwargs:
                self.data = kwargs.pop("data")
            elif args:
                self.data = args.pop(0)
            else:
                raise Exception("data was not provided")

            self._Init_d71d2b1f57974cfaa2cc80de838c20e7_()

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

            result = cls.__CompareItem__(a.success, b.success)
            if result is not None: return result

            result = cls.__CompareItem__(a.range, b.range)
            if result is not None: return result

            result = cls.__CompareItem__(a.data, b.data)
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

        @property
        def Success(self): return self.success
        @property
        def IterBegin(self): return self.range.begin
        @property
        def IterEnd(self): return self.range.end
        @property
        def Data(self): return self.data
        # Return Type: None
        def _Init_d71d2b1f57974cfaa2cc80de838c20e7_(self):
            assert self.data is not None or self.success is False

    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class _LexResultData(object):
        def __init__(self, *args, **kwargs):
            Phrase._LexResultData._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # 

            # No bases

            # No members

            self._Init_86b71ca6774543cf8c63437685b99804_()

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

        def _Init_86b71ca6774543cf8c63437685b99804_(self):
            pass

        pass
    LexResultData = _LexResultData
    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class WhitespaceLexResultData(_LexResultData):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.WhitespaceLexResultData._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # whitespace

            Phrase._LexResultData._InternalInit(self, args, kwargs)

            # whitespace
            if "whitespace" in kwargs:
                self.whitespace = kwargs.pop("whitespace")
            elif args:
                self.whitespace = args.pop(0)
            else:
                raise Exception("whitespace was not provided")

            self._Init_3df39378c97d49048e2e041805d257f2_()

        def __eq__(self, other):
            if Phrase._LexResultData.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) == 0

        def __ne__(self, other):
            if Phrase._LexResultData.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other) != 0

        def __lt__(self, other):
            if Phrase._LexResultData.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) < 0

        def __le__(self, other):
            if Phrase._LexResultData.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) <= 0

        def __gt__(self, other):
            if Phrase._LexResultData.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) > 0

        def __ge__(self, other):
            if Phrase._LexResultData.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) >= 0

        @classmethod
        def __Compare__(cls, a, b):
            result = Phrase._LexResultData.__Compare__(a, b)
            if result != 0: return result

            result = cls.__CompareItem__(a.whitespace, b.whitespace)
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

        def _Init_3df39378c97d49048e2e041805d257f2_(self):
            pass

        LineInfo_WhitespaceRange = LineInfo.WhitespaceRange
    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class TokenLexResultData(_LexResultData):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.TokenLexResultData._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # token, whitespace, value, range, is_ignored

            Phrase._LexResultData._InternalInit(self, args, kwargs)

            # token
            if "token" in kwargs:
                self.token = kwargs.pop("token")
            elif args:
                self.token = args.pop(0)
            else:
                raise Exception("token was not provided")

            # whitespace
            if "whitespace" in kwargs:
                self.whitespace = kwargs.pop("whitespace")
            elif args:
                self.whitespace = args.pop(0)
            else:
                raise Exception("whitespace was not provided")

            # value
            if "value" in kwargs:
                self.value = kwargs.pop("value")
            elif args:
                self.value = args.pop(0)
            else:
                raise Exception("value was not provided")

            # range
            if "range" in kwargs:
                self.range = kwargs.pop("range")
            elif args:
                self.range = args.pop(0)
            else:
                raise Exception("range was not provided")

            # is_ignored
            if "is_ignored" in kwargs:
                self.is_ignored = kwargs.pop("is_ignored")
            elif args:
                self.is_ignored = args.pop(0)
            else:
                raise Exception("is_ignored was not provided")

            self._Init_7873f037c5564ed2b7bed255e6343257_()

        def __eq__(self, other):
            if Phrase._LexResultData.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) == 0

        def __ne__(self, other):
            if Phrase._LexResultData.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other) != 0

        def __lt__(self, other):
            if Phrase._LexResultData.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) < 0

        def __le__(self, other):
            if Phrase._LexResultData.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) <= 0

        def __gt__(self, other):
            if Phrase._LexResultData.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) > 0

        def __ge__(self, other):
            if Phrase._LexResultData.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) >= 0

        @classmethod
        def __Compare__(cls, a, b):
            result = Phrase._LexResultData.__Compare__(a, b)
            if result != 0: return result

            result = cls.__CompareItem__(a.token, b.token)
            if result is not None: return result

            result = cls.__CompareItem__(a.whitespace, b.whitespace)
            if result is not None: return result

            result = cls.__CompareItem__(a.value, b.value)
            if result is not None: return result

            result = cls.__CompareItem__(a.range, b.range)
            if result is not None: return result

            result = cls.__CompareItem__(a.is_ignored, b.is_ignored)
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

        def _Init_7873f037c5564ed2b7bed255e6343257_(self):
            pass

        Token_MatchResult = Token.MatchResult
        LineInfo_WhitespaceRange = LineInfo.WhitespaceRange
        @property
        def Token(self): return self.token
        @property
        def Whitespace(self): return self.whitespace
        @property
        def Value(self): return self.value
        @property
        def IterBegin(self): return self.range.begin
        @property
        def IterEnd(self): return self.range.end
        @property
        def IsIgnored(self): return self.is_ignored
    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class PhraseLexResultData(_LexResultData):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.PhraseLexResultData._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # phrase, data, unique_id, potential_error_context=None

            Phrase._LexResultData._InternalInit(self, args, kwargs)

            # phrase
            if "phrase" in kwargs:
                self.phrase = kwargs.pop("phrase")
            elif args:
                self.phrase = args.pop(0)
            else:
                raise Exception("phrase was not provided")

            # data
            if "data" in kwargs:
                self.data = kwargs.pop("data")
            elif args:
                self.data = args.pop(0)
            else:
                raise Exception("data was not provided")

            # unique_id
            if "unique_id" in kwargs:
                self.unique_id = kwargs.pop("unique_id")
            elif args:
                self.unique_id = args.pop(0)
            else:
                raise Exception("unique_id was not provided")

            # potential_error_context
            if "potential_error_context" in kwargs:
                self.potential_error_context = kwargs.pop("potential_error_context")
            elif args:
                self.potential_error_context = args.pop(0)
            else:
                self.potential_error_context = None

            self._Init_99da70f797ea42bba4c25215f8736a78_()

        def __eq__(self, other):
            if Phrase._LexResultData.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) == 0

        def __ne__(self, other):
            if Phrase._LexResultData.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other) != 0

        def __lt__(self, other):
            if Phrase._LexResultData.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) < 0

        def __le__(self, other):
            if Phrase._LexResultData.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) <= 0

        def __gt__(self, other):
            if Phrase._LexResultData.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) > 0

        def __ge__(self, other):
            if Phrase._LexResultData.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) >= 0

        @classmethod
        def __Compare__(cls, a, b):
            result = Phrase._LexResultData.__Compare__(a, b)
            if result != 0: return result

            result = cls.__CompareItem__(a.phrase, b.phrase)
            if result is not None: return result

            result = cls.__CompareItem__(a.data, b.data)
            if result is not None: return result

            result = cls.__CompareItem__(a.unique_id, b.unique_id)
            if result is not None: return result

            result = cls.__CompareItem__(a.potential_error_context, b.potential_error_context)
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

        def _Init_99da70f797ea42bba4c25215f8736a78_(self):
            pass

        @property
        def Phrase(self): return self.phrase
        @property
        def Data(self): return self.data
        @property
        def UniqueId(self): return self.unique_id
        @property
        def PotentialErrorContext(self): return self.potential_error_context
    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class PhraseContainerLexResultData(_LexResultData):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.PhraseContainerLexResultData._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # data_items, is_complete

            Phrase._LexResultData._InternalInit(self, args, kwargs)

            # data_items
            if "data_items" in kwargs:
                self.data_items = kwargs.pop("data_items")
            elif args:
                self.data_items = args.pop(0)
            else:
                raise Exception("data_items was not provided")

            # is_complete
            if "is_complete" in kwargs:
                self.is_complete = kwargs.pop("is_complete")
            elif args:
                self.is_complete = args.pop(0)
            else:
                raise Exception("is_complete was not provided")

            self._Init_23f6eecc2efa4ecbbe136e5b15c1b3ff_()

        def __eq__(self, other):
            if Phrase._LexResultData.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) == 0

        def __ne__(self, other):
            if Phrase._LexResultData.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other) != 0

        def __lt__(self, other):
            if Phrase._LexResultData.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) < 0

        def __le__(self, other):
            if Phrase._LexResultData.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) <= 0

        def __gt__(self, other):
            if Phrase._LexResultData.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) > 0

        def __ge__(self, other):
            if Phrase._LexResultData.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) >= 0

        @classmethod
        def __Compare__(cls, a, b):
            result = Phrase._LexResultData.__Compare__(a, b)
            if result != 0: return result

            result = cls.__CompareItem__(a.data_items, b.data_items)
            if result is not None: return result

            result = cls.__CompareItem__(a.is_complete, b.is_complete)
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

        def _Init_23f6eecc2efa4ecbbe136e5b15c1b3ff_(self):
            pass

        @property
        def DataItems(self): return self.data_items
        @property
        def IsComplete(self): return self.is_complete
    StandardLexResultData = PhraseLexResultData
    MultipleLexResultData = PhraseContainerLexResultData
    # Visibility: public
    # ClassModifier: mutable
    # ClassType: Class
    class Observer(object):
        """\
        BugBug
        """

        def __init__(self, *args, **kwargs):
            Phrase.Observer._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # 

            # No bases

            # No members

            self._Init_f42047d747ca48edbba1d0c7c6fa6db0_()

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

        def _Init_f42047d747ca48edbba1d0c7c6fa6db0_(self):
            pass

        # Visibility: public
        # ClassModifier: immutable
        # ClassType: Struct
        class GetDynamicPhrasesResult(object):
            def __init__(self, *args, **kwargs):
                Phrase.Observer.GetDynamicPhrasesResult._InternalInit(self, list(args), kwargs)

            def _InternalInit(self, args, kwargs):
                # phrases, name=None

                # No bases

                # phrases
                if "phrases" in kwargs:
                    self.phrases = kwargs.pop("phrases")
                elif args:
                    self.phrases = args.pop(0)
                else:
                    raise Exception("phrases was not provided")

                # name
                if "name" in kwargs:
                    self.name = kwargs.pop("name")
                elif args:
                    self.name = args.pop(0)
                else:
                    self.name = None

                self._Init_2e3b9daabb784073b771834ff5f7aef5_()

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

                result = cls.__CompareItem__(a.phrases, b.phrases)
                if result is not None: return result

                result = cls.__CompareItem__(a.name, b.name)
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

            def _Init_2e3b9daabb784073b771834ff5f7aef5_(self):
                pass

        # Return Type: GetDynamicPhrasesResult
        def GetDynamicPhrases(self, unique_id, type, ):
            raise Exception("Abstract/Deferred method")

        # Return Type: None
        def StartPhrase(self, unique_id, phrase, ):
            raise Exception("Abstract/Deferred method")

        # Return Type: None
        def EndPhrase(self, unique_id, phrase, was_successful, ):
            raise Exception("Abstract/Deferred method")

        # Return Type: None
        def OnPushScope(self, data, range, ):
            raise Exception("Abstract/Deferred method")

        # Return Type: None
        def OnPopScope(self, data, range, ):
            raise Exception("Abstract/Deferred method")

        # Return Type: Continuation val
        def OnInternalPhrase(self, data, range, ):
            raise Exception("Abstract/Deferred method")

        def OnPushScopeProxy(self, data, range): return self.OnPushScope(data, range.begin, range.end)
        def OnPopScopeProxy(self, data, range): return self.OnPopScope(data, range.begin, range.end)
        def OnInternalPhraseProxy(self, data, range): return self.OnInternalPhrase(data, range.begin, range.end)
    @property
    def Name(self): return self._name_
    @Name.setter
    def Name(self, value): self._name_ = value
    @property
    def Parent(self): return self.ParentProper()
    @property
    def IsPopulated(self): return self.IsPopulatedProper()
    def __hash__(self): return self._name_.__hash__()
    # Return Type: Bool val
    def IsPopulatedProper(self):
        return self._is_populated

    # Return Type: <Phrase | None> val
    def ParentProper(self):
        return self._parent

    # Return Type: Bool val
    def PopulateRecursive(self, parent, new_phrase, ):
        """\
        BugBug
        """

        if self._parent is None:
            self._parent = parent
        else:
            assert self._parent == parent, ("A `Phrase` should not be the child of multiple parents; consider constructing the `Phrase` via `PhraseItem` in `../Phrases/DSL.TheLanguage`", self._parent.name, parent.Name if parent is not None else None, self.name, )

        if self._is_populated:
            return False

        self._is_populated = True
        return self._PopulateRecursiveImpl(new_phrase, )

    # Return Type: <LexResult | None> val
    def Lex(self, unique_id, iter, observer, ignore_whitespace=False, ):
        raise Exception("Abstract/Deferred method")

    # Return Type: Bool val
    def _PopulateRecursiveImpl(self, new_phrase, ):
        raise Exception("Abstract/Deferred method")

