# ----------------------------------------------------------------------
# |
# |  Phrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 17:11:28
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

from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    TextIO,
    Tuple,
    Union,
)

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

if True:
    import sys
    sys.path.insert(0, os.path.normpath(os.path.join(_script_dir, "..", "..", "GeneratedCode")))
    from Lexer_TheLanguage.Components_TheLanguage.Phrase_TheLanguage import *
    sys.path.pop(0)

else:
    with InitRelativeImports():
        from .NormalizedIterator import NormalizedIterator
        from .ThreadPool import EnqueueAsyncItemType
        from .Token import Token as TokenClass


    # ----------------------------------------------------------------------
    class DynamicPhrasesType(Enum):
        Attributes                              = auto()
        Expressions                             = auto()
        Names                                   = auto()
        Statements                              = auto()
        TemplateDecoratorExpressions            = auto()
        TemplateDecoratorTypes                  = auto()
        Types                                   = auto()


    # ----------------------------------------------------------------------
    class Phrase(Interface.Interface, YamlRepr.ObjectReprImplBase):
        """Abstract base class for all phrases, where a phrase is a collection of tokens to be matched"""

        # ----------------------------------------------------------------------
        # |
        # |  Public Types
        # |
        # ----------------------------------------------------------------------
        class NormalizedIteratorRange(object):
            def __init__(self, begin, end):
                self.begin = begin
                self.end = end

                self._Init_()

            def __eq__(self, other):
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other) == 0

            def __ne__(self, other):
                if not isinstance(other, self.__class__): return True
                return self.__class__.__Compare__(self, other) != 0

            def __lt__(self, other):
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other) < 0

            def __le__(self, other):
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other) <= 0

            def __gt__(self, other):
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other) > 0

            def __ge__(self, other):
                if not isinstance(other, self.__class__): return False
                return self.__class__.__Compare__(self, other) >= 0

            @classmethod
            def __Compare__(cls, a, b):
                if a.begin is None and b.begin is None: pass
                elif a.begin is None: return -1
                elif b.begin is None: return 1
                elif a.begin < b.begin: return -1
                elif a.begin > b.begin: return 1

                if a.end is None and b.end is None: pass
                elif a.end is None: return -1
                elif b.end is None: return 1
                elif a.end < b.end: return -1
                elif a.end > b.end: return 1

                return 0

            # Return Type: None
            def _Init_(self):
                assert self.begin.Offset <= self.end.Offset

        @dataclass(frozen=True, repr=False)
        class LexResult(YamlRepr.ObjectReprImplBase):
            """Result returned by calls to Lex"""

            Success: bool
            iter: "NormalizedIteratorRange"
            Data: Optional["Phrase.StandardLexResultData"]

            @property
            def IterBegin(self): return self.iter.begin
            @property
            def IterEnd(self): return self.iter.end

            # ----------------------------------------------------------------------
            def __post_init__(self):
                assert self.IterBegin.Offset <= self.IterEnd.Offset, self

                self.UpdatePerformanceData()

            # ----------------------------------------------------------------------
            # Set this value to True to enable basic performance data collection.
            # ----------------------------------------------------------------------
            if False:
                _perf_data = [0]
                _perf_data_lock = threading.Lock()

                # ----------------------------------------------------------------------
                @classmethod
                def UpdatePerformanceData(cls):
                    with cls._perf_data_lock:
                        cls._perf_data[0] += 1

                # ----------------------------------------------------------------------
                @classmethod
                def DisplayPerformanceData(
                    cls,
                    output_stream: TextIO,
                ):
                    with cls._perf_data_lock:
                        output_stream.write("\n\nPhrase.PhraseResult Creation Count: {}\n\n".format(cls._perf_data[0]))

                # ----------------------------------------------------------------------

            else:
                # ----------------------------------------------------------------------
                @staticmethod
                def UpdatePerformanceData(*args, **kwargs):
                    pass

                # ----------------------------------------------------------------------
                @staticmethod
                def DisplayPerformanceData(*args, **kwargs):
                    pass

                # ----------------------------------------------------------------------

        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class LexResultData(YamlRepr.ObjectReprImplBase):
            """Abstract base class for data that is associated with a LexResult"""

            # ----------------------------------------------------------------------
            def __post_init__(
                self,
                **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
            ):
                YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class PhraseLexResultData(LexResultData):
            Phrase: "Phrase"  # type: ignore
            Data: Optional["Phrase.LexResultData"]
            UniqueId: Optional[Tuple[str, ...]]
            PotentialErrorContext: Optional["Phrase.LexResultData"]             = field(default=None)

            # ----------------------------------------------------------------------
            def __post_init__(self):
                super(Phrase.PhraseLexResultData, self).__post_init__(
                    Phrase=lambda phrase: phrase.Name,
                    UniqueId=None,
                    PotentialErrorContext=None,
                )

                assert (
                    (self.Data is not None and self.UniqueId is not None)
                    or (self.Data is None and self.UniqueId is None)
                )

        StandardLexResultData = PhraseLexResultData

        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class PhraseContainerLexResultData(LexResultData):
            DataItems: List[Optional["Phrase.LexResultData"]]
            IsComplete: bool

        MultipleLexResultData = PhraseContainerLexResultData

        # ----------------------------------------------------------------------
        @dataclass(frozen=True, repr=False)
        class TokenLexResultData(LexResultData):
            """Result from parsing a token"""

            Token: TokenClass

            Whitespace: Optional[Tuple[int, int]]
            Value: TokenClass.MatchResult
            iter: "NormalizedIteratorRange"
            is_ignored: bool

            @property
            def IterBegin(self): return self.iter.begin
            @property
            def IterEnd(self): return self.iter.end
            @property
            def IsIgnored(self): return self.is_ignored

            # ----------------------------------------------------------------------
            def __post_init__(self):
                super(Phrase.TokenLexResultData, self).__post_init__(
                    Token=lambda token: token.Name,
                )

        # ----------------------------------------------------------------------
        class Observer(Interface.Interface):
            """Observes events generated by calls to `Lex`"""

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
            ) -> Tuple[List["Phrase"], Optional[str]]:
                """Returns a list of dynamic phrases and an optional name to refer to them by"""
                raise Exception("Abstract method")  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.abstractmethod
            def StartPhrase(
                unique_id: Tuple[str, ...],
                phrase: "Phrase",
            ) -> None:
                """Invoked when processing begins on a phrase"""
                raise Exception("Abstract method")  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.abstractmethod
            def EndPhrase(
                unique_id: Tuple[str, ...],
                phrase: "Phrase",
                was_successful: bool,
            ) -> None:
                """Invoked when processing has completed on a phrase"""
                raise Exception("Abstract method")  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.abstractmethod
            def OnPushScope(
                data: "Phrase.StandardLexResultData",
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> None:
                raise Exception("Abstract method")  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.abstractmethod
            def OnPopScope(
                data: "Phrase.StandardLexResultData",
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> None:
                raise Exception("Abstract method")  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.abstractmethod
            def OnInternalPhrase(
                data: "Phrase.StandardLexResultData",
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> bool:                          # True to continue, False to terminate
                """Invoked when an internal phrase is successfully matched"""
                raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        # Bring these types into the scope of derived classes
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

            YamlRepr.ObjectReprImplBase.__init__(
                self,
                Parent=None,
                **custom_display_funcs,
            )

            self.Name                           = name
            self.Parent                         = None

            self._is_populated                  = False

        # ----------------------------------------------------------------------
        def PopulateRecursive(
            self,
            parent: Optional["Phrase"],
            new_phrase: "Phrase",
        ) -> bool:                              # True if changes were made based on population, False if no changes were made
            if self.Parent is None:
                self.Parent = parent
            else:
                assert self.Parent == parent, (
                    "A Phrase should not be the child of multiple parents; consider constructing the Phrase with 'PhraseItem' in '../Phrases/DLS.py'.",
                    self.Parent.Name,
                    parent.Name if parent is not None else None,
                    self.Name,
                )

            if self._is_populated:
                return False

            self._is_populated = True
            return self._PopulateRecursiveImpl(new_phrase)

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Lex(
            unique_id: Tuple[str, ...],
            normalized_iter: NormalizedIterator,
            observer: Observer,
            ignore_whitespace=False,
        ) -> Union[
            "Phrase.LexResult",                 # Result may or may not be successful
            None,                               # Terminate processing
        ]:
            raise Exception("Abstract method")

        # ----------------------------------------------------------------------
        # |
        # |  Private Methods
        # |
        # ----------------------------------------------------------------------
        @Interface.abstractmethod
        def _PopulateRecursiveImpl(
            self,
            new_phrase: "Phrase",
        ) -> bool:                              # True if changes were made based on population, False if no changes were made
            """Populates all instances of types that should be replaced (in the support of recursive phrase)."""
            raise Exception("Abstract method")  # pragma: no cover
