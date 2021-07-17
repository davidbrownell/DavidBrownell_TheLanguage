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

import os
import textwrap

from typing import cast, Any, Callable, Generator, List, Optional, Tuple, Union

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
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParseResult(Interface.Interface):
        """Result returned by calls to ParseAsync"""

        Success: bool
        Iter: NormalizedIterator
        Data: Optional["Statement.StandardParseResultData"]

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

        Statement: "Statement"  # type: ignore
        Data: Optional["Statement.ParseResultData"]
        UniqueId: Optional[List[str]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert (
                (self.Data is not None and self.UniqueId is not None)
                or (self.Data is None and self.UniqueId is None)
            )

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
                name=self.Statement.ToString(
                    verbose=verbose,
                ),
                label=label,
                result=StringHelpers.LeftJustify(
                    (
                        self.Data.ToString(
                            verbose=verbose,
                        ) if self.Data else "<No Data>"
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
        """A collection of ParseResultData items"""

        DataItems: List[Optional["Statement.ParseResultData"]]
        IsComplete: bool

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
                            ).rstrip() if data else "<No Data>",
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
                assert item
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
    class Observer(Interface.Interface):
        """Observes events generated by calls to ParseAsync"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def StartStatement(
            unique_id: List[str],
            statement_stack: List["Statement"],
        ) -> None:
            """Called before any event is generated for a particular unique_id"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def EndStatement(
            unique_id: List[str],
            statement_info_stack: List[
                Tuple[
                    "Statement",
                    Optional[bool],         # was successful or None if the event was generated by a child statement and this one is not yet complete
                ],
            ],
        ) -> None:
            """Called when all events have been generated for a particular unique_id"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnIndentAsync(
            data_stack: List["Statement.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnDedentAsync(
            data_stack: List["Statement.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> None:
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        async def OnInternalStatementAsync(
            data_stack: List["Statement.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal statement is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

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
        self._is_populated                  = False

    # ----------------------------------------------------------------------
    def PopulateRecursive(self):
        self.PopulateRecursiveImpl(self)

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.ToString()

    # ----------------------------------------------------------------------
    def ToString(
        self,
        verbose=False,
    ) -> str:
        if verbose:
            return "{} <{}>".format(self.Name, ", ".join([str(uid) for uid in self.UniqueId]))

        return self.Name

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def ParseAsync(
        unique_id: List[str],
        normalized_iter: NormalizedIterator,
        observer: Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        "Statement.ParseResult",            # Result may or may not be successful
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
        Common implementation for a Statement that contains children; events will be modified
        to include information about the current Statement in addition to the child statement(s).
        """

        # ----------------------------------------------------------------------
        def __init__(
            self,
            statement: "Statement",
            unique_id: List[str],
            observer: "Statement.Observer",
            items: List[Any],
            item_decorator_func: Callable[[Any], "Statement.ParseResultData"],
        ):
            self._statement                 = statement
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
        def StartStatement(
            self,
            unique_id: List[str],
            statement_stack: List["Statement"],
        ):
            return self._observer.StartStatement(
                unique_id,
                statement_stack + [self._statement],
            )

        # ----------------------------------------------------------------------
        @Interface.override
        def EndStatement(
            self,
            unique_id: List[str],
            statement_info_stack: List[
                Tuple[
                    "Statement",
                    Optional[bool],
                ]
            ],
        ):
            return self._observer.EndStatement(
                unique_id,
                statement_info_stack + cast(List[Tuple["Statement", Optional[bool]]], [(self._statement, None)]),
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def OnIndentAsync(
            self,
            data_stack: List["Statement.StandardParseResultData"],
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
            data_stack: List["Statement.StandardParseResultData"],
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
        async def OnInternalStatementAsync(
            self,
            data_stack: List["Statement.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ):
            return await self._OnImplAsync(
                self._observer.OnInternalStatementAsync,
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
                    List["Statement.StandardParseResultData"],
                    NormalizedIterator,
                    NormalizedIterator,
                ],
                Any,
            ],
            data_stack: List["Statement.StandardParseResultData"],
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> Any:
            return await method_func(
                data_stack + [
                    Statement.StandardParseResultData(
                        self._statement,
                        Statement.MultipleStandardParseResultData(
                            [None if item is None else self._item_decorator_func(item) for item in self._items],
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
        new_statement: "Statement",
    ) -> bool:
        if self._is_populated:
            return False

        result = self._PopulateRecursiveImpl(new_statement)
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
        new_statement: "Statement",
    ) -> bool:
        """\
        Populates all instances of `type_to_replace` with `new_statement`. This
        allows for recursive statement definitions.
        """
        raise Exception("Abstract method")  # pragma: no cover
