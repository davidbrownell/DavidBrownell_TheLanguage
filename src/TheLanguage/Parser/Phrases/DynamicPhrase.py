# ----------------------------------------------------------------------
# |
# |  DynamicPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-09 11:19:22
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

from typing import Callable, List, Optional, Tuple, Union

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
    from ..Components.Phrase import Phrase


# ----------------------------------------------------------------------
class DynamicPhrase(Phrase):
    """Collects dynamic statements and parses them"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        get_dynamic_phrases_func: Callable[
            [
                List[str],                  # unique_id
                Phrase.Observer,
            ],
            Union[
                List[Phrase],               # List of Phrases
                Tuple[List[Phrase], str],   # List of Phrases and the phase name
            ]
        ],
        name: str=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrases"

        super(DynamicPhrase, self).__init__(name)

        self._get_dynamic_phrases_func      = get_dynamic_phrases_func

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
        result: Optional[Phrase.ParseResult] = None

        observer.StartPhrase(unique_id, [self])
        with CallOnExit(
            lambda: observer.EndPhrase(
                unique_id,
                [
                    (
                        self,
                        result is not None and result.Success,
                    ),
                ],
            ),
        ):
            dynamic_phrases = self._get_dynamic_phrases_func(unique_id, observer)
            if not dynamic_phrases:
                return Phrase.ParseResult(False, normalized_iter, None)

            if isinstance(dynamic_phrases, tuple):
                dyanmic_phrases, phrase_name = dynamic_phrases
            else:
                phrase_name = None

            assert isinstance(dynamic_phrases, list)

            # Use the logic in the OrPhrase constructor to create a pretty name for the phrase;
            # use that name when creating the unique_id to be used for events associated with
            # this invocation.
            or_phrase = OrPhrase(
                dynamic_phrases,
                name=phrase_name,
            )

            result = await or_phrase.ParseAsync(
                unique_id + [or_phrase.Name],
                normalized_iter,
                Phrase.ObserverDecorator(
                    self,
                    unique_id,
                    observer,
                    [result],
                    lambda result: result.Data,
                ),
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            if result is None:
                return None

            data = Phrase.StandardParseResultData(self, result.Data, unique_id)

            if (
                result.Success
                and not await observer.OnInternalPhraseAsync(
                    [data],
                    normalized_iter,
                    result.Iter,
                )
            ):
                return None

            return Phrase.ParseResult(result.Success, result.Iter, data)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    ) -> bool:
        # Nothing to do here
        return False
