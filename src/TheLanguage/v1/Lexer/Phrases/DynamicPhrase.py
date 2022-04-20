# ----------------------------------------------------------------------
# |
# |  DynamicPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 12:49:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DynamicPhrase object"""

import os
import uuid

from typing import Callable, cast, Generator, List, Optional, TextIO, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .OrPhrase import OrPhrase
    from .SequencePhrase import SequencePhrase
    from .TokenPhrase import TokenPhrase

    from ..Components.Phrase import DynamicPhrasesType, NormalizedIterator, Phrase


# ----------------------------------------------------------------------
class DynamicPhrase(Phrase):
    """\
    Collects dynamic statements and invokes them, ensure that left-recursive phrases work as intended.

    Prevents infinite recursion for those phrases that are left recursive (meaning they belong to
    a category and consume that category as the first phrase within the sequence).

    Examples:
        # The phrase is an expression and the first phrase within the sequence is also an expression
        AddExpression:= <expression> '+' <expression>
        CastExpression:= <expression> 'as' <type>
        IndexExpression:= <expression> '[' <expression> ']'
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrases_type: DynamicPhrasesType,
        get_dynamic_phrases_func: Callable[
            [
                Tuple[str, ...],            # unique_id
                DynamicPhrasesType,
                Phrase.Observer,
            ],
            Tuple[int, List[Phrase], Optional[str]],
        ],
        name: Optional[str]=None,
        include_phrases: Optional[List[Union[str, Phrase]]]=None,
        exclude_phrases: Optional[List[Union[str, Phrase]]]=None,
        is_valid_data_func: Optional[Callable[[Phrase.LexResultData], bool]]=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrase"

        super(DynamicPhrase, self).__init__(name)

        self.dynamic_phrases_type           = phrases_type
        self.is_valid_data_func             = is_valid_data_func or (lambda *args, **kwargs: True)

        self._get_dynamic_phrases_func      = get_dynamic_phrases_func
        self._display_name: Optional[str]   = None

        # ----------------------------------------------------------------------
        def CreateIncludePhraseFunc(
            include_phrases: Optional[List[Union[str, Phrase]]],
            exclude_phrases: Optional[List[Union[str, Phrase]]],
        ) -> Callable[[Phrase], bool]:
            assert (
                (not include_phrases and not exclude_phrases)
                or not exclude_phrases
                or not include_phrases
            )

            if include_phrases:
                these_include_phrases = set(
                    [
                        phrase.name if isinstance(phrase, Phrase) else phrase
                        for phrase in include_phrases
                    ],
                )

                return lambda phrase: phrase.name in these_include_phrases

            if exclude_phrases:
                these_exclude_phrases = set(
                    [
                        phrase.name if isinstance(phrase, Phrase) else phrase
                        for phrase in exclude_phrases
                    ],
                )

                return lambda phrase: phrase.name not in these_exclude_phrases

            return lambda phrase: True

        # ----------------------------------------------------------------------

        self._pre_phrase_filter_func        = CreateIncludePhraseFunc(include_phrases, exclude_phrases)

        self._executor: Union[
            None,
            DynamicPhrase._StandardExecutor,
            DynamicPhrase._LeftRecursiveExecutor,
        ] = None

    # ----------------------------------------------------------------------
    @staticmethod
    def IsLeftRecursivePhrase(
        phrase: Phrase,
        phrases_type: Optional[DynamicPhrasesType]=None,
    ) -> bool:
        return (
            isinstance(phrase, SequencePhrase)
            and len(phrase.phrases) > 1
            and isinstance(phrase.phrases[0], DynamicPhrase)
            and (
                phrases_type is None
                or phrase.phrases[0].dynamic_phrases_type == phrases_type
            )
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def IsRightRecursivePhrase(
        phrase: Phrase,
        phrases_type: Optional[DynamicPhrasesType]=None,
    ) -> bool:
        return (
            isinstance(phrase, SequencePhrase)
            and len(phrase.phrases) > 1
            and isinstance(phrase.phrases[-1], DynamicPhrase)
            and (
                phrases_type is None
                or phrase.phrases[-1].dynamic_phrases_type == phrases_type
            )
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def GetDynamicData(
        data: Phrase.LexResultData,
    ) -> Phrase.LexResultData:
        assert isinstance(data.phrase, DynamicPhrase), data.phrase
        assert isinstance(data.data, Phrase.LexResultData), data.data

        data = data.data

        assert isinstance(data, Phrase.LexResultData), data
        assert isinstance(data.phrase, OrPhrase), data.phrase
        assert isinstance(data.data, Phrase.LexResultData), data.data

        data = data.data

        assert isinstance(data, Phrase.LexResultData), data
        return data

    # ----------------------------------------------------------------------
    @property
    def DisplayName(self) -> str:
        return self._display_name or self.name

    # ----------------------------------------------------------------------
    @Interface.override
    def Lex(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        single_threaded=False,
        ignore_whitespace=False,
    ) -> Optional[Phrase.LexResult]:
        result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, result is not None and result.success)):
            # Get the dynamic phrases
            dynamic_phrases_id, dynamic_phrases, dynamic_name = self._get_dynamic_phrases_func(
                unique_id,
                self.dynamic_phrases_type,
                observer,
            )

            assert isinstance(dynamic_phrases, list)

            if self._executor is None or dynamic_phrases_id != self._executor.dynamic_phrases_id:
                # Filter the list by those that have been explicitly included on excluded
                dynamic_phrases = [
                    phrase for phrase in dynamic_phrases if self._pre_phrase_filter_func(phrase)
                ]

                # Split the phrases into those that are left-recursive and those that are not
                left_recursive_phrases: List[Phrase] = []
                standard_phrases: List[Phrase] = []

                for phrase in dynamic_phrases:
                    if self.__class__.IsLeftRecursivePhrase(phrase, self.dynamic_phrases_type):
                        left_recursive_phrases.append(phrase)
                    else:
                        standard_phrases.append(phrase)

                if left_recursive_phrases:
                    self._executor = self.__class__._LeftRecursiveExecutor(  # pylint: disable=protected-access
                        self,
                        dynamic_phrases_id,
                        dynamic_name,
                        left_recursive_phrases,
                        standard_phrases,
                    )
                elif standard_phrases:
                    self._executor = self.__class__._StandardExecutor(  # pylint: disable=protected-access
                        self,
                        dynamic_phrases_id,
                        dynamic_name,
                        standard_phrases,
                    )
                else:
                    assert False, self  # pragma: no cover

                self._display_name = dynamic_name

            result = self._executor.Execute(
                unique_id,
                normalized_iter,
                observer,
                single_threaded=single_threaded,
                ignore_whitespace=ignore_whitespace,
            )

            if result is None:
                return None

            if result.success and not observer.OnInternalPhrase(result.iter_range, result.data):
                return None

            return result

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PrettyPrint(
        indentation: str,
        data: Phrase.LexResultData.DataItemType,
        output_stream: TextIO,
    ) -> None:
        assert isinstance(data, Phrase.LexResultData), data
        data.phrase.PrettyPrint(indentation, data.data, output_stream)

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _StandardExecutor(object):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            dynamic_phrase: "DynamicPhrase",
            dynamic_phrases_id: int,
            dynamic_name: Optional[str],
            phrases: List[Phrase],
        ):
            self.dynamic_phrase             = dynamic_phrase
            self.dynamic_phrases_id         = dynamic_phrases_id

            self._or_phrase                 = OrPhrase(
                phrases,
                name=dynamic_name,
            )

        # ----------------------------------------------------------------------
        def Execute(
            self,
            unique_id: Tuple[str, ...],
            normalized_iter: NormalizedIterator,
            observer: Phrase.Observer,
            *,
            single_threaded: bool,
            ignore_whitespace: bool,
        ) -> Optional[Phrase.LexResult]:
            result = self._or_phrase.Lex(
                unique_id + (self._or_phrase.name, ),
                normalized_iter,
                observer,
                single_threaded=single_threaded,
                ignore_whitespace=ignore_whitespace,
            )

            if result is None:
                return None

            return Phrase.LexResult.Create(
                result.success,
                result.iter_range,
                Phrase.LexResultData.Create(self.dynamic_phrase, unique_id, result.data, None),
            )

    # ----------------------------------------------------------------------
    class _LeftRecursiveExecutor(object):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            dynamic_phrase: "DynamicPhrase",
            dynamic_phrases_id: int,
            dynamic_name: Optional[str],
            left_recursive_phrases: List[Phrase],
            standard_phrases: List[Phrase],
        ):
            self.dynamic_phrase             = dynamic_phrase
            self.dynamic_phrases_id         = dynamic_phrases_id

            self._prefix_phrase             = OrPhrase(
                standard_phrases,
                name="{} <Prefix>".format(dynamic_name or ""),
            )

            self._suffix_phrase             = OrPhrase(
                [
                    self.__class__._SequenceSuffixWrapper(cast(SequencePhrase, phrase))  # pylint: disable=protected-access
                    for phrase in left_recursive_phrases
                ],
                name="{} <Suffix>".format(dynamic_name or ""),
            )

            self._pseudo_or_phrase          = OrPhrase(
                left_recursive_phrases + standard_phrases,
                name=dynamic_name,
            )

        # ----------------------------------------------------------------------
        def Execute(
            self,
            unique_id: Tuple[str, ...],
            normalized_iter: NormalizedIterator,
            observer: Phrase.Observer,
            *,
            single_threaded: bool,
            ignore_whitespace: bool,
        ) -> Optional[Phrase.LexResult]:
            # If here, we need to simulate greedy left-recursive consumption without devolving into
            # infinite recursion scenarios. To simulate this, simulate recursion interspersed with
            # attempts to match non-left-recursive phrases. Try the left recursive phrases at 1 level
            # of recursion first, then try the non-left-recursive phrases.

            # ----------------------------------------------------------------------
            def PhraseIterator() -> Generator[Tuple[Phrase, Tuple[str, ...]], None, None]:
                # Prefix
                yield (
                    self._prefix_phrase,
                    unique_id + ("__Prefix__", ),
                )

                # Suffix(es)
                iterator = 0

                while True:
                    yield (
                        self._suffix_phrase,
                        unique_id + ("__Suffix__", str(iterator), ),
                    )
                    iterator += 1

            # ----------------------------------------------------------------------

            results: List[Phrase.LexResultData] = []

            starting_iter = normalized_iter.Clone()
            phrase_iter = PhraseIterator()

            while True:
                this_phrase, this_unique_id = next(phrase_iter)

                this_result = this_phrase.Lex(
                    this_unique_id,
                    normalized_iter,
                    observer,
                    single_threaded=single_threaded,
                    ignore_whitespace=ignore_whitespace,
                )

                if this_result is None:
                    return None

                if not results or this_result.success:
                    normalized_iter = this_result.iter_range.end

                results.append(this_result.data)

                if not this_result.success:
                    break

            assert results
            error_result = results.pop()

            if not results:
                return Phrase.LexResult.Create(
                    False,
                    Phrase.NormalizedIteratorRange.Create(starting_iter, normalized_iter),
                    Phrase.LexResultData.Create(self.dynamic_phrase, unique_id, error_result, None),
                )

            # Strip the prefix- and suffix-cruft from the data items so that we can simulate a
            # standard phrase.
            for result_index, result in enumerate(results):
                assert isinstance(result.phrase, OrPhrase), result.phrase
                assert isinstance(result.data, Phrase.LexResultData), result.data

                results[result_index] = Phrase.LexResultData.Create(
                    self.dynamic_phrase,
                    unique_id,
                    Phrase.LexResultData.Create(
                        self._pseudo_or_phrase,
                        # Don't worry about providing a unique id here, as they are all going to be
                        # overwritten below
                        unique_id,
                        result.data,
                        None,
                    ),
                    None,
                )

            root = results[0]

            for result in results[1:]:
                result_data = self.dynamic_phrase.__class__.GetDynamicData(result)

                assert isinstance(result_data, Phrase.LexResultData), result_data
                assert isinstance(result_data.phrase, SequencePhrase), result_data.phrase
                assert isinstance(result_data.data, list), result_data.data

                if __debug__:
                    # The number of existing (non-ignored) data items should be 1 less than the number
                    # of expected (non-control-token) data items.
                    non_ignored_data_items = sum(
                        1 if not isinstance(di, Phrase.TokenLexResultData) or not di.is_ignored else 0
                        for di in result_data.data
                    )

                    non_control_token_phrases = sum(
                        1 if not isinstance(phrase, TokenPhrase) or not phrase.token.is_control_token else 0
                        for phrase in result_data.phrase.phrases
                    )

                    assert non_ignored_data_items == non_control_token_phrases - 1

                result_data.data.insert(0, root)

                if self.dynamic_phrase.__class__.IsRightRecursivePhrase(result_data.phrase):
                    right = result_data.data[-1]
                    assert isinstance(right, Phrase.LexResultData)

                    right_data = self.dynamic_phrase.__class__.GetDynamicData(right)

                    leftmost_right: Optional[Phrase.LexResultData] = None
                    leftmost_right_data: Optional[Phrase.LexResultData] = None

                    potential_leftmost_right: Phrase.LexResultData = right
                    potential_leftmost_right_data: Phrase.LexResultData = right_data

                    while True:
                        if not isinstance(potential_leftmost_right_data.phrase, SequencePhrase):
                            break

                        if not self.dynamic_phrase.__class__.IsRightRecursivePhrase(potential_leftmost_right_data.phrase):
                            break

                        leftmost_right = potential_leftmost_right
                        leftmost_right_data = potential_leftmost_right_data

                        assert isinstance(potential_leftmost_right_data.data, list)
                        assert potential_leftmost_right_data.data

                        potential_leftmost_right = cast(Phrase.LexResultData, potential_leftmost_right_data.data[0])
                        potential_leftmost_right_data = self.dynamic_phrase.__class__.GetDynamicData(potential_leftmost_right)

                    if leftmost_right is not None:
                        result_precedence = result_data.phrase.CalcPrecedence(result_data.data)

                        assert leftmost_right_data is not None
                        assert isinstance(leftmost_right_data.phrase, SequencePhrase)
                        assert isinstance(leftmost_right_data.data, list)
                        assert leftmost_right_data.data

                        leftmost_right_precedence = leftmost_right_data.phrase.CalcPrecedence(leftmost_right_data.data)

                        if result_precedence <= leftmost_right_precedence:
                            result_data.data[-1] = leftmost_right_data.data[0]
                            leftmost_right_data.data[0] = result

                            if result_precedence == leftmost_right_precedence:
                                root = right
                            else:
                                root = leftmost_right

                            continue

                root = result

            # Should this data be considered as valid?
            assert isinstance(root, Phrase.LexResultData), root

            if not self.dynamic_phrase.is_valid_data_func(root):
                return Phrase.LexResult.Create(
                    False,
                    Phrase.NormalizedIteratorRange.Create(starting_iter, normalized_iter),
                    root,
                )

            # At this point, we have massaged and modified the structure of the tree to the point where
            # attempting to use previously cached values will not work. Update all of the unique_ids for
            # all data in the hierarchy to prevent caching.

            unique_id_str = "Pseudo ({})".format(uuid.uuid4())
            unique_id_suffix_iteration = 0

            # ----------------------------------------------------------------------
            def UpdateUniqueIds(
                data: Phrase.LexResultData.DataItemType,
            ) -> None:
                if data is None:
                    return

                nonlocal unique_id_suffix_iteration

                if isinstance(data, Phrase.LexResultData):
                    object.__setattr__(data, "unique_id", (unique_id_str, str(unique_id_suffix_iteration)))

                    unique_id_suffix_iteration += 1
                    UpdateUniqueIds(data.data)

                elif isinstance(data, Phrase.TokenLexResultData):
                    # Nothing to do here
                    pass

                elif isinstance(data, list):
                    for item in data:
                        UpdateUniqueIds(item)

                else:
                    assert False, data  # pragma: no cover

            # ----------------------------------------------------------------------

            UpdateUniqueIds(root)

            # Update the data to include error info
            if error_result is not None:
                root = Phrase.LexResultData.Create(
                    root.phrase,
                    root.unique_id,
                    root.data,
                    error_result,
                )

            return Phrase.LexResult.Create(
                True,
                Phrase.NormalizedIteratorRange.Create(starting_iter, normalized_iter),
                root,
            )

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        class _SequenceSuffixWrapper(Phrase):
            # ----------------------------------------------------------------------
            def __init__(
                self,
                phrase: SequencePhrase,
            ):
                super(DynamicPhrase._LeftRecursiveExecutor._SequenceSuffixWrapper, self).__init__("Wrapper ({})".format(phrase.name))  # pylint: disable=protected-access

                self._phrase                    = phrase

            # ----------------------------------------------------------------------
            @Interface.override
            def Lex(
                self,
                unique_id: Tuple[str, ...],
                normalized_iter: NormalizedIterator,
                observer: Phrase.Observer,
                *,
                single_threaded=False,
                ignore_whitespace=False,
            ) -> Optional[Phrase.LexResult]:
                return self._phrase.LexSuffix(
                    unique_id,
                    normalized_iter,
                    observer,
                    single_threaded=single_threaded,
                    ignore_whitespace=ignore_whitespace,
                )

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def PrettyPrint(
                indentation: str,
                data: Phrase.LexResultData.DataItemType,
                output_stream: TextIO,
            ) -> None:
                raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")

            # ----------------------------------------------------------------------
            @Interface.override
            def _PopulateRecursiveImpl(
                self,
                new_phrase: Phrase,
            ) -> bool:
                raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        # Nothing downstream has changed
        return False
