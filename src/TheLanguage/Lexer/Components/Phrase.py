# ----------------------------------------------------------------------
# |
# |  Phrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-08 00:31:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Phrase object"""

import os
import threading

from enum import auto, Enum
from typing import Any, Awaitable, Callable, cast, Dict, Generator, List, Optional, TextIO, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .ThreadPool import EnqueueAsyncItemType
    from .Token import Token as TokenClass



# ----------------------------------------------------------------------
class DynamicPhrasesType(Enum):
    Expressions                             = auto()    # Phrase that returns a value
    Names                                   = auto()    # Phrase that can be used as a name
    Statements                              = auto()    # Phrase that doesn't return a value
    Types                                   = auto()    # Phrase that can be used as a type


# ----------------------------------------------------------------------
class Phrase(Interface.Interface, YamlRepr.ObjectReprImplBase):
    """Abstract base class for all phrases, where a phrase is a collection of tokens"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class LexResult(YamlRepr.ObjectReprImplBase):
        """Result returned by calls to LexAsync"""

        Success: bool
        IterBegin: NormalizedIterator
        IterEnd: NormalizedIterator
        Data: Optional["Phrase.StandardLexResultData"]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.IterBegin.Offset <= self.IterEnd.Offset, self

            self.UpdateStats()

        # ----------------------------------------------------------------------
        # Set this value to True to enable basic statistic collection.
        # ----------------------------------------------------------------------
        if False:
            _stats = [0]
            _stats_lock = threading.Lock()

            # ----------------------------------------------------------------------
            @classmethod
            def UpdateStats(cls):
                with cls._stats_lock:
                    cls._stats[0] += 1

            # ----------------------------------------------------------------------
            @classmethod
            def DisplayStats(
                cls,
                output_stream: TextIO,
            ):
                with cls._stats_lock:
                    output_stream.write("\n\nPhrase.PhraseResult Creation Count: {}\n\n".format(cls._stats[0]))

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
    @dataclass(frozen=True, repr=False)
    class LexResultData(YamlRepr.ObjectReprImplBase):
        """Abstract base class for data associated with a LexResult"""

        # ----------------------------------------------------------------------
        def __post_init__(
            self,
            **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
        ):
            YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

        # ----------------------------------------------------------------------
        @Interface.extensionmethod
        def Enum(self) -> Generator[
            "Phrase.LexResultData",
            None,
            None,
        ]:
            yield self

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class StandardLexResultData(LexResultData):
        """Single phrase and data"""

        # ----------------------------------------------------------------------
        Phrase: "Phrase"  # type: ignore
        Data: Optional["Phrase.LexResultData"]
        UniqueId: Optional[Tuple[str, ...]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(Phrase.StandardLexResultData, self).__post_init__(
                Phrase=lambda phrase: phrase.Name,
                UniqueId=None,  # type: ignore
            )

            assert (
                (self.Data is not None and self.UniqueId is not None)
                or (self.Data is None and self.UniqueId is None)
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MultipleStandardLexResultData(LexResultData):
        """A collection of LexResultData items"""

        # ----------------------------------------------------------------------
        DataItems: List[Optional["Phrase.LexResultData"]]
        IsComplete: bool

        # ----------------------------------------------------------------------
        @Interface.override
        def Enum(self) -> Generator[
            "Phrase.LexResultData",
            None,
            None,
        ]:
            for data_item in self.DataItems:
                if data_item is not None:
                    yield from data_item.Enum()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class TokenLexResultData(LexResultData):
        """Result of parsing a Token"""

        # ----------------------------------------------------------------------
        Token: TokenClass

        Whitespace: Optional[Tuple[int, int]]
        Value: TokenClass.MatchResult
        IterBegin: NormalizedIterator
        IterEnd: NormalizedIterator
        IsIgnored: bool

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(Phrase.TokenLexResultData, self).__post_init__(
                Token=lambda token: token.Name,
            )

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to LexAsync"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Enqueue(
            func_infos: List[EnqueueAsyncItemType],
        ) -> Awaitable[Any]:
            """Enqueues the provided functions in an executor"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def GetDynamicPhrases(
            unique_id: Tuple[str, ...],
            phrases_type: DynamicPhrasesType,
        ) -> Tuple[Optional[str], List["Phrase"]]:
            """Returns a list of dynamic phrases"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def StartPhrase(
            unique_id: Tuple[str, ...],
            phrase_stack: List["Phrase"],
        ) -> None:
            """Called before any event is generated for a particular unique_id"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def EndPhrase(
            unique_id: Tuple[str, ...],
            phrase_info_stack: List[
                Tuple[
                    "Phrase",
                    Optional[bool],         # was successful or None if the event was generated by a child phrase and this one is not yet complete
                ],
            ],
        ) -> None:
            """Called when all events have been generated for a particular unique_id"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnIndentAsync(
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnDedentAsync(
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnInternalPhraseAsync(
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal phrase is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    EnqueueAsyncItemType                    = EnqueueAsyncItemType
    NormalizedIterator                      = NormalizedIterator

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        assert name

        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

        self.Name                           = name
        self._is_populated                  = False

        self._result_cache_lock                                             = threading.Lock()
        self._result_cache: Dict[Any, "Phrase.LexResult"]                 = {}

    # ----------------------------------------------------------------------
    def PopulateRecursive(self):
        self.PopulateRecursiveImpl(self)

    # ----------------------------------------------------------------------
    async def LexAsync(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ):
        # Look for the cached value
        cache_key = normalized_iter.ToCacheKey()

        with self._result_cache_lock:
            cached_result = self._result_cache.get(cache_key, None)
            if cached_result is not None:
                return cached_result

        # Invoke functionality
        result = await self._LexAsyncImpl(
            unique_id,
            normalized_iter,
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        if result is None:
            return None

        # Cache the result; note that we don't want to cache successful results as that will prevent
        # expected events from being generated for future invocations.
        #
        # TODO: It might be good to revisit the statement above so that we can send events for cached
        #       values.
        if not result.Success:
            with self._result_cache_lock:
                self._result_cache[cache_key] = result

        return result

    # ----------------------------------------------------------------------
    # |
    # |  Protected Types
    # |
    # ----------------------------------------------------------------------
    class ObserverDecorator(Observer):
        """\
        Common implementation for a Phrase that contains children; events will be modified
        to include information about the current Phrase in addition to the child phrase(s).
        """

        # ----------------------------------------------------------------------
        def __init__(
            self,
            phrase: "Phrase",
            unique_id: Tuple[str, ...],
            observer: "Phrase.Observer",
            items: List[Any],
            item_decorator_func: Callable[[Any], "Phrase.LexResultData"],
            post_filter_dynamic_phrases_func: Optional[
                Callable[
                    [
                        Tuple[str, ...],    # unique_id
                        Optional[str],      # Unfiltered phrases name
                        List["Phrase"],     # Unfiltered dynamic phrases
                    ],
                    Tuple[Optional[str], List["Phrase"]]                    # Filtered dynamic phrases
                ]
            ]=None,
        ):
            self._phrase                                = phrase
            self._unique_id                             = unique_id
            self._observer                              = observer
            self._items                                 = items
            self._item_decorator_func                   = item_decorator_func
            self._post_filter_dynamic_phrases_func      = post_filter_dynamic_phrases_func

        # ----------------------------------------------------------------------
        @Interface.override
        def Enqueue(
            self,
            func_infos: List[EnqueueAsyncItemType],
        ) -> Awaitable[Any]:
            return self._observer.Enqueue(func_infos)

        # ----------------------------------------------------------------------
        @Interface.override
        def GetDynamicPhrases(
            self,
            unique_id: Tuple[str, ...],
            phrases_type: DynamicPhrasesType,
        ) -> Tuple[Optional[str], List["Phrase"]]:
            name, phrases = self._observer.GetDynamicPhrases(unique_id, phrases_type)

            if self._post_filter_dynamic_phrases_func:
                name, phrases = self._post_filter_dynamic_phrases_func(unique_id, name, phrases)

            return name, phrases

        # ----------------------------------------------------------------------
        @Interface.override
        def StartPhrase(
            self,
            unique_id: Tuple[str, ...],
            phrase_stack: List["Phrase"],
        ):
            return self._observer.StartPhrase(
                unique_id,
                phrase_stack + [self._phrase],
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def EndPhrase(
            self,
            unique_id: Tuple[str, ...],
            phrase_info_stack: List[
                Tuple[
                    "Phrase",
                    Optional[bool],
                ]
            ],
        ):
            return self._observer.EndPhrase(
                unique_id,
                phrase_info_stack + cast(
                    List[Tuple["Phrase", Optional[bool]]],
                    [(self._phrase, None)],
                ),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnIndentAsync(
            self,
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ):
            return await self._OnImplAsync(
                self._observer.OnIndentAsync,
                data_stack,
                iter_before,
                iter_after,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnDedentAsync(
            self,
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ):
            return await self._OnImplAsync(
                self._observer.OnDedentAsync,
                data_stack,
                iter_before,
                iter_after,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnInternalPhraseAsync(
            self,
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ):
            return await self._OnImplAsync(
                self._observer.OnInternalPhraseAsync,
                data_stack,
                iter_before,
                iter_after,
            )

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        async def _OnImplAsync(
            self,
            method_func: Callable[
                [
                    List["Phrase.StandardLexResultData"],
                    NormalizedIterator,
                    NormalizedIterator,
                ],
                Any,
            ],
            data_stack: List["Phrase.StandardLexResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> Any:
            return await method_func(
                data_stack + [
                    # pylint: disable=too-many-function-args
                    Phrase.StandardLexResultData(
                        self._phrase,
                        # pylint: disable=too-many-function-args
                        Phrase.MultipleStandardLexResultData(
                            [
                                None if item is None else self._item_decorator_func(item)
                                for item in self._items
                            ],
                            False,
                        ),
                        self._unique_id,
                    ),
                ],
                iter_before,
                iter_after,
            )

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def PopulateRecursiveImpl(
        self,
        new_phrase: "Phrase",
    ) -> bool:
        if self._is_populated:
            return False

        result = self._PopulateRecursiveImpl(new_phrase)
        self._is_populated = True

        return result

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.abstractmethod
    def _PopulateRecursiveImpl(
        self,
        new_phrase: "Phrase",
    ) -> bool:
        """\
        Populates all instances of types that should be replaced (in the support
        of recursive phrases).
        """
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def _LexAsyncImpl(
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        "Phrase.LexResult",               # Result may or may not be successful
        None,                               # Terminate processing
    ]:
        raise Exception("Abstract method")  # pragma: no cover