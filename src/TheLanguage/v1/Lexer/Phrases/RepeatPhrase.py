# ----------------------------------------------------------------------
# |
# |  RepeatPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 13:11:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RepeatPhrase object"""

import os

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
class RepeatPhrase(Phrase):
    """Matches content that repeats the provided phrase N times"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase: Phrase,
        min_matches: int,
        max_matches: Optional[int],
        name: Optional[str]=None,
    ):
        assert phrase
        assert min_matches >= 0
        assert max_matches is None or max_matches >= min_matches

        if name is None:
            name = self.__class__._CreateDefaultName(phrase, min_matches, max_matches)  # type: ignore  # pylint: disable=protected-access
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None

        super(RepeatPhrase, self).__init__(name)

        self.phrase                         = phrase
        self.min_matches                    = min_matches
        self.max_matches                    = max_matches
        self._name_is_default                = name_is_default

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
        success = False

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, success)):
            working_iter = normalized_iter.Clone()

            results: List[Phrase.LexResultData] = []
            error_result: Optional[Phrase.LexResult] = None

            while not working_iter.AtEnd():
                result = self.phrase.Lex(
                    unique_id + ("{} [{}]".format(self.name, len(results)), ),
                    working_iter.Clone(),
                    observer,
                    single_threaded=single_threaded,
                    ignore_whitespace=ignore_whitespace,
                )

                if result is None:
                    return None

                if not result.success:
                    error_result = result
                    break

                results.append(result.data)
                working_iter = result.iter_range.end.Clone()

                if self.max_matches is not None and len(results) == self.max_matches:
                    break

            if len(results) >= self.min_matches:
                success = True
                assert self.max_matches is None or len(results) <= self.max_matches

                iter_range = Phrase.NormalizedIteratorRange.Create(normalized_iter.Clone(), working_iter)

                data = Phrase.LexResultData.Create(
                    self,
                    unique_id,
                    results,
                    error_result.data if error_result is not None else None,
                )

                if not observer.OnInternalPhrase(iter_range, data):
                    return None

                return Phrase.LexResult.Create(True, iter_range, data)

            # Gather the failure info
            if error_result is not None:
                results.append(error_result.data)
                working_iter = error_result.iter_range.end.Clone()

            return Phrase.LexResult.Create(
                False,
                Phrase.NormalizedIteratorRange.Create(normalized_iter.Clone(), working_iter),
                Phrase.LexResultData.Create(self, unique_id, results, None),
            )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PrettyPrint(
        indentation: str,
        data: Phrase.LexResultData.DataItemType,
        output_stream: TextIO,
    ) -> None:
        assert isinstance(data, list), data

        output_stream.write("{}{{{{{{\n".format(indentation))

        this_indentation = indentation + "    "

        for item in data:
            assert isinstance(item, Phrase.LexResultData), item
            item.phrase.PrettyPrint(this_indentation, item.data, output_stream)

        output_stream.write("{}}}}}}}\n".format(indentation))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        replaced_phrase = False

        if isinstance(self.phrase, RecursivePlaceholderPhrase):
            self.phrase = new_phrase
            replaced_phrase = True
        else:
            replaced_phrase = self.phrase.PopulateRecursive(self, new_phrase)

        if replaced_phrase and self._name_is_default:
            self.name = self.__class__._CreateDefaultName(self.phrase, self.min_matches, self.max_matches)  # type: ignore  # pylint: disable=protected-access

        return replaced_phrase

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrase: Phrase,
        min_matches: int,
        max_matches: Optional[int],
    ) -> str:
        return "{{{}, {}, {}}}".format(phrase.name, min_matches, max_matches)
