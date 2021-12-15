# ----------------------------------------------------------------------
# |
# |  RepeatPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 22:40:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RepeatPhrase object"""

import os

from typing import List, Optional, Tuple

from dataclasses import dataclass

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
        assert min_matches >= 0, min_matches
        assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

        if name is None:
            name = self.__class__._CreateDefaultName(phrase, min_matches, max_matches)
            name_is_default = True
        else:
            name_is_default = False

        assert name is not None

        super(RepeatPhrase, self).__init__(name)

        self.Phrase                         = phrase
        self.MinMatches                     = min_matches
        self.MaxMatches                     = max_matches
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

        success = False

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, success)):
            original_normalized_iter = normalized_iter.Clone()

            results: List[Optional[Phrase.LexResultData]] = []
            error_result: Optional[Phrase.LexResult] = None

            while not normalized_iter.AtEnd():
                result = await self.Phrase.LexAsync(
                    unique_id + ("{} [{}]".format(self.Name, len(results)), ),
                    normalized_iter.Clone(),
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )

                if result is None:
                    return None

                if not result.Success:
                    error_result = result
                    break

                results.append(result.Data)
                normalized_iter = result.IterEnd.Clone()

                if self.MaxMatches is not None and len(results) == self.MaxMatches:
                    break

            if len(results) >= self.MinMatches:
                success = True
                assert self.MaxMatches is None or len(results) <= self.MaxMatches

                # pylint: disable=too-many-function-args
                data = self.__class__.StandardLexResultData(
                    self,
                    Phrase.MultipleLexResultData(results, True),
                    unique_id,
                    error_result.Data if error_result is not None else None,
                )

                if not observer.OnInternalPhrase(
                    data,
                    original_normalized_iter,
                    normalized_iter,
                ):
                    return None

                return Phrase.LexResult(True, Phrase.NormalizedIteratorRange(original_normalized_iter, normalized_iter), data)

            # Gather the failure information
            if error_result is not None:
                results.append(error_result.Data)
                normalized_iter = error_result.IterEnd

            # pylint: disable=too-many-function-args
            return Phrase.LexResult(
                False,
                Phrase.NormalizedIteratorRange(original_normalized_iter, normalized_iter),
                Phrase.StandardLexResultData(
                    self,
                    Phrase.MultipleLexResultData(results, True),
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

        if isinstance(self.Phrase, RecursivePlaceholderPhrase):
            self.Phrase = new_phrase
            replaced_phrase = True
        else:
            replaced_phrase = self.Phrase.PopulateRecursive(self, new_phrase) or replaced_phrase

        if replaced_phrase and self._name_is_default:
            self.Name = self.__class__._CreateDefaultName(self.Phrase, self.MinMatches, self.MaxMatches)

        return replaced_phrase

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        phrase: Phrase,
        min_matches: int,
        max_matches: Optional[int],
    ) -> str:
        return "{{{}, {}, {}}}".format(phrase.Name, min_matches, max_matches)
