# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------


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

    from .OrPhrase_TheLanguage import OrPhrase
    from .RecursivePlaceholderPhrase_TheLanguage import RecursivePlaceholderPhrase
    from .SequencePhrase_TheLanguage import SequencePhrase
    from .TokenPhrase_TheLanguage import TokenPhrase
    from ..Components_TheLanguage.Phrase_TheLanguage import DynamicPhrasesType, Phrase, UniqueId

import uuid
# Visibility: public
# ClassModifier: mutable
# ClassType: Class
class DynamicPhrase(Phrase):
    """\
    Collects dynamic phrases and invokes them, ensuring that left- and right-recursive phrases work
    as intended.

    Prevents infinte recursion for those phrases that are left-recursive (meaning they belong to
    a category and consume that same category as the first phrase within the sequence).

    Examples of left-recursive phrases:
        AddExpression := <expression> '+' <expression>
        CastExpression := <expression> 'as' <type>
        IndexExpression := <expression> '[' <expression> ']'

    Examples of right-recursive phrases:
        AddExpression := <expression> '+' <expression>
        NegativeExpression := '-' <expression>
    """

    def __init__(self, *args, **kwargs):
        args = list(args)
        DynamicPhrase._InternalInit(self, args, kwargs)
        assert not args, args
        assert not kwargs, kwargs

    def _InternalInit(self, args, kwargs):
        # phrases_type, is_valid_data_func, _get_dynamic_phrases_func

        Phrase._InternalInit(self, args, kwargs)

        # phrases_type
        if "phrases_type" in kwargs:
            self.phrases_type = kwargs.pop("phrases_type")
        elif args:
            self.phrases_type = args.pop(0)
        else:
            raise Exception("phrases_type was not provided")

        # is_valid_data_func
        if "is_valid_data_func" in kwargs:
            self.is_valid_data_func = kwargs.pop("is_valid_data_func")
        elif args:
            self.is_valid_data_func = args.pop(0)
        else:
            raise Exception("is_valid_data_func was not provided")

        # _get_dynamic_phrases_func
        if "_get_dynamic_phrases_func" in kwargs:
            self._get_dynamic_phrases_func = kwargs.pop("_get_dynamic_phrases_func")
        elif args:
            self._get_dynamic_phrases_func = args.pop(0)
        else:
            raise Exception("_get_dynamic_phrases_func was not provided")

        # _lexer
        self._lexer = None

        self._Init_ed4a6bd523914440a5a145a161c85a8f_()

    def __eq__(self, other):
        compare_cache = {}

        if Phrase.__eq__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) == 0

    def __ne__(self, other):
        compare_cache = {}

        if Phrase.__ne__(self, other) is False: return False
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other, compare_cache) != 0

    def __lt__(self, other):
        compare_cache = {}

        if Phrase.__lt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) < 0

    def __le__(self, other):
        compare_cache = {}

        if Phrase.__le__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) <= 0

    def __gt__(self, other):
        compare_cache = {}

        if Phrase.__gt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) > 0

    def __ge__(self, other):
        compare_cache = {}

        if Phrase.__ge__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other, compare_cache) >= 0

    @classmethod
    def __Compare__(cls, a, b, compare_cache):
        result = Phrase.__Compare__(a, b, compare_cache)
        if result != 0: return result

        result = cls.__CompareItem__(a.phrases_type, b.phrases_type, compare_cache)
        if result is not None: return result

        return 0

    @classmethod
    def __CompareItem__(cls, a, b, compare_cache):
        cache_key = (id(a), id(b), )

        cache_value = compare_cache.get(cache_key, None)
        if cache_value is not None:
            return cache_value

        def Impl():
            nonlocal a
            nonlocal b

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

        result = Impl()

        compare_cache[cache_key] = result
        return result

    def _Init_ed4a6bd523914440a5a145a161c85a8f_(self):
        pass

    # Type alias: public Phrases = List<Phrase, >{min_length'=1, }
    # Type alias: public GetDynamicPhrasesFunc = Tuple(String, Phrases)UniqueId immutableDynamicPhrasesType immutableOberver ref
    # Type alias: public IsValidDataFunc = Bool valPhraseLexResultData immutable
    @property
    def DisplayName(self): return None if self._lexer is None else self._lexer.display_name
    def __hash__(self): return super(DynamicPhrase, self).__hash__()
    # Return Type: DynamicPhrase
    @staticmethod
    def Create(phrases_type, get_dynamic_phrases_func, include_phrases=None, exclude_phrases=None, is_valid_data_func=None, name=None, ):
        # Return Type: Bool val
        def _DefaultIsValidDataFunc(data, ):
            return True

        is_valid_data_func = is_valid_data_func or _DefaultIsValidDataFunc
        name = name or "Dynamic Phrase"
        return DynamicPhrase(name, phrases_type, is_valid_data_func, get_dynamic_phrases_func, )

    # Return Type: <LexResult | None> val
    def Lex(self, unique_id, iter, observer, ignore_whitespace=False, ):
        result = None # as <LexResult | None>
        observer.StartPhrase(unique_id, self, )
        dynamic_info = self._get_dynamic_phrases_func(unique_id, self.phrases_type, observer, )
        dynamic_phrases_name = dynamic_info[1]
        dynamic_phrases = dynamic_info[0]
        dynamic_unique_id = 0
        if True:
            left_recursive_phrases = List()
            standard_phrases = List()
            for phrase in dynamic_phrases:
                if DynamicPhrase.IsLeftRecursivePhrase(phrase, self.phrases_type, ):
                    left_recursive_phrases.InsertBack_(phrase, )
                else:
                    standard_phrases.InsertBack_(phrase, )

            _LeftRecursiveLexer = DynamicPhrase._LeftRecursiveLexer
            _StandardLexer = DynamicPhrase._StandardLexer
            if left_recursive_phrases:
                self._lexer = _LeftRecursiveLexer(dynamic_unique_id, dynamic_phrases_name, standard_phrases, left_recursive_phrases, )
            else:
                self._lexer = _StandardLexer(dynamic_unique_id, dynamic_phrases_name, standard_phrases, )


        assert self._lexer is not None
        result = self._lexer.Execute(self, unique_id, iter, observer, ignore_whitespace=ignore_whitespace, )
        if result is None:
            return None

        if (result.success and not observer.OnInternalPhraseProxy(result.data, result.range, )):
            return None

        return result

    # Return Type: Bool val
    @staticmethod
    def IsLeftRecursivePhrase(phrase, phrases_type=None, ):
        phrases_length = len(phrase.Phrases)
        return (phrase.__class__.__name__ == "SequencePhrase" and phrases_length > 1 and phrase.Phrases[0].__class__.__name__ == "DynamicPhrase" and (phrases_type is None or phrase.Phrases[0].phrases_type == phrases_type))

    # Return Type: Bool val
    @staticmethod
    def IsRightRecursivePhrase(phrase, phrases_type=None, ):
        phrases_length = len(phrase.Phrases)
        return (phrase.__class__.__name__ == "SequencePhrase" and phrases_length > 2 and phrase.Phrases[-1].__class__.__name__ == "DynamicPhrase" and (phrases_type is None or phrase.Phrases[-1].phrases_type == phrases_type))

    # Return Type: PhraseLexResultData val
    @staticmethod
    def SkipDynamicData(data, ):
        """\
        Skips the `LexResultData` that is associated with the implementation details of
        `DynamicPhrase` results.
        """

        assert data.phrase.__class__.__name__ == "DynamicPhrase"
        assert data.data.__class__.__name__ == "PhraseLexResultData"
        data = data.data
        assert data.phrase.__class__.__name__ == "OrPhrase"
        assert data.data.__class__.__name__ == "PhraseLexResultData"
        data = data.data
        return data

    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class _Lexer(object):
        def __init__(self, *args, **kwargs):
            args = list(args)
            DynamicPhrase._Lexer._InternalInit(self, args, kwargs)
            assert not args, args
            assert not kwargs, kwargs

        def _InternalInit(self, args, kwargs):
            # unique_id, display_name, phrases

            # No bases

            # unique_id
            if "unique_id" in kwargs:
                self.unique_id = kwargs.pop("unique_id")
            elif args:
                self.unique_id = args.pop(0)
            else:
                raise Exception("unique_id was not provided")

            # display_name
            if "display_name" in kwargs:
                self.display_name = kwargs.pop("display_name")
            elif args:
                self.display_name = args.pop(0)
            else:
                raise Exception("display_name was not provided")

            # phrases
            if "phrases" in kwargs:
                self.phrases = kwargs.pop("phrases")
            elif args:
                self.phrases = args.pop(0)
            else:
                raise Exception("phrases was not provided")

            self._Init_c49609d4524f43ce833c7d62faad7613_()

        def __eq__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) == 0

        def __ne__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other, compare_cache) != 0

        def __lt__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) < 0

        def __le__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) <= 0

        def __gt__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) > 0

        def __ge__(self, other):
            compare_cache = {}

            # No bases
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) >= 0

        @classmethod
        def __Compare__(cls, a, b, compare_cache):
            # No bases

            result = cls.__CompareItem__(a.unique_id, b.unique_id, compare_cache)
            if result is not None: return result

            result = cls.__CompareItem__(a.display_name, b.display_name, compare_cache)
            if result is not None: return result

            result = cls.__CompareItem__(a.phrases, b.phrases, compare_cache)
            if result is not None: return result

            return 0

        @classmethod
        def __CompareItem__(cls, a, b, compare_cache):
            cache_key = (id(a), id(b), )

            cache_value = compare_cache.get(cache_key, None)
            if cache_value is not None:
                return cache_value

            def Impl():
                nonlocal a
                nonlocal b

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

            result = Impl()

            compare_cache[cache_key] = result
            return result

        def _Init_c49609d4524f43ce833c7d62faad7613_(self):
            pass

        # Return Type: <LexResult | None> val
        def Execute(self, phrase, unique_id, iter, observer, ignore_whitespace, ):
            raise Exception("Abstract/Deferred method")

    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class _StandardLexer(_Lexer):
        def __init__(self, *args, **kwargs):
            args = list(args)
            DynamicPhrase._StandardLexer._InternalInit(self, args, kwargs)
            assert not args, args
            assert not kwargs, kwargs

        def _InternalInit(self, args, kwargs):
            # 

            DynamicPhrase._Lexer._InternalInit(self, args, kwargs)

            # _or_phrase
            self._or_phrase = None

            self._Init_cdfe49968d604c1fa82cbfea8c7d97b7_()

        def __eq__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) == 0

        def __ne__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other, compare_cache) != 0

        def __lt__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) < 0

        def __le__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) <= 0

        def __gt__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) > 0

        def __ge__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) >= 0

        @classmethod
        def __Compare__(cls, a, b, compare_cache):
            result = DynamicPhrase._Lexer.__Compare__(a, b, compare_cache)
            if result != 0: return result



            return 0

        @classmethod
        def __CompareItem__(cls, a, b, compare_cache):
            cache_key = (id(a), id(b), )

            cache_value = compare_cache.get(cache_key, None)
            if cache_value is not None:
                return cache_value

            def Impl():
                nonlocal a
                nonlocal b

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

            result = Impl()

            compare_cache[cache_key] = result
            return result

        # Return Type: <LexResult | None> val
        def Execute(self, phrase, unique_id, iter, observer, ignore_whitespace, ):
            LexResult = Phrase.LexResult
            NormalizedIteratorRange = Phrase.NormalizedIteratorRange
            PhraseLexResultData = Phrase.PhraseLexResultData
            if not self.phrases:
                return LexResult(False, NormalizedIteratorRange(iter.Clone(), iter.Clone(), ), None, )

            result = self._or_phrase.Lex(unique_id + (self._or_phrase.Name, ), iter, observer, ignore_whitespace=ignore_whitespace, )
            if result is None:
                return None

            return LexResult(result.success, result.range, PhraseLexResultData(phrase, result.data, unique_id, ), )

        # Return Type: None
        def _Init_cdfe49968d604c1fa82cbfea8c7d97b7_(self):
            self._or_phrase = OrPhrase.Create(self.phrases, name=self.display_name, ) # as val

    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class _LeftRecursiveLexer(_Lexer):
        def __init__(self, *args, **kwargs):
            args = list(args)
            DynamicPhrase._LeftRecursiveLexer._InternalInit(self, args, kwargs)
            assert not args, args
            assert not kwargs, kwargs

        def _InternalInit(self, args, kwargs):
            # left_recursive_phrases

            DynamicPhrase._Lexer._InternalInit(self, args, kwargs)

            # left_recursive_phrases
            if "left_recursive_phrases" in kwargs:
                self.left_recursive_phrases = kwargs.pop("left_recursive_phrases")
            elif args:
                self.left_recursive_phrases = args.pop(0)
            else:
                raise Exception("left_recursive_phrases was not provided")

            # _prefix_phrase
            self._prefix_phrase = None

            # _suffix_phrase
            self._suffix_phrase = None

            # _pseudo_phrase
            self._pseudo_phrase = None

            self._Init_567d9ea5e142412d9908dcfda9529c4d_()

        def __eq__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) == 0

        def __ne__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other, compare_cache) != 0

        def __lt__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) < 0

        def __le__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) <= 0

        def __gt__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) > 0

        def __ge__(self, other):
            compare_cache = {}

            if DynamicPhrase._Lexer.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other, compare_cache) >= 0

        @classmethod
        def __Compare__(cls, a, b, compare_cache):
            result = DynamicPhrase._Lexer.__Compare__(a, b, compare_cache)
            if result != 0: return result

            result = cls.__CompareItem__(a.left_recursive_phrases, b.left_recursive_phrases, compare_cache)
            if result is not None: return result

            return 0

        @classmethod
        def __CompareItem__(cls, a, b, compare_cache):
            cache_key = (id(a), id(b), )

            cache_value = compare_cache.get(cache_key, None)
            if cache_value is not None:
                return cache_value

            def Impl():
                nonlocal a
                nonlocal b

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

            result = Impl()

            compare_cache[cache_key] = result
            return result

        # Return Type: LexResult val
        def Execute(self, phrase, unique_id, iter, observer, ignore_whitespace, ):
            LexResult = Phrase.LexResult
            NormalizedIteratorRange = Phrase.NormalizedIteratorRange
            PhraseLexResultData = Phrase.PhraseLexResultData
            TokenLexResultData = Phrase.TokenLexResultData
            # Return Type: Tuple(Phrase, UniqueId)
            def _PhraseIterator():
                yield (self._prefix_phrase, unique_id + ("__Prefix__", ), )
                iteration = 0
                while True:
                    iteration_str = str(iteration)
                    yield (self._suffix_phrase, unique_id + ("__Suffix__", iteration_str, ), )
                    iteration += 1

            original_iter = iter.Clone()
            data_items = List()
            phrase_iterator = _PhraseIterator()
            while True:
                this_phrase, this_unique_id = next(phrase_iterator)
                this_result = this_phrase.Lex(this_unique_id, iter, observer, ignore_whitespace=ignore_whitespace, )
                if this_result is None:
                    return None

                if not data_items or this_result.success:
                    iter = this_result.range.end.Clone()

                assert this_result.data is not None
                data_items.InsertBack_(this_result.data, )
                if not this_result.success:
                    break

            assert data_items
            error_data_item = data_items.RemoveBack_()
            range = NormalizedIteratorRange(original_iter, iter, )
            if not data_items:
                return LexResult(False, range, PhraseLexResultData(self, error_data_item, unique_id, ), )

            for (data_item_index, data_item, ) in Enumerate(data_items, ):
                assert data_item.phrase.__class__.__name__ == "OrPhrase"
                assert data_item.data is not None
                data_items[data_item_index] = data_item.data
            for (data_item_index, data_item, ) in Enumerate(data_items, ):
                if data_item_index != 0:
                    if True:
                        assert data_item.phrase.__class__.__name__ == "SequencePhrase"
                        assert data_item.data.__class__.__name__ == "PhraseContainerLexResultData"
                        non_ignored_data_items = Sum(1 if not di.__class__.__name__ == "TokenLexResultData" or not di.is_ignored else 0 for di in data_item.data.data_items, )
                        non_control_token_phrases = Sum(1 if not phrase.__class__.__name__ == "TokenPhrase" or not phrase.token.is_control_token else 0 for phrase in data_item.phrase.Phrases, )
                        assert non_ignored_data_items == non_control_token_phrases - 1

                    data_item.data.data_items.insert(0, data_items[data_item_index - 1])

                data_items[data_item_index] = PhraseLexResultData(phrase, PhraseLexResultData(self._pseudo_phrase, data_item, unique_id, ), unique_id, )
            data = data_items[-1]
            value_data = DynamicPhrase.SkipDynamicData(data, )
            if (DynamicPhrase.IsLeftRecursivePhrase(value_data.phrase, phrase.phrases_type, ) and DynamicPhrase.IsRightRecursivePhrase(value_data.phrase, phrase.phrases_type, )):
                assert value_data.data.__class__.__name__ == "PhraseContainerLexResultData"
                assert value_data.data.data_items[-1].__class__.__name__ == "PhraseLexResultData"
                value_data = DynamicPhrase.SkipDynamicData(value_data.data.data_items[-1], )
                if DynamicPhrase.IsRightRecursivePhrase(value_data.phrase, phrase.phrases_type, ):
                    root_dynamic = data
                    root_actual = DynamicPhrase.SkipDynamicData(root_dynamic, )
                    assert root_actual.phrase.__class__.__name__ == "SequencePhrase"
                    assert root_actual.data.__class__.__name__ == "PhraseContainerLexResultData"
                    new_root_dynamic = root_actual.data.data_items[-1]
                    new_root_actual = DynamicPhrase.SkipDynamicData(new_root_dynamic, )
                    assert new_root_actual.phrase.__class__.__name__ == "SequencePhrase"
                    assert new_root_actual.data.__class__.__name__ == "PhraseContainerLexResultData"
                    travel = new_root_actual
                    while True:
                        potential_travel_dynamic = travel.data.data_items[0]
                        potential_travel_actual = DynamicPhrase.SkipDynamicData(potential_travel_dynamic, )
                        if not DynamicPhrase.IsRightRecursivePhrase(potential_travel_actual.phrase, phrase.phrases_type, ):
                            break

                        travel = potential_travel_actual
                    root_actual.data.data_items[-1] = travel.data.data_items[0]
                    travel.data.data_items[0] = data
                    data = new_root_dynamic


            assert data.__class__.__name__ == "PhraseLexResultData"
            if not phrase.is_valid_data_func(data, ):
                return LexResult(False, range, data, )

            unique_id_suffix_str = "Pseudo ({})".format(uuid.uuid4())
            unique_id_suffix_iteration = 0
            # Return Type: None
            def _UpdateUniqueIds(data, ):
                nonlocal unique_id_suffix_iteration

                if data is None:
                    return

                if data.__class__.__name__ == "PhraseLexResultData":
                    data.unique_id = (unique_id_suffix_str, str(unique_id_suffix_iteration))
                    unique_id_suffix_iteration += 1
                    _UpdateUniqueIds(data.data, )
                elif data.__class__.__name__ == "PhraseContainerLexResultData":
                    for data_item in data.data_items:
                        _UpdateUniqueIds(data_item, )
                elif data.__class__.__name__ == "TokenLexResultData":
                    pass
                else:
                    assert False, data


            _UpdateUniqueIds(data, )
            data = PhraseLexResultData(data.phrase, data.data, data.unique_id, error_data_item, )
            return LexResult(True, range, data, )

        Phrase = Phrase
        # Visibility: private
        # ClassModifier: immutable
        # ClassType: Class
        class _SequenceSuffixWrapper(Phrase):
            def __init__(self, *args, **kwargs):
                args = list(args)
                DynamicPhrase._LeftRecursiveLexer._SequenceSuffixWrapper._InternalInit(self, args, kwargs)
                assert not args, args
                assert not kwargs, kwargs

            def _InternalInit(self, args, kwargs):
                # _phrase

                Phrase._InternalInit(self, args, kwargs)

                # _phrase
                if "_phrase" in kwargs:
                    self._phrase = kwargs.pop("_phrase")
                elif args:
                    self._phrase = args.pop(0)
                else:
                    raise Exception("_phrase was not provided")

                self._Init_7216306d679c4d58b83ee7ef47836cd5_()

            def __eq__(self, other):
                compare_cache = {}

                if Phrase.__eq__(self, other) is False: return False
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other, compare_cache) == 0

            def __ne__(self, other):
                compare_cache = {}

                if Phrase.__ne__(self, other) is False: return False
                if not isinstance(other, self.__class__): return True
                return self.__class__.__Compare__(self, other, compare_cache) != 0

            def __lt__(self, other):
                compare_cache = {}

                if Phrase.__lt__(self, other) is False: return False
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other, compare_cache) < 0

            def __le__(self, other):
                compare_cache = {}

                if Phrase.__le__(self, other) is False: return False
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other, compare_cache) <= 0

            def __gt__(self, other):
                compare_cache = {}

                if Phrase.__gt__(self, other) is False: return False
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other, compare_cache) > 0

            def __ge__(self, other):
                compare_cache = {}

                if Phrase.__ge__(self, other) is False: return False
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other, compare_cache) >= 0

            @classmethod
            def __Compare__(cls, a, b, compare_cache):
                result = Phrase.__Compare__(a, b, compare_cache)
                if result != 0: return result

                result = cls.__CompareItem__(a._phrase, b._phrase, compare_cache)
                if result is not None: return result

                return 0

            @classmethod
            def __CompareItem__(cls, a, b, compare_cache):
                cache_key = (id(a), id(b), )

                cache_value = compare_cache.get(cache_key, None)
                if cache_value is not None:
                    return cache_value

                def Impl():
                    nonlocal a
                    nonlocal b

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

                result = Impl()

                compare_cache[cache_key] = result
                return result

            def _Init_7216306d679c4d58b83ee7ef47836cd5_(self):
                pass

            # Return Type: _SequenceSuffixWrapper val
            @staticmethod
            def Create(phrase, ):
                _SequenceSuffixWrapper = DynamicPhrase._LeftRecursiveLexer._SequenceSuffixWrapper
                return _SequenceSuffixWrapper("_SequenceSuffixWrapper", phrase, ) # as val

            # Return Type: <LexResult | None> val
            def Lex(self, unique_id, iter, observer, ignore_whitespace=False, ):
                return self._phrase.LexSuffix(unique_id, iter, observer, ignore_whitespace=ignore_whitespace, )

        # Return Type: None
        def _Init_567d9ea5e142412d9908dcfda9529c4d_(self):
            assert self.phrases
            self._prefix_phrase = OrPhrase.Create(self.phrases, name="{} <Prefix>".format(self.display_name, ), ) # as val
            _SequenceSuffixWrapper = DynamicPhrase._LeftRecursiveLexer._SequenceSuffixWrapper
            python_workaround = [_SequenceSuffixWrapper.Create(phrase) for phrase in self.left_recursive_phrases]
            self._suffix_phrase = OrPhrase.Create(python_workaround, name="{} <Suffix>".format(self.display_name, ), ) # as val
            self._pseudo_phrase = OrPhrase.Create(self.left_recursive_phrases + self.phrases, name=self.display_name, ) # as val

    # Return Type: Bool val
    def _PopulateRecursiveImpl(self, new_phrase, ):
        return False

