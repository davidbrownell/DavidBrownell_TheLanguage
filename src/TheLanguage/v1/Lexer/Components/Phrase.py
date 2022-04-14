# ----------------------------------------------------------------------
# |
# |  Phrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-02 16:03:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types used when defining phrases"""

import os
import sys
import textwrap
import threading

from enum import auto, Enum
from typing import Any, Callable, List, Optional, TextIO, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import DataclassDecorators
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .ThreadPool import EnqueueFuncInfoType, EnqueueReturnType
    from .Tokens import Token


# ----------------------------------------------------------------------
class DynamicPhrasesType(Enum):
    Attributes                              = auto()
    Expressions                             = auto()
    Names                                   = auto()
    Statements                              = auto()
    TemplateExpressions                     = auto()
    TemplateTypes                           = auto()
    Types                                   = auto()


# ----------------------------------------------------------------------
class Phrase(Interface.Interface, ObjectReprImplBase):
    """Abstract base class for all phrases, where a phrase is a collection of tokens to be matched"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @DataclassDecorators.ComparisonOperators
    @dataclass(frozen=True, repr=False)
    class NormalizedIteratorRange(ObjectReprImplBase):
        begin: NormalizedIterator
        end: NormalizedIterator

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.begin.offset <= self.end.offset

            ObjectReprImplBase.__init__(self)

        # ----------------------------------------------------------------------
        @staticmethod
        def Compare(a, b) -> int:
            if a.begin.offset < b.begin.offset:
                return -1
            elif a.begin.offset > b.begin.offset:
                return 1

            if a.end.offset < b.end.offset:
                return -1
            elif a.end.offset > b.end.offset:
                return 1

            return 0

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class LexResult(ObjectReprImplBase):
        """Result returned by calls to Lex"""

        success: bool
        iter_range: "Phrase.NormalizedIteratorRange"
        data: "Phrase.LexResultData"

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.iter_range is not None
            assert self.data is not None

            ObjectReprImplBase.__init__(self)

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
                    output_stream.write(
                        textwrap.dedent(
                            """\


                            Phrase.LexResult Creation Count: {}

                            """,
                        ).format(cls._perf_data[0]),
                    )

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
    class LexResultData(ObjectReprImplBase):
        # ----------------------------------------------------------------------
        # |  Public Types
        DataItemType                        = Union[
            None,
            "Phrase.LexResultData",
            "Phrase.TokenLexResultData",
            List["Phrase.LexResultData.DataItemType"],
        ]

        # ----------------------------------------------------------------------
        # |  Public Data
        phrase: "Phrase"
        unique_id: Tuple[str, ...]
        data: DataItemType
        potential_error_context: Optional["Phrase.LexResultData"]

        # ----------------------------------------------------------------------
        # |  Public Methods
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.potential_error_context is None or self.data is not None

            ObjectReprImplBase.__init__(
                self,
                phrase=lambda value: value.name,
                unique_id=None,
                potential_error_context=None,
            )

        # ----------------------------------------------------------------------
        def PrettyPrint(
            self,
            output_stream: TextIO=sys.stdout,
        ) -> None:
            self.phrase.PrettyPrint("", self.data, output_stream)

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class TokenLexResultData(ObjectReprImplBase):
        token: Token
        value: Token.MatchResult
        iter_range: "Phrase.NormalizedIteratorRange"
        is_ignored: bool

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            ObjectReprImplBase.__init__(
                self,
                token=lambda value: value.name,
            )

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to `Lex`"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Enqueue(
            func_infos: List[EnqueueFuncInfoType],
        ) -> EnqueueReturnType:
            """Enqueues the provided functions in an executor"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def GetDynamicPhrases(
            unique_id: Tuple[str, ...],
            phrases_type: DynamicPhrasesType,
        ) -> Tuple[List["Phrase"], Optional[str]]:
            """Returns a list of dyanmic phrases and a name to refer to them by"""
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
            iter_range: "Phrase.NormalizedIteratorRange",
            data: "Phrase.LexResultData",
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnPopScope(
            iter_range: "Phrase.NormalizedIteratorRange",
            data: "Phrase.LexResultData",
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnInternalPhrase(
            iter_range: "Phrase.NormalizedIteratorRange",
            data: "Phrase.LexResultData",
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal phrase is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

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

        ObjectReprImplBase.__init__(
            self,
            parent=None,
            **custom_display_funcs,
        )

        self.name                           = name
        self.parent                         = None

        self._is_populated                  = False

    # ----------------------------------------------------------------------
    def PopulateRecursive(
        self,
        parent: Optional["Phrase"],
        new_phrase: "Phrase",
    ) -> bool:                              # True if changes were made based on population, False if no changes were made
        if self.parent is None:
            self.parent = parent
        else:
            assert self.parent != parent, (
                "A Phrase should not be the child of multiple parents; consider constructing the Phrase with `PhraseItem` in `../Phrases/DSL.py`.",
                self.parent.name,
                parent.name if parent is not None else None,
                self.name,
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
        *,
        single_threaded=False,
        ignore_whitespace=False,
    ) -> Union[
        None,                               # Terminate processing
        "Phrase.LexResult",                 # Result may or may not be successful
    ]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def PrettyPrint(
        indentation: str,
        data: "Phrase.LexResultData.DataItemType",
        output_stream: TextIO,
    ) -> None:
        """Pretty prints output"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _PopulateRecursiveImpl(
        new_phrase: "Phrase",
    ) -> bool:                              # True if changes were made based on population, False if no changes were made
        """Populates all instances of types that should be replaced (in the support of recursive phrase)."""
        raise Exception("Abstract method")  # pragma: no cover
