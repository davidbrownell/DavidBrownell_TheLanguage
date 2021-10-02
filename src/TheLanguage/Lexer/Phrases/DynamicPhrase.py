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
from CommonEnvironment import RegularExpression

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
    # |
    # |  Public Methods
    # |
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
        phrases_type: Optional[DynamicPhrasesType],
    ) -> bool:
        return (
            isinstance(phrase, SequencePhrase)
            and len(phrase.Phrases) > 1
            and isinstance(phrase.Phrases[0], DynamicPhrase)
            and (
                phrases_type is None
                or phrase.Phrases[0].DynamicPhrasesType == phrases_type
            )
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

            # TODO: Is there a way to cache these results so that we don't have to filter over and over?

            # Split the phrases into those that are left-recursive and those that are not
            left_recursive_phrases = []
            standard_phrases = []

            for phrase in dynamic_phrases:
                if self.__class__.IsLeftRecursivePhrase(phrase, self.DynamicPhrasesType):
                    if self._left_recursive_filter_func(phrase):
                        left_recursive_phrases.append(phrase)
                else:
                    standard_phrases.append(phrase)

            if (
                left_recursive_phrases
                and not self.__class__._IsLeftRecursiveSuffixInvocation(unique_id)
            ):
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
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _PREFIX_PHRASE_DECORATOR                = " <Prefix>"
    _PREFIX_UNIQUE_ID_DECORATOR             = "Prefix"

    _SUFFIX_PHRASE_DECORATOR                = " <Suffix>"
    _SUFFIX_UNIQUE_ID_DECORATOR_TEMPLATE    = "Suffix [{iteration}]"
    _SUFFIX_UNIQUE_ID_DECORATOR_REGEX       = RegularExpression.TemplateStringToRegex(_SUFFIX_UNIQUE_ID_DECORATOR_TEMPLATE)

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

    # ----------------------------------------------------------------------
    @classmethod
    def _IsLeftRecursiveSuffixInvocation(
        cls,
        unique_id: Tuple[str, ...],
    ) -> bool:
        for id_part in unique_id:
            if cls._SUFFIX_UNIQUE_ID_DECORATOR_REGEX.match(id_part):  # type: ignore
                return True

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

        original_normalized_iter = normalized_iter.Clone()
        data_items: List[Phrase.StandardLexResultData] = []

        # Evaluate the prefix
        prefix_phrase = OrPhrase(
            standard_phrases,
            name="{}{}".format(
                dynamic_phrases_name or "",
                self.__class__._PREFIX_PHRASE_DECORATOR,
            ),
        )

        result = await prefix_phrase.LexAsync(
            unique_id + (self.__class__._PREFIX_PHRASE_DECORATOR, ),
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        assert result.Data is not None
        data_items.append(result.Data)
        normalized_iter = result.IterEnd

        prefix_success = result.Success
        suffix_success = False

        # Evaluate the suffix one or more times
        if prefix_success:
            suffix_phrase = OrPhrase(
                [_SuffixWrapper(cast(SequencePhrase, phrase)) for phrase in left_recursive_phrases],
                name="{}{}".format(
                    dynamic_phrases_name or "",
                    self.__class__._SUFFIX_PHRASE_DECORATOR,
                ),
            )

            iteration = 0

            while True:
                result = await suffix_phrase.LexAsync(
                    unique_id + (self.__class__._SUFFIX_UNIQUE_ID_DECORATOR_TEMPLATE.format(iteration=iteration), ),
                    normalized_iter,
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                iteration += 1

                if result is None:
                    return None

                if len(data_items) == 1 or result.Success:
                    assert result.Data is not None
                    data_items.append(result.Data)

                    normalized_iter = result.IterEnd

                    suffix_success = result.Success

                if not result.Success:
                    break

        if not prefix_success and not suffix_success:
            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                original_normalized_iter,
                normalized_iter,
                Phrase.StandardLexResultData(
                    self,
                    Phrase.MultipleLexResultData(
                        cast(List[Optional[Phrase.LexResultData]], data_items),
                        True,
                    ),
                    unique_id,
                ),
            )

        # When we return the results, we want it to appear as if the result came from the original
        # phrase(s) (rather than a split between the prefix and suffix). Doctor the results to
        # achieve this illusion.
        assert len(data_items) >= 2

        # As part of this hackery, we will need to update the unique ids to prevent caching
        # (since we have changed relationships).
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

        if not suffix_success:
            assert prefix_success

            # If here, we matched a phrase but not a left-recursive phrase. Update the results to match
            # what would be produced if we matched that phrase in isolation (but associate the error
            # results of attempting to match the suffix in case there are errors upstream).

            # pylint: disable=too-many-function-args
            root_data = Phrase.StandardLexResultData(
                data_items[0].Phrase,
                data_items[0].Data,
                data_items[0].UniqueId,
                data_items[1],
            )

            assert root_data.Data is not None
            UpdateUniqueIds(root_data.Data)

            root_data = Phrase.StandardLexResultData(self, root_data, unique_id)

        else:
            # The first result in the list of results needs to be updated to match the first phrase
            # within the sequence; use the data at index 1 as a reference to get this info.
            # Wrap this object in a 2nd layer of Parser.StandardLexResultData to ensure a
            # consistent interface across all data items in the for loop below.

            data_items[0] = Phrase.StandardLexResultData(  # pylint: disable=too-many-function-args
                None,                                   # This value will never be used
                Phrase.StandardLexResultData(  # pylint: disable=too-many-function-args
                    cast(
                        SequencePhrase,
                        cast(
                            Phrase.StandardLexResultData,
                            data_items[1].Data,
                        ).Phrase,
                    ).Phrases[0],
                    data_items[0],
                    data_items[0].UniqueId,
                ),
                data_items[0].UniqueId,                 # This value will never be used
            )

            # For the remaining items, make the previous match the first element in the new match
            for data_item_index in range(1, len(data_items)):
                previous_data_item_data = data_items[data_item_index - 1].Data
                current_data_item = data_items[data_item_index]

                assert isinstance(current_data_item, Phrase.StandardLexResultData)
                assert isinstance(current_data_item.Data, Phrase.StandardLexResultData)
                assert isinstance(current_data_item.Data.Data, Phrase.MultipleLexResultData)

                current_data_item.Data.Data.DataItems.insert(0, previous_data_item_data)

            root_data = cast(
                Phrase.StandardLexResultData,
                cast(Phrase.StandardLexResultData, data_items[-1]).Data,
            )

            UpdateUniqueIds(root_data)

        assert root_data is not None
        assert root_data.Data is not None

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(True, original_normalized_iter, normalized_iter, root_data)


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
