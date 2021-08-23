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

from typing import cast, List, Optional, Union

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
    @Interface.override
    async def ParseAsync(
        self,
        unique_id: List[str],
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

            result_data: List[Optional[Phrase.ParseResultData]] = []

            # Match the first phrase. The first part of the process will attempt to match
            # non-left-recursive phrases; the second part will use that information when
            # attempting to match left-recursive phrases other than this one.
            left_recursive_phrases = []

            # ----------------------------------------------------------------------
            def FilterDynamicPhrasesPartA(
                unique_id: List[str],
                phrases: List[Phrase],
            ) -> List[Phrase]:
                assert unique_id
                is_left_recursive = unique_id[-1].endswith("[0 <A>]")

                if not is_left_recursive:
                    return phrases

                standard_phrases = []

                for phrase in phrases:
                    if phrase == self:
                        continue

                    if isinstance(phrase, LeftRecursiveSequencePhrase):
                        left_recursive_phrases.append(phrase)
                    else:
                        standard_phrases.append(phrase)

                assert standard_phrases
                return standard_phrases

            # ----------------------------------------------------------------------

            result = None
            result = await self.Phrases[0].ParseAsync(
                unique_id + ["Sequence: {} [0 <A>]".format(self.Name)],
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

            normalized_iter = result.Iter

            assert result.Data
            result_data.append(result.Data)

            # Match any left-recursive content
            if left_recursive_phrases:
                # ----------------------------------------------------------------------
                def FilterDynamicPhrasesPartB(
                    unique_id: List[str],
                    phrases: List[Phrase],
                ) -> List[Phrase]:
                    # Note that the cast isn't correct here, but we are providing something
                    # that looks like a Phrase to the DynamicPhrase instance.
                    return [cast(Phrase, _PrefixWrapper(phrase)) for phrase in left_recursive_phrases]

                # ----------------------------------------------------------------------

                this_result = None
                this_result = await self.Phrases[0].ParseAsync(
                    unique_id + ["Sequence: {} [0 <B>]".format(self.Name)],
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
                    normalized_iter = this_result.Iter

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
            normalized_iter = result.Iter

            assert result.Data is not None
            assert result.Data.Data is not None
            assert isinstance(result.Data.Data, Phrase.MultipleStandardParseResultData)

            result_data += result.Data.Data.DataItems

            # Commit the results
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

            return Phrase.ParseResult(success, normalized_iter, data)

    # ----------------------------------------------------------------------
    async def ParseSuffixAsync(
        self,
        unique_id: List[str],
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
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _PrefixWrapper(Phrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase: LeftRecursiveSequencePhrase,
    ):
        super(_PrefixWrapper, self).__init__("_PrefixWrapper")

        self._phrase                    = phrase

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        unique_id: List[str],
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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        raise Exception("This should never be called, as this object should never be instantiated as part of a Phrase hierarchy")
