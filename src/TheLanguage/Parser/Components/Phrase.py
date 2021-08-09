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

from typing import cast, Any, Callable, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .Token import Token as TokenClass


# ----------------------------------------------------------------------
class Phrase(Interface.Interface, CommonEnvironment.ObjectReprImplBase):
    """Abstract base class for all phrases, where a phrase is a collection of tokens"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class ParseResult(CommonEnvironment.ObjectReprImplBase):
        """Result returned by calls to ParseAsync"""

        Success: bool
        Iter: NormalizedIterator
        Data: Optional["Phrase.ParseResultData"]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                include_class_info=False,
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class ParseResultData(CommonEnvironment.ObjectReprImplBase):
        """Abstract base class for data associated with a ParseResult"""

        # ----------------------------------------------------------------------
        def __post_init__(
            self,
            **custom_display_funcs: Callable[[Any], str],
        ):
            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                include_class_info=False,
                **custom_display_funcs,
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class StandardParseResultData(ParseResultData):
        """Single phrase and data"""

        # ----------------------------------------------------------------------
        Phrase: "Phrase"  # type: ignore
        Data: Optional["Phrase.ParseResultData"]
        UniqueId: Optional[List[str]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(Phrase.StandardParseResultData, self).__post_init__()

            assert (
                (self.Data is not None and self.UniqueId is not None)
                or (self.Data is None and self.UniqueId is None)
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class MultipleStandardParseResultData(ParseResultData):
        """A collection of ParseResultData items"""

        # ----------------------------------------------------------------------
        DataItems: List[Optional["Phrase.ParseResultData"]]
        IsComplete: bool

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class TokenParseResultData(ParseResultData):
        """Result of parsing a Token"""

        # ----------------------------------------------------------------------
        Token: TokenClass

        Whitespace: Optional[Tuple[int, int]]
        Value: TokenClass.MatchResult
        IterBefore: NormalizedIterator
        IterAfter: NormalizedIterator
        IsIgnored: bool

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(Phrase.TokenParseResultData, self).__post_init__(
                Token=lambda token: token.Name,
            )

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to ParseAsync"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def StartPhrase(
            unique_id: List[str],
            phrase_stack: List["Phrase"],
        ) -> None:
            """Called before any event is generated for a particular unique_id"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def EndPhrase(
            unique_id: List[str],
            phrase_stack: List[
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
            data_stack: List["Phrase.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnDedentAsync(
            data_stack: List["Phrase.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnInternalPhraseAsync(
            data_stack: List["Phrase.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal phrase is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    NormalizedIterator                  = NormalizedIterator

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        **custom_display_funcs: Callable[[Any], str],
    ):
        assert name

        CommonEnvironment.ObjectReprImplBase.__init__(
            self,
            include_class_info=False,
            **custom_display_funcs,
        )

        self.Name                           = name
        self._is_populated                  = False

    # ----------------------------------------------------------------------
    def PopulateRecursive(self):
        self.PopulateRecursiveImpl(self)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ParseAsync(
        unique_id: List[str],
        normalized_iter: NormalizedIterator,
        observer: Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        "Phrase.ParseResult",               # Result may or may not be successful
        None,                               # Terminate processing
    ]:
        raise Exception("Abstract method")  # pragma: no cover

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
            unique_id: List[str],
            observer: "Phrase.Observer",
            items: List[Any],
            item_decorator_func: Callable[[Any], "Phrase.ParseResultData"],
        ):
            self._phrase                    = phrase
            self._unique_id                 = unique_id
            self._observer                  = observer
            self._items                     = items
            self._item_decorator_func       = item_decorator_func

        # ----------------------------------------------------------------------
        def __getattr__(self, name):
            value = getattr(self._observer, name)

            # ----------------------------------------------------------------------
            def Impl(*args, **kwargs):
                return value(*args, **kwargs)

            # ----------------------------------------------------------------------

            return Impl

        # ----------------------------------------------------------------------
        @Interface.override
        def StartPhrase(
            self,
            unique_id: List[str],
            phrase_stack: List["Phrase"],
        ):
            return self._obserer.StartPhrase(
                unique_id,
                phrase_stack + [self._phrase],
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def EndPhrase(
            self,
            unique_id: List[str],
            phrase_info_stack: List[
                Tuple[
                    "Phrase",
                    Optional[bool],
                ]
            ],
        ):
            return self._obserer.EndPhrase(
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
            data_stack: List["Phrase.StandardParseResultData"],
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
            data_stack: List["Phrase.StandardParseResultData"],
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
            data_stack: List["Phrase.StandardParseResultData"],
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
                    List["Phrase.StandardParseResultData"],
                    NormalizedIterator,
                    NormalizedIterator,
                ],
                Any,
            ],
            data_stack: List["Phrase.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> Any:
            return await method_func(
                data_stack + [
                    Phrase.StandardParseResultData(
                        self._phrase,
                        Phrase.MultipleStandardParseResultData(
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
