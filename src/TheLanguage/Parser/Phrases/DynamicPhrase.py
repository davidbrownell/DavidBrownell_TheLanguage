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
import textwrap
import threading

from typing import cast, Callable, Dict, List, Optional, TextIO, Tuple, Union

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
    from ..Components.Phrase import DynamicPhrasesType, Phrase


# ----------------------------------------------------------------------
class DynamicPhrase(Phrase):
    """Collects dynamic statements and parses them"""

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
            Tuple[Optional[str], List[Phrase]],         # List of Phrases and the phase name
        ],
        name: str=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrases"

        super(DynamicPhrase, self).__init__(name)

        self.DynamicPhrasesType             = phrases_type
        self._get_dynamic_phrases_func      = get_dynamic_phrases_func

    # ----------------------------------------------------------------------
    # Set this value to True to enable basic statistic collection.
    # ----------------------------------------------------------------------
    if False:  # <constant value> pylint: disable=W0125
        _stats: Dict[
            Tuple[bytes, int],              # (normalized_iter.Hash, normalized_iter.Offset)
            Dict[
                Tuple[str, ...],            # unique_id
                Dict[
                    int,                    # id(Phrase)
                    int                     # count
                ],
            ]
        ] = {}

        _stats_lock = threading.Lock()

        # ----------------------------------------------------------------------
        def UpdateStats(
            self,
            unique_id: Tuple[str, ...],
            normalized_iter: Phrase.NormalizedIterator,
        ):
            with self._stats_lock:
                data = self._stats.setdefault((cast(bytes, normalized_iter.Hash), normalized_iter.Offset), {})
                data = data.setdefault(unique_id, {})

                key = id(self)

                if key not in data:
                    data[key] = 0

                data[key] += 1

        # ----------------------------------------------------------------------
        @classmethod
        def DisplayStats(
            cls,
            output_stream: TextIO,
            verbose=False,
        ):
            with cls._stats_lock:
                output_stream.write(
                    textwrap.dedent(
                        """\

                        Dynamic Phrase Info
                        ===================
                        """,
                    ),
                )

                for (_, offset), data in cls._stats.items():
                    content = "Offset {} ({})".format(offset, len(data))

                    output_stream.write(
                        "    {}{}\n".format(
                            content,
                            "\n    {}".format("-" * len(content)) if verbose else "",
                        ),
                    )

                    if verbose:
                        for unique_id in data.keys():
                            output_stream.write("        {}\n".format(unique_id))

                        output_stream.write("\n")

        # ----------------------------------------------------------------------

    else:
        # ----------------------------------------------------------------------
        @staticmethod
        def UpdateStats(*args, **kwargs):
            pass

        # ----------------------------------------------------------------------
        @staticmethod
        def DisplayStats(*args, **kwargs):
            pass

        # ----------------------------------------------------------------------

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
            phrase_name, dynamic_phrases = self._get_dynamic_phrases_func(
                unique_id,
                self.DynamicPhrasesType,
                observer,
            )
            assert isinstance(dynamic_phrases, list), dynamic_phrases

            if not dynamic_phrases:
                # <Too many arguments> pylint: disable=E1121
                return Phrase.ParseResult(False, normalized_iter, normalized_iter, None)

            self.UpdateStats(unique_id, normalized_iter)

            # Use the logic in the OrPhrase constructor to create a pretty name for the phrase;
            # use that name when creating the unique_id to be used for events associated with
            # this invocation.
            or_phrase = OrPhrase(
                dynamic_phrases,
                name=phrase_name,
            )

            result = await or_phrase.ParseAsync(
                unique_id + (or_phrase.Name, ),
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

            # <Too many arguments> pylint: disable=E1121
            data = Phrase.StandardParseResultData(self, result.Data, unique_id)

            if (
                result.Success
                and not await observer.OnInternalPhraseAsync(
                    [data],
                    normalized_iter,
                    result.IterEnd,
                )
            ):
                return None

            # <Too many arguments> pylint: disable=E1121
            return Phrase.ParseResult(result.Success, normalized_iter, result.IterEnd, data)
