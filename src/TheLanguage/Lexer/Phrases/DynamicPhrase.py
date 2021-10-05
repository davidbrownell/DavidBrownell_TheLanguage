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

from typing import cast, Callable, Generator, List, Optional, Tuple, Union

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

        name = name or "Dynamic Phrase"

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
    @staticmethod
    def IsRightRecursivePhrase(
        phrase: Phrase,
        phrases_type: Optional[DynamicPhrasesType],
    ) -> bool:
        return (
            isinstance(phrase, SequencePhrase)
            and len(phrase.Phrases) > 2
            and isinstance(phrase.Phrases[-1], DynamicPhrase)
            and (
                phrases_type is None
                or phrase.Phrases[-1].DynamicPhrasesType == phrases_type
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
                return None

            if (
                result.Success
                and result.Data is not None
                and not await observer.OnInternalPhraseAsync(
                    result.Data,
                    result.IterBegin,
                    result.IterEnd,
                )
            ):
                return None

            return result

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    # BugBug: It might be possible to remove this
    _PREFIX_PHRASE_DECORATOR                = " <Prefix>" # BugBug: Remove
    _PREFIX_UNIQUE_ID_DECORATOR             = "Prefix"

    _SUFFIX_PHRASE_DECORATOR                = " <Suffix>" # BugBug: Remove
    _SUFFIX_UNIQUE_ID_DECORATOR_TEMPLATE    = "Suffix [i: {iteration}]"
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
        return Phrase.LexResult(
            result.Success,
            normalized_iter,
            result.IterEnd,
            # pylint: disable=too-many-function-args
            Phrase.StandardLexResultData(self, result.Data, unique_id),
        )

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

        # If here, we need to simulate greedy left-recursive consumption without devolving into
        # infinite recursion scenarios. To simulate this, simulate recursion interspersed with
        # attempts to match non-left-recursive phrases. Try the left recursive phrases at 1 level
        # of recursion first, then try the non-left-recursive phrases.

        assert left_recursive_phrases
        assert standard_phrases

        original_normalized_iter = normalized_iter.Clone()

        # Attempt to match the prefix
        prefix_phrase = OrPhrase(
            standard_phrases,
            name="{} <Prefix>".format(dynamic_phrases_name or ""),
        )

        prefix_result = await prefix_phrase.LexAsync(
            unique_id + ("Prefix", ),
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        if prefix_result is None:
            return None

        data = Phrase.StandardLexResultData(
            self,
            prefix_result.Data,
            prefix_result.Data.UniqueId if prefix_result.Data is not None else None,
        )

        if not prefix_result.Success:
            return Phrase.LexResult(
                False,
                original_normalized_iter,
                prefix_result.IterEnd,
                data,
            )

        normalized_iter = prefix_result.IterEnd

        # Attempt to match the suffix one or more times
        suffix_phrase = OrPhrase(
            [_SuffixWrapper(cast(SequencePhrase, phrase)) for phrase in left_recursive_phrases],
            name="{} <Suffix>".format(dynamic_phrases_name or ""),
        )

        iteration = 0

        while True:
            suffix_result = await suffix_phrase.LexAsync(
                unique_id + ("Suffix", str(iteration)),
                normalized_iter,
                observer,
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            iteration += 1

            if suffix_result is None:
                return None

            normalized_iter = suffix_result.IterEnd

            if not suffix_result.Success:
                if suffix_result.Data is not None:
                    # Augment the existing data with information about this error
                    data = Phrase.StandardLexResultData(
                        data.Phrase,
                        data.Data,
                        data.UniqueId,
                        suffix_result.Data,
                    )

                break

            assert suffix_result.Data is not None
            assert suffix_result.Data.Data is not None
            assert isinstance(suffix_result.Data.Data.Phrase, SequencePhrase)
            assert isinstance(suffix_result.Data.Data.Data, Phrase.MultipleLexResultData)
            assert len(suffix_result.Data.Data.Data.DataItems) == len(suffix_result.Data.Data.Phrase.Phrases) - 1

            suffix_result.Data.Data.Data.DataItems.insert(0, data)
            data = suffix_result.Data


         # BugBug
        return Phrase.LexResult(True, original_normalized_iter, normalized_iter, data)

















        # The first time through the loop, invoke the non-recursive phrase before the recursive
        # phrase. After that, invoke the recursive phrase before the non-recursive phrase.

        # ----------------------------------------------------------------------
        def Iterator() -> Generator[
            Tuple[str, Phrase, Phrase],
            None,
            None,
        ]:
            iteration = 0

            if not any(id_part.startswith("dyn: ") for id_part in unique_id):
                yield ("dyn: {}".format(iteration), non_recursive_phrase, recursive_phrase)

            while True:
                iteration += 1
                yield ("dyn: {}".format(iteration), recursive_phrase, non_recursive_phrase)

        # ----------------------------------------------------------------------

        original_normalized_iter = normalized_iter.Clone()

        iter = Iterator()

        data: Optional[Phrase.StandardLexResultData] = None
        error_results: List[Optional[Phrase.StandardLexResultData]] = []

        while len(error_results) < 2 and not normalized_iter.AtEnd():
            error_results = []

            iteration, phrase1, phrase2 = next(iter)

            for phrase, id_suffix in [
                (phrase1, "A"),
                (phrase2, "B"),
            ]:
                this_result = await phrase.LexAsync(
                    unique_id + (iteration, id_suffix),
                    normalized_iter,
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                if this_result.Success:
                    assert this_result.Data is not None
                    assert this_result.Data.Data is not None

                    if isinstance(this_result.Data.Data.Phrase, SequencePhrase):
                        assert data is not None
                        assert isinstance(this_result.Data.Data.Data, Phrase.MultipleLexResultData)
                        assert len(this_result.Data.Data.Data.DataItems) == len(this_result.Data.Data.Phrase.Phrases) - 1

                        this_result.Data.Data.Data.DataItems.insert(0, data)

                    data = this_result.Data
                    normalized_iter = this_result.IterEnd

                    break

                error_results.append(this_result.Data)

        if error_results:
            error_data = Phrase.MultipleLexResultData(
                cast(List[Optional[Phrase.LexResultData]], error_results),
                True,
            )
        else:
            error_data = None

        if data is None:
            data = Phrase.StandardLexResultData(
                self,
                error_data,
                unique_id,
            )

            success = False

        else:
            assert data.Data is not None

            data = Phrase.StandardLexResultData(
                self,
                data,
                unique_id,
                error_data,
            )

            if self.IsRightRecursivePhrase(data.Data.Data.Phrase, self.DynamicPhrasesType):
                right_data = data.Data.Data.Data.DataItems[-1]

                # Drill into the dynamic phrase and or phrase
                assert isinstance(right_data.Phrase, DynamicPhrase), right_data
                right_data = right_data.Data

                assert isinstance(right_data.Phrase, OrPhrase), right_data
                right_data = right_data.Data

                # Is this a dynamic phrase as well?
                if (
                    isinstance(right_data.Phrase, DynamicPhrase)
                    and isinstance(right_data.Data.Phrase, OrPhrase)
                    and self.IsRightRecursivePhrase(
                        right_data.Data.Data.Phrase,
                        right_data.Phrase.DynamicPhrasesType,
                    )
                ):
                    # Splitting phrases into those that are left-recursive and those that
                    # aren't avoids infinite recursion with left-recursive phrases, but it
                    # means that we are overly greedy for those phrases that are also right-
                    # recursive. So, we have to perform some tree manipulation to end up with
                    # the results that we want. The diagrams below illustrate the scenario and operations.
                    #
                    # Scenario:
                    #
                    #     1 + 2 - 3
                    #
                    # Which should be parsed as:
                    #
                    #     (1 + 2) - 3
                    #
                    # What we have (incorrect):
                    #
                    #     +      <-- root
                    #    / \
                    #   1   -    <-- pivot
                    #      / \
                    #     2   3
                    #
                    # What we want (correct):
                    #
                    #  pivot -->    -
                    #              / \
                    #  root -->   +   3
                    #            / \
                    #           1   2
                    #
                    # Adjust the tree accordingly.

                    root_data = data.Data.Data.Data
                    assert isinstance(root_data, Phrase.MultipleLexResultData)

                    pivot = root_data.DataItems[-1].Data.Data
                    pivot_data = pivot.Data.Data.Data
                    assert isinstance(pivot_data, Phrase.MultipleLexResultData)

                    root_data.DataItems[-1] = pivot_data.DataItems[0]
                    pivot_data.DataItems[0] = data

                    data = pivot

            success = True

        return Phrase.LexResult(success, original_normalized_iter, normalized_iter, data)















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

            data = Phrase.StandardLexResultData(self, root_data, unique_id)

        else:
            # The first result in the list of results needs to be updated to match the first phrase
            # within the sequence; use the data at index 1 as a reference to get this info.
            data_items[0] = Phrase.StandardLexResultData(  # pylint: disable=too-many-function-args
                cast(
                    SequencePhrase,
                    cast(
                        Phrase.StandardLexResultData,
                        data_items[1].Data,
                    ).Phrase,
                ).Phrases[0],
                data_items[0],
                data_items[0].UniqueId,
            )

            # For the remaining items, make the previous match the first element in the new match
            for data_item_index in range(1, len(data_items)):
                current_data_item = data_items[data_item_index]
                previous_data_item = data_items[data_item_index - 1]

                assert isinstance(current_data_item.Data, Phrase.StandardLexResultData)
                assert isinstance(current_data_item.Data.Phrase, SequencePhrase)
                assert isinstance(current_data_item.Data.Data, Phrase.MultipleLexResultData)
                assert len(current_data_item.Data.Data.DataItems) == len(current_data_item.Data.Phrase.Phrases) - 1

                current_data_item.Data.Data.DataItems.insert(0, previous_data_item)

            data = data_items[-1]

            # Splitting the phrases into those that are left-recursive and those that are not solved
            # the left-recursive problem, but created a new one in that the results now right-heavy.
            # For example, given the input "1 + 2 - 3", we get data that corresponds to:
            #
            # Before:
            #
            #     +      <-- root
            #    / \
            #   1   -    <-- pivot
            #      / \
            #     2   3
            #
            # But want a tree that looks like:
            #
            #
            # After:
            #
            #  pivot -->    -
            #              / \
            #  root -->   +   3
            #            / \
            #           1   2
            #
            # Adjust the tree accordingly.

            assert data.Data is not None

            if self.IsRightRecursivePhrase(data.Data.Phrase, self.DynamicPhrasesType):
                # If here, we know that the phrase is also left-recursive. Therefore, we only need
                # to worry about modifying the left- and right-most children.
                root = data

                assert isinstance(root, Phrase.StandardLexResultData)
                assert isinstance(root.Data, Phrase.StandardLexResultData)
                assert isinstance(root.Data.Phrase, SequencePhrase)
                assert isinstance(root.Data.Data, Phrase.MultipleLexResultData)

                pivot = root.Data.Data.DataItems[-1]

                assert isinstance(pivot, Phrase.StandardLexResultData)
                assert isinstance(pivot.Data, Phrase.StandardLexResultData)
                assert isinstance(pivot.Data.Phrase, SequencePhrase)
                assert isinstance(pivot.Data.Data, Phrase.MultipleLexResultData)

                BugBug = 10

            BugBug = 10

            # BugBug # The first result in the list of results needs to be updated to match the first phrase
            # BugBug # within the sequence; use the data at index 1 as a reference to get this info.
            # BugBug # Wrap this object in a 2nd layer of Parser.StandardLexResultData to ensure a
            # BugBug # consistent interface across all data items in the for loop below.
            # BugBug
            # BugBug data_items[0] = Phrase.StandardLexResultData(  # pylint: disable=too-many-function-args
            # BugBug     None,                                   # This value will never be used
            # BugBug     Phrase.StandardLexResultData(  # pylint: disable=too-many-function-args
            # BugBug         cast(
            # BugBug             SequencePhrase,
            # BugBug             cast(
            # BugBug                 Phrase.StandardLexResultData,
            # BugBug                 data_items[1].Data,
            # BugBug             ).Phrase,
            # BugBug         ).Phrases[0],
            # BugBug         data_items[0],
            # BugBug         data_items[0].UniqueId,
            # BugBug     ),
            # BugBug     data_items[0].UniqueId,                 # This value will never be used
            # BugBug )
            # BugBug
            # BugBug # For the remaining items, make the previous match the first element in the new match
            # BugBug for data_item_index in range(1, len(data_items)):
            # BugBug     previous_data_item_data = data_items[data_item_index - 1].Data
            # BugBug     current_data_item = data_items[data_item_index]
            # BugBug
            # BugBug     assert isinstance(current_data_item, Phrase.StandardLexResultData)
            # BugBug     assert isinstance(current_data_item.Data, Phrase.StandardLexResultData)
            # BugBug     assert isinstance(current_data_item.Data.Data, Phrase.MultipleLexResultData)
            # BugBug
            # BugBug     current_data_item.Data.Data.DataItems.insert(0, previous_data_item_data)
            # BugBug
            # BugBug data = cast(
            # BugBug     Phrase.StandardLexResultData,
            # BugBug     cast(Phrase.StandardLexResultData, data_items[-1]).Data,
            # BugBug )

            # We need to modify the tree itself, as the algorithm will produce a tree weighted towards
            # the right rather than one weighted towards the left.
            #
            # For example, given the phrase:
            #
            #     a + b - c
            #
            # We will have at this point:
            #
            #         +
            #        / \
            #       a   -
            #          / \
            #         b   c
            #
            # And what we want is:
            #
            #         -
            #        / \
            #       +   c
            #      / \
            #     a   b

            # BugBug
            #   a + b
            #   -
            #   c

            BugBug = 10

            # BugBug assert isinstance(root_data.Data, Phrase.MultipleLexResultData)
            # BugBug assert root_data.Data.DataItems
            # BugBug assert isinstance(root_data.Data.DataItems[-1], Phrase.StandardLexResultData)
            # BugBug assert isinstance(root_data.Data.DataItems[-1].Data, Phrase.StandardLexResultData)
            # BugBug assert isinstance(root_data.Data.DataItems[-1].Data.Data, Phrase.StandardLexResultData)
            # BugBug
            # BugBug if self.__class__.IsLeftRecursivePhrase(root_data.Data.DataItems[-1].Data.Data.Phrase, self.DynamicPhrasesType):
            # BugBug     new_root = root_data.Data.DataItems[-1]
            # BugBug
            # BugBug     root_data.Data.DataItems[-1] = root_data
            # BugBug     root_data = new_root
            # BugBug
            # BugBug
            # BugBug     BugBug = 10


            UpdateUniqueIds(data)

        assert data is not None

        if not await observer.OnInternalPhraseAsync(data, original_normalized_iter, normalized_iter):
            return None

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(True, original_normalized_iter, normalized_iter, data)


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
