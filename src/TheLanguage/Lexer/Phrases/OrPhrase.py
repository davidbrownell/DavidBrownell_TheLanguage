# ----------------------------------------------------------------------
# |
# |  OrPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 10:03:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the OrPhrase object"""

import os
import textwrap

from typing import List, Optional, Tuple

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .RecursivePlaceholderPhrase import RecursivePlaceholderPhrase
    from ..Components.Phrase import Phrase


# ----------------------------------------------------------------------
class OrPhrase(Phrase):
    """Attempts to match one of the provided phrases"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrases: List[Phrase],
        sort_results=True,
        name: Optional[str]=None,

        # By default, ambiguity results when multiple phrases are successfully matched for the same
        # amount of data. When this value is set to True, the phrase order will be used to resolve
        # this ambiguity rather than generating an error.
        ambiguities_resolved_by_order: Optional[bool]=None,
    ):
        assert phrases
        assert all(phrase for phrase in phrases)

        if name is None:
            name = self.__class__._CreateDefaultName(phrases)
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None

        super(OrPhrase, self).__init__(name)

        self.Phrases                        = phrases
        self.SortResults                    = sort_results
        self.AmbiguitiesResolvedByOrder     = False if ambiguities_resolved_by_order is None else ambiguities_resolved_by_order
        self._name_is_default               = name_is_default

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

        best_result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(
            lambda:
                observer.EndPhrase(unique_id, self, best_result is not None and best_result.Success)
        ):
            original_normalized_iter = normalized_iter.Clone()

            results: List[Phrase.LexResult] = []

            # ----------------------------------------------------------------------
            async def ExecuteAsync(phrase_index, phrase):
                return await phrase.LexAsync(
                    unique_id + ("{} [{}]".format(self.Name, phrase_index), ),
                    normalized_iter.Clone(),
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

            # ----------------------------------------------------------------------

            if not single_threaded and len(self.Phrases) == 1:
                single_threaded = True

            if single_threaded:
                for phrase_index, phrase in enumerate(self.Phrases):
                    result = await ExecuteAsync(phrase_index, phrase)
                    if result is None:
                        return None

                    results.append(result)

                    if not self.SortResults and result.Success:
                        break

            else:
                gathered_results = await observer.Enqueue(
                    [
                        (ExecuteAsync, [phrase_index, phrase])
                        for phrase_index, phrase in enumerate(self.Phrases)
                    ],  # type: ignore
                )

                results = []

                for result in gathered_results:
                    if result is None:
                        return None
                    elif isinstance(result, Exception):
                        raise result

                    results.append(result)

            assert results

            best_index: Optional[int] = None

            if self.SortResults:
                # Stable sort according to:
                #    - Longest matched content
                #    - Success
                #    - Index

                sort_data = [
                    (
                        result.IterEnd.Offset,
                        1 if result.Success else 0,
                        # Ensure that phrases that appear earlier in the list are considered as
                        # better when all else is equal.
                        -index,
                    )
                    for index, result in enumerate(results)
                ]

                sort_data.sort()

                best_index = -sort_data[-1][-1]

                if (
                    not self.AmbiguitiesResolvedByOrder
                    and sort_data[-1][-1] == 1
                    and len(sort_data) > 1
                    and sort_data[-1][:-1] == sort_data[-2][:-1]
                ):
                    best_result = results[best_index]
                    assert best_result.Data is not None

                    # It's not ambiguous if all of the match content will ultimately be ignored
                    if not (
                        (
                            isinstance(best_result.Data.Data, Phrase.TokenLexResultData)
                            and best_result.Data.Data.IsIgnored
                        )
                        or (
                            isinstance(best_result.Data.Data, Phrase.MultipleLexResultData)
                            and all(
                                isinstance(data, Phrase.TokenLexResultData) and data.IsIgnored
                                for data in best_result.Data.Data.DataItems
                            )
                        )
                    ):
                        # Find any additional ambiguities
                        index = -2

                        for index in range(index - 1, -len(sort_data) - 1, -1):
                            if sort_data[index][:-1] != sort_data[-1][:-1]:
                                break

                        assert False, textwrap.dedent(
                            """\
                            Assertions here indicate a grammar that requires context to lex correctly; please modify
                            the grammar so that context is no longer required.

                            {} ambiguities detected.



                            {}
                            """,
                        ).format(
                            -index,
                            "\n\n\n".join([str(results[-sort_data[index][-1]]) for index in range(-1, index - 1, -1)]),
                        )

            else:
                for index, result in enumerate(results):
                    if result.Success:
                        best_index = index
                        break

                if best_index is None:
                    best_index = 0

            assert best_index is not None
            best_result = results[best_index]

            if best_result.Success:
                # pylint: disable=too-many-function-args
                data = Phrase.StandardLexResultData(self, best_result.Data, unique_id)

                if not await observer.OnInternalPhraseAsync(data, original_normalized_iter, best_result.IterEnd):
                    return None

                return Phrase.LexResult(True, original_normalized_iter, best_result.IterEnd, data)

            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                original_normalized_iter,
                best_result.IterEnd,
                Phrase.StandardLexResultData(
                    self,
                    Phrase.MultipleLexResultData([result.Data for result in results], True),
                    unique_id,
                ),
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        replaced_phrase = False

        for phrase_index, phrase in enumerate(self.Phrases):
            if isinstance(phrase, RecursivePlaceholderPhrase):
                self.Phrases[phrase_index] = new_phrase
                replaced_phrase = True
            else:
                replaced_phrase = phrase.PopulateRecursive(self, new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.Name = self.__class__._CreateDefaultName(self.Phrases)

        return replaced_phrase

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrases: List[Phrase],
    ) -> str:
        return "({})".format(" | ".join(phrase.Name for phrase in phrases))
