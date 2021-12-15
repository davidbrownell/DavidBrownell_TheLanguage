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
import uuid

from typing import cast, Callable, Generator, List, Optional, Tuple, Union

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

    from ..Components.Phrase import DynamicPhrasesType, Phrase


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
            Tuple[List[Phrase], Optional[str]],         # List of phrases and optional name to refer to them by
        ],
        name: Optional[str]=None,
        include_phrases: Optional[List[Union[str, Phrase]]]=None,
        exclude_phrases: Optional[List[Union[str, Phrase]]]=None,
        is_valid_data_func: Optional[Callable[[Phrase.StandardLexResultData], bool]]=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrase"

        super(DynamicPhrase, self).__init__(name)

        self.DynamicPhrasesType             = phrases_type
        self._get_dynamic_phrases_func      = get_dynamic_phrases_func
        self._display_name: Optional[str]   = None

        # ----------------------------------------------------------------------
        def CreateIncludePhraseFunc(include_phrase, exclude_phrases):
            assert (
                (not include_phrase and not exclude_phrases)
                or not exclude_phrases
                or not include_phrase
            )

            if include_phrase:
                include_phrase = set(
                    [
                        phrase.Name if isinstance(phrase, Phrase) else phrase
                        for phrase in include_phrase
                    ],
                )

                return lambda phrase: phrase.Name in include_phrase

            if exclude_phrases:
                exclude_phrases = set(
                    [
                        phrase.Name if isinstance(phrase, Phrase) else phrase
                        for phrase in exclude_phrases
                    ],
                )

                return lambda phrase: phrase.Name not in exclude_phrases

            return lambda phrase: True

        # ----------------------------------------------------------------------

        self._pre_phrase_filter_func        = CreateIncludePhraseFunc(include_phrases, exclude_phrases)
        self._is_valid_data_func            = is_valid_data_func or (lambda *args, **kwargs: True)

    # ----------------------------------------------------------------------
    @property
    def DisplayName(self):
        return self._display_name or self.Name

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
                or cast(DynamicPhrase, phrase.Phrases[-1]).DynamicPhrasesType == phrases_type
            )
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def SkipDynamicData(
        data: Phrase.StandardLexResultData,
    ) -> Phrase.StandardLexResultData:
        assert isinstance(data.Phrase, DynamicPhrase)
        assert isinstance(data.Data, Phrase.StandardLexResultData)

        data = data.Data

        assert isinstance(data.Phrase, OrPhrase)
        assert isinstance(data.Data, Phrase.StandardLexResultData)

        data = data.Data

        return data

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

            self._display_name = dynamic_phrases_name

            # Filter the list by those that have been explicitly included or excluded
            dynamic_phrases = [
                phrase for phrase in dynamic_phrases if self._pre_phrase_filter_func(phrase)
            ]

            # TODO: Is there a way to cache these results so that we don't have to filter over and over?

            # Split the phrases into those that are left-recursive and those that are not
            left_recursive_phrases = []
            standard_phrases = []

            for phrase in dynamic_phrases:
                if self.__class__.IsLeftRecursivePhrase(phrase, self.DynamicPhrasesType):
                    left_recursive_phrases.append(phrase)
                else:
                    standard_phrases.append(phrase)

            if left_recursive_phrases:
                assert standard_phrases

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
                and not observer.OnInternalPhrase(
                    result.Data,
                    result.IterBegin,
                    result.IterEnd,
                )
            ):
                return None

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

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(
            result.Success,
            Phrase.NormalizedIteratorRange(normalized_iter, result.IterEnd),
            data,
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

        # ----------------------------------------------------------------------
        def PhraseIterator() -> Generator[
            Tuple[
                Phrase,
                Tuple[str, ...],
            ],
            None,
            None
        ]:
            # Prefix
            yield (
                OrPhrase(
                    standard_phrases,
                    name="{} <Prefix>".format(dynamic_phrases_name or ""),
                ),
                unique_id + ("__Prefix__", ),
            )

            # Suffix(es)
            suffix_phrase = OrPhrase(
                [
                    _SequenceSuffixWrapper(cast(SequencePhrase, phrase))
                    for phrase in left_recursive_phrases
                ],
                name="{} <Suffix>".format(dynamic_phrases_name or ""),
            )

            iteration = 0

            while True:
                yield (suffix_phrase, unique_id + ("__Suffix__", str(iteration)))
                iteration += 1

        # ----------------------------------------------------------------------

        original_normalized_iter = normalized_iter.Clone()

        data_items: List[Phrase.StandardLexResultData] = []

        phrase_iterator = PhraseIterator()

        while True:
            this_phrase, this_unique_id = next(phrase_iterator)

            this_result = await this_phrase.LexAsync(
                this_unique_id,
                normalized_iter,
                observer,
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if this_result is None:
                return None

            if not data_items or this_result.Success:
                normalized_iter = this_result.IterEnd

            assert this_result.Data is not None
            data_items.append(this_result.Data)

            if not this_result.Success:
                break

        assert not normalized_iter.AtEnd()

        error_data_item = data_items.pop()

        if not data_items:
            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                Phrase.NormalizedIteratorRange(original_normalized_iter, normalized_iter),
                Phrase.StandardLexResultData(self, error_data_item, unique_id),
            )

        # Strip the prefix- and suffix-cruft from the output data so that we can simulate a standard
        # phrase.
        for data_item_index, data_item in enumerate(data_items):
            assert isinstance(data_item.Phrase, OrPhrase), data_item.Phrase
            assert data_item.Data is not None

            data_items[data_item_index] = data_item.Data

        # Create an OrPhrase item that looks like what would be generated by the standard lexer
        pseudo_or_phrase = OrPhrase(
            left_recursive_phrases + standard_phrases,
            name=dynamic_phrases_name,
        )

        # Massage the results into the expected format
        for data_item_index, data_item in enumerate(data_items):
            if data_item_index != 0:
                previous_data_item = data_items[data_item_index - 1]

                assert isinstance(data_item.Phrase, SequencePhrase)
                assert isinstance(data_item.Data, Phrase.MultipleLexResultData)

                # The number of existing (non-ignored) data items should be 1 less than the number
                # of expected (non-control-token) data items; merging this one will complete the phrase.
                non_ignored_data_items = sum(
                    1 if not isinstance(di, Phrase.TokenLexResultData) or not di.IsIgnored else 0
                    for di in data_item.Data.DataItems
                )

                non_control_token_phrases = sum(
                    1 if not isinstance(phrase, TokenPhrase) or not phrase.Token.is_control_token else 0
                    for phrase in data_item.Phrase.Phrases
                )

                assert non_ignored_data_items == non_control_token_phrases - 1

                # Insert the previous element into the current data item
                data_item.Data.DataItems.insert(0, previous_data_item)

            # pylint: disable=too-many-function-args
            data_items[data_item_index] = Phrase.StandardLexResultData(
                self,
                Phrase.StandardLexResultData(
                    pseudo_or_phrase,
                    data_item,
                    # Don't worry about providing an unique_id here, as they are all going to be
                    # overwritten below.
                    unique_id,
                ),
                unique_id,
            )

        data = data_items[-1]

        # We may need to alter the tree if we are working with a combination of left- and right-
        # recursive phrases
        value_data = self.SkipDynamicData(data)

        if (
            self.IsLeftRecursivePhrase(value_data.Phrase, self.DynamicPhrasesType)
            and self.__class__.IsRightRecursivePhrase(value_data.Phrase, self.DynamicPhrasesType)
        ):
            assert isinstance(value_data.Data, Phrase.MultipleLexResultData)
            assert isinstance(value_data.Data.DataItems[-1], Phrase.StandardLexResultData)

            value_data = self.SkipDynamicData(cast(Phrase.StandardLexResultData, value_data.Data.DataItems[-1]))

            if self.__class__.IsRightRecursivePhrase(value_data.Phrase, self.DynamicPhrasesType):
                # TODO: Add tests with a combo of mathematical, logical, and func operators ('.', '->', etc.)
                #       Not all types should support this decoration, but right now it is applied to all; tests
                #       will illustrate the problem.
                #
                #             one and two.three.Four() -> (((one and two).three).Four())     <<This is not correct>>

                # Splitting phrases into those that are left-recursive and those that
                # aren't avoids infinite recursion with left-recursive phrases, but it
                # means that we are overly greedy for those phrases that are also right-
                # recursive. So, we have to perform some tree manipulation to end up with
                # the results that we want. The diagrams below illustrate the scenario and operations.
                #
                #   ==============================================================================
                #
                #   Scenario                            Should be parsed as:
                #   ----------------------------------  ------------------------------------------
                #   1 + 2 - 3                           ((1 + 2) - 3)
                #
                #   What we have (incorrect):           What we want (correct):
                #   ----------------------------------  ------------------------------------------
                #   root -->     +                      new_root --> -
                #               / \                                 / \
                #              1   -   <-- new_root     root -->   +   3
                #                 / \                             / \
                #   travel -->   2   3                           1   2  <-- travel
                #
                #   ==============================================================================
                #
                #   Scenario                            Should be parsed as:
                #   ----------------------------------  ------------------------------------------
                #   1 + 2 - 3 * 4                       (((1 + 2) - 3) * 4)
                #
                #   What we have (incorrect):           What we want (correct):
                #   ----------------------------------  ------------------------------------------
                #   root -->     +                      new_root --> *
                #               / \                                 / \
                #              1   *    <-- new_root               -   4
                #                 / \                             / \
                #   travel -->   -   4                  root --> +   3
                #               / \                             / \
                #              2   3                           1   2  <-- travel
                #
                #   ==============================================================================
                #
                #   1) Identify travel (left-most left-recursive phrase)
                #   2) Root last = travel first
                #   3) Travel first = root
                #   4) Root = new root

                root_dynamic = data
                root_actual = self.SkipDynamicData(root_dynamic)

                assert isinstance(root_actual.Phrase, SequencePhrase)
                assert isinstance(root_actual.Data, Phrase.MultipleLexResultData)

                new_root_dynamic = root_actual.Data.DataItems[-1]
                new_root_actual = self.SkipDynamicData(cast(Phrase.StandardLexResultData, new_root_dynamic))

                assert isinstance(new_root_actual.Phrase, SequencePhrase)
                assert isinstance(new_root_actual.Data, Phrase.MultipleLexResultData)

                travel = new_root_actual

                while True:
                    potential_travel_dynamic = travel.Data.DataItems[0]
                    potential_travel_actual = self.SkipDynamicData(potential_travel_dynamic)

                    if not self.__class__.IsRightRecursivePhrase(potential_travel_actual.Phrase, self.DynamicPhrasesType):
                        break

                    travel = potential_travel_actual

                root_actual.Data.DataItems[-1] = travel.Data.DataItems[0]
                travel.Data.DataItems[0] = data

                data = new_root_dynamic

        # Should this data be considered as valid?
        assert isinstance(data, Phrase.StandardLexResultData)

        if not self._is_valid_data_func(data):
            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                Phrase.NormalizedIteratorRange(original_normalized_iter, normalized_iter),
                data,
            )

        # At this point, we have massaged and modified the structure of the tree to the point where
        # attempting to use previously cached values will not work. Update all of the unique_ids for
        # all data in the hierarchy to prevent caching.

        unique_id_suffix_str = "Pseudo ({})".format(uuid.uuid4())
        unique_id_suffix_iteration = 0

        # ----------------------------------------------------------------------
        def UpdateUniqueIds(
            data: Optional[Phrase.LexResultData],
        ):
            nonlocal unique_id_suffix_iteration

            if data is None:
                return

            if isinstance(data, Phrase.StandardLexResultData):
                object.__setattr__(
                    data,
                    "unique_id",
                    (unique_id_suffix_str, str(unique_id_suffix_iteration), ),
                )

                unique_id_suffix_iteration += 1
                UpdateUniqueIds(data.Data)

            elif isinstance(data, Phrase.MultipleLexResultData):
                for data_item in data.DataItems:
                    UpdateUniqueIds(data_item)

            elif isinstance(data, Phrase.TokenLexResultData):
                # Nothing to do here
                pass

            else:
                assert False, data  # pragma: no cover

        # ----------------------------------------------------------------------

        UpdateUniqueIds(data)

        # Create data that includes the error info
        data = cast(Phrase.StandardLexResultData, data)

        # pylint: disable=too-many-function-args
        data = Phrase.StandardLexResultData(
            data.Phrase,
            data.Data,
            data.UniqueId,
            error_data_item,
        )

        # pylint: disable=too-many-function-args
        return Phrase.LexResult(
            True,
            Phrase.NormalizedIteratorRange(original_normalized_iter, normalized_iter),
            cast(Phrase.StandardLexResultData, data),
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
        super(_SequenceSuffixWrapper, self).__init__("Wrapper ({})".format(phrase.Name))

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
