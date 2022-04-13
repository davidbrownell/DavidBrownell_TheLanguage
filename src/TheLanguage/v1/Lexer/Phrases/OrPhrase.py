# ----------------------------------------------------------------------
# |
# |  OrPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 11:45:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the OrPhrase object"""

import os
import textwrap

from typing import List, Optional, TextIO, Tuple

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

    from ..Components.Phrase import NormalizedIterator, Phrase


# ----------------------------------------------------------------------
class OrPhrase(Phrase):
    """Attempt to match one of the provided phrases"""

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
        assert all(phrases)

        if name is None:
            name = self.__class__._CreateDefaultName(phrases)  # type: ignore  # pylint: disable=protected-access
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None

        super(OrPhrase, self).__init__(name)

        self.phrases                        = phrases
        self.sort_results                   = sort_results
        self.ambiguities_resolved_by_order  = ambiguities_resolved_by_order
        self._name_is_default               = name_is_default

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

        best_result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, best_result is not None and best_result.success)):
            results: List[Phrase.LexResult] = []

            # ----------------------------------------------------------------------
            def Execute(phrase_index, phrase) -> Phrase.LexResult:
                return phrase.Lex(
                    unique_id + ("{} ({})".format(self.name, phrase_index), ),
                    normalized_iter.Clone(),
                    observer,
                    single_threaded=single_threaded,
                    ignore_whitespace=ignore_whitespace,
                )

            # ----------------------------------------------------------------------

            if single_threaded or len(self.phrases) == 1:
                for phrase_index, phrase in enumerate(self.phrases):
                    result = Execute(phrase_index, phrase)
                    if result is None:
                        return None

                    results.append(result)

                    if not self.sort_results and result.success:
                        break

            else:
                futures = observer.Enqueue(
                    [
                        (Execute, [phrase_index, phrase])
                        for phrase_index, phrase in enumerate(self.phrases)
                    ],
                )

                for future in futures:
                    result = future.result()

                    if result is None:
                        return None
                    elif isinstance(result, Exception):
                        raise result

                    results.append(result)

            assert results

            # Find the best result
            best_index: Optional[int] = None

            if self.sort_results:
                # Stable sort according to:
                #       - Longest matched content
                #       - Success
                #       - Index

                sort_data = [
                    (
                        result.iter_range.end.offset,
                        1 if result.success else 0,
                        # Ensure that phrases that appear earlier in the list are considered as
                        # better when all else is equal.
                        -index,
                    )
                    for index, result in enumerate(results)
                ]

                sort_data.sort()

                best_index = -sort_data[-1][-1]
                assert best_index >= 0
                assert best_index < len(results)

                if (
                    not self.ambiguities_resolved_by_order
                    and sort_data[-1][-1] == 1
                    and len(sort_data) > 1
                    and sort_data[-1][:-1] == sort_data[-2][:-1]
                ):
                    best_result = results[best_index]
                    assert best_result.data is not None

                    # It's not ambiguous if all of the matched content will ultimately be ignored
                    if not (
                        (
                            isinstance(best_result.data.data, Phrase.TokenLexResultData)
                            and best_result.data.data.is_ignored
                        )
                        or (
                            isinstance(best_result.data.data, list)
                            and all(
                                isinstance(data, Phrase.TokenLexResultData) and data.is_ignored
                                for data in best_result.data.data
                            )
                        )
                    ):
                        # Find any additional ambiguous data
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
                            "\n\n\n".join(str(results[-sort_data[index][-1]]) for index in range(-1, index - 1, -1)),
                        )  # pragma: no cover

            else:
                for index, result in enumerate(results):
                    if result.success:
                        best_index = index
                        break

                if best_index is None:
                    best_index = 0

            assert best_index is not None
            best_result = results[best_index]

            if best_result.success:
                data = Phrase.LexResultData.Create(self, unique_id, best_result.data, None)

                if not observer.OnInternalPhrase(best_result.iter_range, data):
                    return None

                return Phrase.LexResult.Create(
                    True,
                    best_result.iter_range,
                    data,
                )

            return Phrase.LexResult.Create(
                False,
                best_result.iter_range,
                Phrase.LexResultData.Create(
                    self,
                    unique_id,
                    [result.data for result in results],
                    None,
                ),
            )

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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        replaced_phrase = False

        for phrase_index, phrase in enumerate(self.phrases):
            if isinstance(phrase, RecursivePlaceholderPhrase):
                self.phrases[phrase_index] = new_phrase
                replaced_phrase = True
            else:
                replaced_phrase = phrase.PopulateRecursive(self, new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.name = self.__class__._CreateDefaultName(self.phrases)  # type: ignore  # pylint: disable=protected-access

        return replaced_phrase

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrases: List[Phrase],
    ) -> str:
        return "({})".format(" | ".join(phrase.name for phrase in phrases))
