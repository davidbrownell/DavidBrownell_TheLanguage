# ----------------------------------------------------------------------
# |
# |  DynamicPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 10:34:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DynamicPhrase object"""

import os

from typing import cast, Callable, List, Optional, Tuple, Union

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
    from ..Components.Phrase import DynamicPhrasesType, Phrase


# ----------------------------------------------------------------------
class DynamicPhrase(Phrase):
    """\
    Collects dynamic statements and invokes them, ensure that left-recursive phrases work as intended.

    Prevents infinite recursion for those phrases that are left recursive (meaning they belong to
    a category and consume that category as the first phrase within the sequence).

    Examples:
        # The phrase is an expression and the first phrase within the sequence is also an expression
        AddExpression:= <expr> '+' <expr>
        CastExpression:= <expr> 'as' <type>
        IndexExpression:= <expr> '[' <expr> ']'
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
            Tuple[List[Phrase], Optional[str]],         # List of phrases and optional name to refer to them by
        ],
        name: Optional[str]=None,
        include_names: Optional[List[Union[str, Phrase]]]=None,
        exclude_names: Optional[List[Union[str, Phrase]]]=None,
        left_recursive_include_names: Optional[List[Union[str, Phrase]]]=None,
        left_recursive_exclude_names: Optional[List[Union[str, Phrase]]]=None,
        left_recursive_standard_include_names: Optional[List[Union[str, Phrase]]]=None,
        left_recursive_standard_exclude_names: Optional[List[Union[str, Phrase]]]=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrases"

        super(DynamicPhrase, self).__init__(name)

        self.DynamicPhrasesType             = phrases_type
        self._get_dynamic_phrases_func      = get_dynamic_phrases_func

        # ----------------------------------------------------------------------
        def CreateIncludePhraseFunc(include_names, exclude_names):
            assert (
                (not include_names and not exclude_names)
                or not exclude_names
                or not include_names
            )

            if include_names:
                include_names = set(
                    [
                        phrase.Name if isinstance(phrase, Phrase) else phrase
                        for phrase in include_names
                    ],
                )

                return lambda phrase: phrase.Name in include_names

            if exclude_names:
                exclude_names = set(
                    [
                        phrase.Name if isinstance(phrase, Phrase) else phrase
                        for phrase in exclude_names
                    ],
                )

                return lambda phrase: phrase.Name not in exclude_names

            return lambda phrase: True

        # ----------------------------------------------------------------------

        self._standard_filter_func                      = CreateIncludePhraseFunc(include_names, exclude_names)
        self._left_recursive_filter_func                = CreateIncludePhraseFunc(left_recursive_include_names, left_recursive_exclude_names)
        self._left_recursive_standard_filter_func       = CreateIncludePhraseFunc(left_recursive_standard_include_names, left_recursive_standard_exclude_names)

    # ----------------------------------------------------------------------
    @staticmethod
    def IsLeftRecursivePhrase(
        phrase: Phrase,
        phrases_type: DynamicPhrasesType,
    ) -> bool:
        return (
            isinstance(phrase, SequencePhrase)
            and len(phrase.Phrases) > 1
            and isinstance(phrase.Phrases[0], DynamicPhrase)
            and phrase.Phrases[0].DynamicPhrasesType == phrases_type
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def LexAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.LexResult]:

        result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(
            lambda: observer.EndPhrase(unique_id, self, result is not None and result.Success)
        ):
            # Get the dynamic phrases
            dynamic_phrases, dynamic_phrases_name = self._get_dynamic_phrases_func(
                unique_id,
                self.DynamicPhrasesType,
                observer,
            )

            assert isinstance(dynamic_phrases, list), dynamic_phrases

            # Filter the list by those that have been explicitly included or excluded
            dynamic_phrases = [
                phrase for phrase in dynamic_phrases if self._standard_filter_func(phrase)
            ]

            # Split the phrases into those that are left-recursive and those that are not
            left_recursive_phrases = []
            standard_phrases = []

            for phrase in dynamic_phrases:
                if self.__class__.IsLeftRecursivePhrase(phrase, self.DynamicPhrasesType):
                    if self._left_recursive_filter_func(phrase):
                        left_recursive_phrases.append(phrase)
                else:
                    standard_phrases.append(phrase)

            if left_recursive_phrases:
                standard_phrases = [
                    phrase for phrase in standard_phrases if self._left_recursive_standard_filter_func(phrase)
                ]

                if standard_phrases:
                    result = await self._LexLeftRecursiveAsync(
                        dynamic_phrases_name,
                        left_recursive_phrases,
                        standard_phrases,
                        unique_id,
                        normalized_iter,
                        observer,
                        ignore_whitespace=ignore_whitespace,
                        single_threaded=single_threaded,
                    )
            elif standard_phrases:
                result = await self._LexStandardAsync(
                    dynamic_phrases_name,
                    standard_phrases,
                    unique_id,
                    normalized_iter,
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

            if result is None:
                # pylint: disable=too-many-function-args
                result = Phrase.LexResult(False, normalized_iter, normalized_iter, None)

            return result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        # Nothing downstream has changed
        return False

    # ----------------------------------------------------------------------
    async def _LexStandardAsync(
        self,
        dynamic_phrases_name: Optional[str],
        phrases: List[Phrase],
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        *,
        ignore_whitespace: bool,
        single_threaded: bool,
    ) -> Optional[Phrase.LexResult]:
        or_phrase = OrPhrase(
            phrases,
            name=dynamic_phrases_name,
        )

        result = await or_phrase.LexAsync(
            unique_id + (or_phrase.Name, ),
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        # pylint: disable=too-many-function-args
        data = Phrase.StandardLexResultData(self, result.Data, unique_id)

        if (
            result.Success
            and not await observer.OnInternalPhraseAsync(data, normalized_iter, result.IterEnd)
        ):
            return None

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(result.Success, normalized_iter, result.IterEnd, data)

    # ----------------------------------------------------------------------
    async def _LexLeftRecursiveAsync(
        self,
        dynamic_phrases_name: Optional[str],
        left_recursive_phrases: List[Phrase],
        standard_phrases: List[Phrase],
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        *,
        ignore_whitespace: bool,
        single_threaded: bool,
    ) -> Optional[Phrase.LexResult]:
        assert left_recursive_phrases
        assert standard_phrases

        success = False

        original_normalized_iter = normalized_iter.Clone()
        data_items: List[Optional[Phrase.LexResultData]] = []

        # Evaluate the prefix
        prefix_phrase = OrPhrase(
            standard_phrases,
            name="{} <Prefix>".format(dynamic_phrases_name) if dynamic_phrases_name else None,
        )

        result = await prefix_phrase.LexAsync(
            unique_id + ("Prefix", ),
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        data_items.append(result.Data)
        normalized_iter = result.IterEnd

        # Evaluate the suffix one or more times
        if result.Success:
            suffix_phrase = OrPhrase(
                [_SuffixWrapper(cast(SequencePhrase, phrase)) for phrase in left_recursive_phrases],
                name="{} <Suffix>".format(dynamic_phrases_name) if dynamic_phrases_name else None,
            )

            iteration = 0

            while True:
                result = await suffix_phrase.LexAsync(
                    unique_id + ("Suffix [{}]".format(iteration), ),
                    normalized_iter,
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                iteration += 1

                if result is None:
                    return None

                if len(data_items) == 1 or result.Success:
                    data_items.append(result.Data)
                    normalized_iter = result.IterEnd

                    success = result.Success

                if not result.Success:
                    break

        if not success:
            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                original_normalized_iter,
                normalized_iter,
                Phrase.StandardLexResultData(
                    self,
                    Phrase.MultipleLexResultData(data_items, True),
                    unique_id,
                ),
            )

        # When we return the results, we want it to appear as if the result came from the
        # original sequence (rather than a split between the prefix and suffix). Perform
        # some hackery on the results to achieve this illusion.
        assert len(data_items) >= 2

        for data_item_index, data_item in enumerate(data_items):
            assert isinstance(data_item, Phrase.StandardLexResultData)
            assert isinstance(data_item.Data, Phrase.StandardLexResultData)

            if data_item_index != len(data_items) - 1:
                if data_item_index == 0:
                    # Simulate the look and feel of results that would come from a standard DynamicPhrase

                    # pylint: disable=too-many-function-args
                    data_item_data = Phrase.StandardLexResultData(
                        cast(
                            SequencePhrase,
                            cast(
                                Phrase.StandardLexResultData,
                                cast(
                                    Phrase.StandardLexResultData,
                                    data_items[1],
                                ).Data,
                            ).Phrase,
                        ).Phrases[0],
                        data_item,
                        unique_id + ("Prefix", ),
                    )

                else:
                    data_item_data = data_item.Data

                data_item_next = data_items[data_item_index + 1]

                assert isinstance(data_item_next, Phrase.StandardLexResultData)
                assert isinstance(data_item_next.Data, Phrase.StandardLexResultData)
                assert isinstance(data_item_next.Data.Data, Phrase.MultipleLexResultData)

                data_item_next.Data.Data.DataItems.insert(0, data_item_data)

        root = cast(Phrase.StandardLexResultData, data_items[-1]).Data
        assert root

        # Update the unique ids to prevent caching (since we have changed relationships)

        unique_id_len = len(unique_id)

        # ----------------------------------------------------------------------
        def UpdateUniqueIds(
            data_item: Phrase.StandardLexResultData,
        ):
            assert data_item.UniqueId is not None
            assert len(data_item.UniqueId) > unique_id_len

            new_unique_id = (
                data_item.UniqueId[:unique_id_len]
                + ("**{}**".format(data_item.UniqueId[unique_id_len]),)
                + data_item.UniqueId[unique_id_len + 1:]
            )

            object.__setattr__(data_item, "UniqueId", new_unique_id)

            if data_item.Data is not None:
                for child in data_item.Data.Enum():
                    if isinstance(child, Phrase.TokenLexResultData):
                        continue

                    UpdateUniqueIds(child)

        # ----------------------------------------------------------------------

        UpdateUniqueIds(root)

        object.__setattr__(root, "UniqueId", unique_id)

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(True, original_normalized_iter, normalized_iter, root)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _SuffixWrapper(Phrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase: SequencePhrase,
    ):
        super(_SuffixWrapper, self).__init__("Wrapper ({})".format(phrase.Name))

        self._phrase                        = phrase

    # ----------------------------------------------------------------------
    @Interface.override
    async def LexAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.LexResult]:
        return await self._phrase.LexSuffixAsync(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")
