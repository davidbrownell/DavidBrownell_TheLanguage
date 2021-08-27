# ----------------------------------------------------------------------
# |
# |  LeftRecursiveSequencePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-22 18:51:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LeftRecursiveSequencePhrase object"""

import os

from typing import List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .DynamicPhrase import DynamicPhrase
    from .SequencePhrase import Phrase, RegexToken, SequencePhrase


# ----------------------------------------------------------------------
class LeftRecursiveSequencePhrase(SequencePhrase):
    """\
    SequencePhrase where the first phrase is a dynamic expression that
    belongs to the same category as the one that this belongs to. For example:

        BinaryExpression:= <expr> '+' <expr>            # The first phrase is an expression as is this phrase

    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        comment_token: RegexToken,
        phrases: List[Phrase],
        name: str=None,
    ):
        assert phrases
        assert isinstance(phrases[0], DynamicPhrase)
        assert len(phrases) > 1

        super(LeftRecursiveSequencePhrase, self).__init__(
            comment_token,
            phrases,
            name=name,
        )

    # ----------------------------------------------------------------------
    async def ParseSuffixAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Phrase.ParseResult,
        None,
    ]:
        return await self._MatchAsync(
            1,
            unique_id,
            normalized_iter,
            observer,
            single_threaded,
            1 if ignore_whitespace else 0,
            None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def _ParseAsyncImpl(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Phrase.ParseResult,
        None,
    ]:
        success = False

        observer.StartPhrase(unique_id, [self])
        with CallOnExit(lambda: observer.EndPhrase(unique_id, [(self, success)])):
            original_normalized_iter = normalized_iter.Clone()

            part1_unique_id_suffix = "[0 <A>]"
            part2_unique_id_suffix = "[0 <B>]"

            result_data: List[Optional[Phrase.ParseResultData]] = []

            # Match the first phrase in the sequence. The first part of the process will attempt
            # to match non-left-recursive phrases; the second part will use that information when
            # attempting to match left-recursive phrases other than this one.
            unique_id_depth = len(unique_id)
            left_recursive_phrases = []

            # ----------------------------------------------------------------------
            def FilterDynamicPhrasesPartA(
                unique_id: Tuple[str, ...],
                name: Optional[str],
                phrases: List[Phrase],
            ) -> Tuple[Optional[str], List[Phrase]]:

                # This filter function will be used for this left-recursive phrase and also downstream
                # phrases; only filter the list of phrases for this phrase.
                assert unique_id

                is_this_left_recursive = (
                    len(unique_id) == unique_id_depth + 1
                    and unique_id[-1].endswith(part1_unique_id_suffix)
                    and self.Name in unique_id[-1]
                )

                if not is_this_left_recursive:
                    return name, phrases

                # Split the list of phrases into those that are left-recursive and those that are not.
                # During part A, we will return those phrases that are not left-recursive and save
                # those that are for part B.
                assert not left_recursive_phrases

                standard_phrases = []

                for phrase in phrases:
                    if isinstance(phrase, LeftRecursiveSequencePhrase):
                        if phrase == self:
                            continue

                        left_recursive_phrases.append(phrase)
                    else:
                        standard_phrases.append(phrase)

                return name, standard_phrases

            # ----------------------------------------------------------------------

            result = None
            result = await self.Phrases[0].ParseAsync(
                unique_id + ("Sequence: {} {}".format(self.Name, part1_unique_id_suffix), ),
                normalized_iter,
                Phrase.ObserverDecorator(
                    self,
                    unique_id,
                    observer,
                    [result],
                    lambda result: result.Data,
                    post_filter_dynamic_phrases_func=FilterDynamicPhrasesPartA,
                ),
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            if not result.Success:
                return result

            normalized_iter = result.IterEnd

            assert result.Data
            result_data.append(result.Data)

            # Match any left-recursive content
            if left_recursive_phrases:
                # ----------------------------------------------------------------------
                def FilterDynamicPhrasesPartB(
                    unique_id: Tuple[str, ...],
                    name: Optional[str],
                    phrases: List[Phrase],
                ) -> Tuple[Optional[str], List[Phrase]]:

                    # This filter function will be used for this left-recursive phrase and also downstream
                    # phrases; only filter the list of phrases for this phrase.
                    assert unique_id

                    # Make sure that we are processing this phrase and not downstream phrases
                    is_this_left_recursive = (
                        len(unique_id) == unique_id_depth + 1
                        and unique_id[-1].endswith(part2_unique_id_suffix)
                        and self.Name in unique_id[-1]
                    )

                    if not is_this_left_recursive:
                        return name, phrases

                    # Return the left-recursive phrases captured in part A.
                    return "_SuffixWrappers", [_SuffixWrapper(phrase) for phrase in left_recursive_phrases]

                # ----------------------------------------------------------------------

                this_result = None
                this_result = await self.Phrases[0].ParseAsync(
                    unique_id + ("Sequence: {} {}".format(self.Name, part2_unique_id_suffix), ),
                    normalized_iter,
                    Phrase.ObserverDecorator(
                        self,
                        unique_id,
                        observer,
                        [this_result],
                        lambda result: result.Data,
                        post_filter_dynamic_phrases_func=FilterDynamicPhrasesPartB,
                    ),
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                if this_result is None:
                    return None

                if this_result.Success:
                    normalized_iter = this_result.IterEnd

                    assert result.Data is not None
                    result_data.append(this_result.Data)

            # Match the remainder of the sequence
            result = await self.ParseSuffixAsync(
                unique_id,
                normalized_iter,
                observer,
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            success = result.Success
            normalized_iter = result.IterEnd

            assert result.Data is not None
            assert result.Data.Data is not None
            assert isinstance(result.Data.Data, Phrase.MultipleStandardParseResultData)

            result_data += result.Data.Data.DataItems

            # Commit the results
            # <Too many arguments> pylint: disable=E1121
            data = Phrase.StandardParseResultData(
                self,
                Phrase.MultipleStandardParseResultData(result_data, True),
                unique_id,
            )

            if (
                success
                and not await observer.OnInternalPhraseAsync(
                    [data],
                    original_normalized_iter,
                    normalized_iter,
                )
            ):
                return None

            # <Too many arguments> pylint: disable=E1121
            return Phrase.ParseResult(success, original_normalized_iter, normalized_iter, data)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _SuffixWrapper(Phrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase: LeftRecursiveSequencePhrase,
    ):
        super(_SuffixWrapper, self).__init__("_SuffixWrapper ({})".format(phrase.Name))

        self._phrase                    = phrase

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
        return await self._phrase.ParseSuffixAsync(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )
