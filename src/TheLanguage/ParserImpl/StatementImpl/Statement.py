# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-23 08:35:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement object"""

import asyncio
import os
import textwrap

from enum import auto, Enum
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..NormalizedIterator import NormalizedIterator
    from ..Token import Token as TokenClass


# ----------------------------------------------------------------------
class Statement(Interface.Interface):
    """Abstract base class for all statement items."""

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to Parse"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnIndentAsync(
            data: "Statement.TokenParseResultData",
        ):
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnDedentAsync(
            data: "Statement.TokenParseResultData",
        ):
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnInternalStatementAsync(
            statement: "Statement",
            data: Optional["Statement.ParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal statement is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover


    # ----------------------------------------------------------------------
    # |
    # |  Public Return Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParseResult(Interface.Interface):
        """Result returned by calls to Invoke"""

        Success: bool
        Iter: NormalizedIterator
        Data: Optional["Statement.ParseResultData"]

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.ToString()

        # ----------------------------------------------------------------------
        @Interface.extensionmethod
        def ToString(
            self,
            verbose=False,
        ) -> str:
            return textwrap.dedent(
                """\
                {success}
                {iter}
                    {data}
                """,
            ).format(
                success=self.Success,
                iter=self.Iter.Offset,
                data="<No Data>" if self.Data is None else StringHelpers.LeftJustify(
                    self.Data.ToString(
                        verbose=verbose,
                    ).rstrip(),
                    4,
                ),
            )

    # ----------------------------------------------------------------------
    class ParseResultData(Interface.Interface):
        """Abstract base class for data associated with a ParseResult."""

        # ----------------------------------------------------------------------
        def __str__(self) -> str:
            return self.ToString()

        # ----------------------------------------------------------------------
        @Interface.abstractmethod
        def ToString(
            self,
            verbose=False,
        ) -> str:
            """Displays the object as a string"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Enum() -> Generator[
            Tuple[
                Optional["Statement"],
                Optional["Statement.ParseResultData"],
            ],
            None,
            None
        ]:
            """Enumerates content"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class StandardParseResultData(ParseResultData):
        """Single statement and data"""

        Statement: "Statement"
        Data: Optional["Statement.ParseResultData"]

        # ----------------------------------------------------------------------
        @Interface.override
        def ToString(
            self,
            verbose=False,
        ) -> str:
            if verbose:
                label = "Data:\n    "
            else:
                label = ""

            return textwrap.dedent(
                """\
                {name}
                    {label}{result}
                """,
            ).format(
                name=self.Statement.Name,
                label=label,
                result=StringHelpers.LeftJustify(
                    (
                        self.Data.ToString(
                            verbose=verbose,
                        ) if self.Data else str(self.Data)
                    ).rstrip(),
                    4,
                ),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def Enum(self) -> Generator[
            Tuple[
                Optional["Statement"],
                Optional["Statement.ParseResultData"],
            ],
            None,
            None
        ]:
            yield self.Statement, self.Data

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class MultipleStandardParseResultData(ParseResultData):
        """A collection of StandardParseResultData items"""

        DataItems: List["Statement.StandardParseResultData"]

        # ----------------------------------------------------------------------
        @Interface.override
        def ToString(
            self,
            verbose=False,
        ) -> str:
            data_items = []

            for data_index, data in enumerate(self.DataItems):
                if verbose:
                    prefix = "{}) ".format(data_index) if verbose else ""
                    indent = len(prefix)
                else:
                    prefix = ""
                    indent = 0

                data_items.append(
                    "{}{}".format(
                        prefix,
                        StringHelpers.LeftJustify(
                            data.ToString(
                                verbose=verbose,
                            ).rstrip() if data else str(data),
                            indent,
                        ),
                    ),
                )

            if not data_items:
                data_items.append("<No Items>")

            data_items = "\n".join(data_items)

            if verbose:
                label = "Data:\n"
            else:
                label = ""

            return "{label}{data}\n".format(
                label=label,
                data=data_items,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def Enum(self) -> Generator[
            Tuple[
                Optional["Statement"],
                Optional["Statement.ParseResultData"],
            ],
            None,
            None
        ]:
            for item in self.DataItems:
                yield from item.Enum()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TokenParseResultData(ParseResultData):
        """Result of parsing a token"""

        Token: TokenClass

        Whitespace: Optional[Tuple[int, int]]
        Value: TokenClass.MatchType
        IterBefore: NormalizedIterator
        IterAfter: NormalizedIterator
        IsIgnored: bool

        # ----------------------------------------------------------------------
        @Interface.override
        def ToString(
            self,
            verbose=False,
        ) -> str:
            return "{name} <<{value}>> ws:{ws}{ignored} [{line_before}, {column_before} -> {line_after}, {column_after}]".format(
                name=self.Token.Name,
                value=str(self.Value),
                ws="None" if self.Whitespace is None else "({}, {})".format(self.Whitespace[0], self.Whitespace[1]),
                ignored=" !Ignored!" if self.IsIgnored else "",
                line_before=self.IterBefore.Line,
                column_before=self.IterBefore.Column,
                line_after=self.IterAfter.Line,
                column_after=self.IterAfter.Column,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def Enum(self) -> Generator[
            Tuple[
                Optional["Statement"],
                Optional["Statement.ParseResultData"],
            ],
            None,
            None
        ]:
            yield None, self

    # ----------------------------------------------------------------------
    NormalizedIterator                      = NormalizedIterator

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
    ):
        assert name

        self.Name                           = name

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def ParseAsync(
        normalized_iter: NormalizedIterator,
        observer: Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        "Statement.ParseResult",            # Result may or may not be successful
        None,                               # Terminate processing
    ]:
        """Parse the content indicated by the provide iterator"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def Parse(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(self.ParseAsync(*args, **kwargs))

    # ----------------------------------------------------------------------
    # |
    # |  Protected Types
    # |
    # ----------------------------------------------------------------------
    # BugBug: This is causing problems, as we need the events to happen in real time. However, when
    # it comes to adding dynamic statements, we need a way to differentiate paths.
    class QueueCommandObserver(Observer):
        """\
        Captures events so that they can be replayed at a later time.

        We only want to generate events for statements that are successfully parsed.
        For simple Statements, this means that we can send events immediately. However,
        this isn't the case for more complicated Statements; for example, an OrStatement
        should only generate events for a single matching Statement.

        This object can be used to capture events generated and then replay them at a
        later time.
        """

        # ----------------------------------------------------------------------
        def __init__(
            self,
            observer: "Statement.Observer",
        ):
            self._observer                                                  = observer
            self._events: List["Statement.QueueCommandObserver.EventInfo"] = []

        # ----------------------------------------------------------------------
        async def ReplayAsync(self) -> bool:
            result = True

            for event in self._events:
                if event.Type == Statement.QueueCommandObserver.EventType.Indent:
                    await self._observer.OnIndentAsync(*event.Args, **event.Kwargs)
                elif event.Type == Statement.QueueCommandObserver.EventType.Dedent:
                    await self._observer.OnDedentAsync(*event.Args, **event.Kwargs)
                elif event.Type == Statement.QueueCommandObserver.EventType.InternalStatement:
                    result = await self._observer.OnInternalStatementAsync(*event.Args, **event.Kwargs)
                    if not result:
                        break
                else:
                    assert False, event  # pragma: no cover

            self._events = []
            return result

        # ----------------------------------------------------------------------
        def __getattr__(self, name):
            """The default behavior is to forward the call to the wrapped observer"""

            # ----------------------------------------------------------------------
            def Impl(*args, **kwargs):
                return getattr(self._observer, name)(*args, **kwargs)

            # ----------------------------------------------------------------------

            return Impl

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnIndentAsync(self, *args, **kwargs):
            self._events.append(
                Statement.QueueCommandObserver.EventInfo(
                    Statement.QueueCommandObserver.EventType.Indent,
                    args,
                    kwargs,
                ),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnDedentAsync(self, *args, **kwargs):
            self._events.append(
                Statement.QueueCommandObserver.EventInfo(
                    Statement.QueueCommandObserver.EventType.Dedent,
                    args,
                    kwargs,
                ),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnInternalStatementAsync(self, *args, **kwargs):
            self._events.append(
                Statement.QueueCommandObserver.EventInfo(
                    Statement.QueueCommandObserver.EventType.InternalStatement,
                    args,
                    kwargs,
                ),
            )

            return True

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        class EventType(Enum):
            Indent                          = auto()
            Dedent                          = auto()
            InternalStatement               = auto()

        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class EventInfo(object):
            Type: "Statement.QueueCommandObserver.EventType"
            Args: Tuple[Any]
            Kwargs: Dict[str, Any]
