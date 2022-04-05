# ----------------------------------------------------------------------
# |
# |  DynamicPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 12:49:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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

    from ..Components.Phrase import DynamicPhrasesType, NormalizedIterator, Phrase


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
            Tuple[List[Phrase], Optional[str]],
        ],
        name: Optional[str]=None,
        include_phrases: Optional[List[Union[str, Phrase]]]=None,
        exclude_phrases: Optional[List[Union[str, Phrase]]]=None,
        is_valid_data_func: Optional[Callable[[Phrase.LexResultData], bool]]=None,
    ):
        assert get_dynamic_phrases_func

        name = name or "Dynamic Phrase"

        super(DynamicPhrase, self).__init__(name)

        self.dynamic_phrases_type           = phrases_type
        self._get_dynamic_phrases_func      = get_dynamic_phrases_func
        self._display_name: Optional[str]   = None

        # ----------------------------------------------------------------------
        def CreateIncludePhraseFunc(
            include_phrases: Optional[List[Union[str, Phrase]]],
            exclude_phrases: Optional[List[Union[str, Phrase]]],
        ) -> Callable[[Phrase], bool]:
            assert (
                (not include_phrases and not exclude_phrases)
                or not exclude_phrases
                or not include_phrases
            )

            if include_phrases:
                these_include_phrases = set(
                    [
                        phrase.name if isinstance(phrase, Phrase) else phrase
                        for phrase in include_phrases
                    ],
                )

                return lambda phrase: phrase.name in these_include_phrases

            if exclude_phrases:
                these_exclude_phrases = set(
                    [
                        phrase.name if isinstance(phrase, Phrase) else phrase
                        for phrase in exclude_phrases
                    ],
                )

                return lambda phrase: phrase.name not in these_exclude_phrases

            return lambda phrase: True

        # ----------------------------------------------------------------------

        self._pre_phrase_filter_func        = CreateIncludePhraseFunc(include_phrases, exclude_phrases)
        self._is_valid_data_func            = is_valid_data_func or (lambda *args, **kwargs: True)

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
        result: Optional[Phrase.LexResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, result is not None and result.success)):
            # Get the dynamic phrases
            dynamic_phrases, dynamic_name = self._get_dynamic_phrases_func(
                unique_id,
                self.dynamic_phrases_type,
                observer,
            )

            assert isinstance(dynamic_phrases, list)

            self._display_name = dynamic_name

            # Filter the list by those that have been explicitly included on excluded
            dynamic_phrases = [
                phrase for phrase in dynamic_phrases if self._pre_phrase_filter_func(phrase)
            ]

            # TODO: Split the phrases into those that are left-recursive and those that are not
            # TODO: left_recursive_phrases: List[Phrase] = []
            standard_phrases: List[Phrase] = []

            for phrase in dynamic_phrases:
                # TODO
                standard_phrases.append(phrase)

            if False: # TODO left_recursive_phrases:
                assert False, "TODO"
            elif standard_phrases:
                result = self._LexStandard(
                    dynamic_name,
                    standard_phrases,
                    unique_id,
                    normalized_iter,
                    observer,
                    single_threaded=single_threaded,
                    ignore_whitespace=ignore_whitespace,
                )

            if result is None:
                return None

            if result.success and not observer.OnInternalPhrase(result.iter_range, result.data):
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
    def _LexStandard(
        self,
        dynamic_name: Optional[str],
        phrases: List[Phrase],
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        single_threaded: bool,
        ignore_whitespace: bool,
    ) -> Optional[Phrase.LexResult]:
        or_phrase = OrPhrase(
            phrases,
            name=dynamic_name,
        )

        result = or_phrase.Lex(
            unique_id + (or_phrase.name, ),
            normalized_iter,
            observer,
            single_threaded=single_threaded,
            ignore_whitespace=ignore_whitespace,
        )

        if result is None:
            return None

        return Phrase.LexResult.Create(
            result.success,
            result.iter_range,
            Phrase.LexResultData.Create(self, unique_id, result.data, None),
        )
