# ----------------------------------------------------------------------
# |
# |  LeftRecursiveSequencePhraseWrapper.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-27 09:40:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LeftRecursiveSequencePhraseWrapper object"""

import os

from typing import cast, List, Optional, Set, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.CallOnExit import CallOnExit

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .DynamicPhrase import DynamicPhrase
    from .OrPhrase import OrPhrase
    from .SequencePhrase import SequencePhrase
    from ..Components.Phrase import DynamicPhrasesType, Phrase


# ----------------------------------------------------------------------
class LeftRecursiveSequencePhraseWrapper(Phrase):
    """\
    Prevents infinite recursion for those phrases that are left recursive (meaning they belong to
    a category and consume that category as the first phrase within the sequence).

    Examples:
        # The phrase is an expression and the first phrase within the sequence is also an expression
        AddExpression:= <expr> '+' <expr>
        CastExpression:= <expr> 'as' <type>
        IndexExpression:= <expr> '[' <expr> ']'

    This wrapper can only be instantiated after all of the non-left-recursive phrases and left-recursive
    phrases have been identified; in other words, an end use would not instantiate this class directly,
    but rather rely on the other phrase building blocks when creating custom phrases.
    """

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
    def __init__(
        self,
        dynamic_phrases_type: DynamicPhrasesType,
        standard_phrases: List[Phrase],
        left_recursive_phrases: List[SequencePhrase],
        name: str=None,
        prefix_name: str=None,
        suffix_name: str=None,
    ):
        assert standard_phrases
        assert left_recursive_phrases
        assert all(self.IsLeftRecursivePhrase(phrase, dynamic_phrases_type) for phrase in left_recursive_phrases)

        name = name or "LeftRecursiveSequencePhraseWrapper"

        super(LeftRecursiveSequencePhraseWrapper, self).__init__(name)

        self.DynamicPhrasesType             = dynamic_phrases_type
        self.StandardPhrases                = standard_phrases
        self.LeftRecursivePhrases           = left_recursive_phrases

        self._prefix_name                   = prefix_name or "{} <Prefix>".format(name)
        self._suffix_name                   = suffix_name or "{} <Suffix>".format(name)

        self._prefix_phrase                 = None      # Updated below
        self._suffix_phrase                 = None      # Updated below

        self._UpdateInternalPhrases()

    # ----------------------------------------------------------------------
    def ExcludePhrases(
        self,
        phrases: Union[
            List[Union[str, Phrase]],
            Set[str],
        ],
    ):
        if not isinstance(phrases, set):
            phrases = set(
                [
                    phrase.Name if isinstance(phrase, Phrase) else phrase
                    for phrase in phrases
                ],
            )

        self.StandardPhrases = [phrase for phrase in self.StandardPhrases if phrase.Name not in phrases]
        self.LeftRecursivePhrases = [phrase for phrase in self.LeftRecursivePhrases if phrase.Name not in phrases]

        self._UpdateInternalPhrases()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")

    # ----------------------------------------------------------------------
    @Interface.override
    async def _ParseAsyncImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.ParseResult]:
        success = False

        original_normalized_iter = normalized_iter.Clone()
        data_items: List[Optional[Phrase.ParseResultData]] = []

        # Evaluate the prefix
        assert self._prefix_phrase is not None

        result = await self._prefix_phrase.ParseAsync(
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

        # Evaluate the suffix
        if result.Success:
            assert self._suffix_phrase is not None

            iteration = 0

            while True:
                result = await self._suffix_phrase.ParseAsync(
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
            # <Too many positional arguments> pylint: disable=E1121
            return Phrase.ParseResult(
                False,
                original_normalized_iter,
                normalized_iter,
                Phrase.StandardParseResultData(
                    self,
                    Phrase.MultipleStandardParseResultData(data_items, True),
                    unique_id,
                ),
            )

        # When we return the results, we want it to appear as if the result came from the
        # original sequence (rather than a split between the prefix and suffix). Perform
        # some hackery on the results to achieve this illusion.

        unique_id_len = len(unique_id)

        # ----------------------------------------------------------------------
        def UpdateUniqueIds(
            data_item: Phrase.StandardParseResultData,
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
                    if isinstance(child, Phrase.TokenParseResultData):
                        continue

                    UpdateUniqueIds(child)

        # ----------------------------------------------------------------------

        assert len(data_items) >= 2

        for data_item_index, data_item in enumerate(data_items):
            assert isinstance(data_item, Phrase.StandardParseResultData)
            assert isinstance(data_item.Data, Phrase.StandardParseResultData)

            if data_item_index != len(data_items) - 1:
                if data_item_index == 0:
                    # Simulate the look and feel of results that would come from a
                    # standard DynamicPhrase

                    # <Too many positional arguments> pylint: disable=E1121
                    data_item_data = Phrase.StandardParseResultData(
                        cast(
                            SequencePhrase,
                            cast(
                                Phrase.StandardParseResultData,
                                cast(
                                    Phrase.StandardParseResultData,
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

                assert isinstance(data_item_next, Phrase.StandardParseResultData)
                assert isinstance(data_item_next.Data, Phrase.StandardParseResultData)
                assert isinstance(data_item_next.Data.Data, Phrase.MultipleStandardParseResultData)

                data_item_next.Data.Data.DataItems.insert(0, data_item_data)

        root = cast(Phrase.StandardParseResultData, data_items[-1]).Data
        assert root

        # Update the unique ids to prevent caching since we have changed relationships
        UpdateUniqueIds(root)

        object.__setattr__(root, "UniqueId", unique_id)

        # <Too many positional arguments> pylint: disable=E1121
        return Phrase.ParseResult(True, original_normalized_iter, normalized_iter, root)

    # ----------------------------------------------------------------------
    def _UpdateInternalPhrases(self):
        self._prefix_phrase = OrPhrase(
            self.StandardPhrases,
            name=self._prefix_name,
        )

        self._suffix_phrase = OrPhrase(
            [_SuffixWrapper(phrase) for phrase in self.LeftRecursivePhrases],
            name=self._suffix_name,
        )


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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")

    # ----------------------------------------------------------------------
    @Interface.override
    async def _ParseAsyncImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Optional[Phrase.ParseResult]:
        return await cast(SequencePhrase, self._phrase).ParseSuffixAsync(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )
