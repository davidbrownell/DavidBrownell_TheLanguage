# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-10 08:01:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement and DynamicStatements items"""

import os

from concurrent.futures import Future
from enum import auto, Enum
from typing import cast, Callable, List, Optional, Tuple, Union

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
    from .Token import Token


# ----------------------------------------------------------------------
class DynamicStatements(Enum):
    """\
    Value that can be used in statements as a placeholder that will be populated dynamically at runtime with statements of the corresponding type.

    Example:
        [
            some_keyword_token,
            newline_token,
            indent_token,
            DynamicStatements.Statements,
            dedent_token,
        ]
    """

    Statements                              = auto()    # Statements that do not generate a result
    Expressions                             = auto()    # Statements that generate a result


# ----------------------------------------------------------------------
class Statement(Interface.Interface):
    """Abstract base class for a type of statement"""

    # ----------------------------------------------------------------------
    ParseResultItemType                     = Union[
        "Statement.TokenParseResultItem",
        "Statement.StatementParseResultItem",
    ]

    ParseResultItemsType                    = List[ParseResultItemType]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TokenParseResultItem(object):
        Token: Token

        Whitespace: Optional[Tuple[int, int]]           # Whitespace immediately before the token
        Value: Token.MatchType                          # Result of the call to Token.Match
        Iter: NormalizedIterator                        # NormalizedIterator after the token has been consumed
        IsIgnored: bool                                 # True if the result is whitespace while whitespace is being ignored

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class StatementParseResultItem(object):
        Statement: Union["Statement", DynamicStatements]
        Results: "Statement.ParseResultItemsType"

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParseResult(object):
        Success: bool
        Results: "Statement.ParseResultItemsType"
        Iter: NormalizedIterator

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to Parse"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Enqueue(
            funcs: List[Callable[[], None]],
        ) -> List[Future]:
            """Enqueues the funcs for execution"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def GetDynamicStatements(
            value: DynamicStatements,
        ) -> List["Statement"]:
            """Returns all currently available dynamic statements based on the current scope"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnIndent():
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnDedent():
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnInternalStatement(
            result: "Statement.StatementParseResultItem",
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal statement is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def Name(self):
        """Returns the name of the derived Statement object"""
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Parse(
        normalized_iter: NormalizedIterator,
        observer: Observer,
    ) -> Optional["Statement.ParseResult"]:
        """Parses the provided content"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @classmethod
    def ParseMultiple(
        cls,
        statements: List["Statement"],
        normalized_iter: NormalizedIterator,
        observer: Observer,
    ) -> Optional["Statement.ParseResult"]:
        """Simultaneously applies multiple statements at the provided location"""

        if len(statements) == 1:
            result = statements[0].Parse(normalized_iter.Clone(), observer)
            if result is None:
                return None

            return Statement.ParseResult(
                result.Success,
                [
                    Statement.StatementParseResultItem(
                        statements[0],
                        result.Results,
                    ),
                ],
                result.Iter,
            )

        futures = observer.Enqueue(
            [
                lambda statement=statement: statement.Parse(normalized_iter.Clone(), observer)
                for statement in statements
            ],
        )

        results = []

        for future in futures:
            result = future.result()
            if result is None:
                return None

            results.append(result)

        # Stable sort according to the criteria:
        #   - Success
        #   - Longest matched content

        sort_data = [
            (
                index,
                1 if result.Success else 0,
                result.Iter.Offset,
            )
            for index, result in enumerate(results)
        ]

        sort_data.sort(
            key=lambda value: value[1:],
            reverse=True,
        )

        result = results[sort_data[0][0]]

        if result.Success:
            return Statement.ParseResult(
                True,
                [
                    Statement.StatementParseResultItem(
                        statements[sort_data[0][0]],
                        result.Results,
                    ),
                ],
                result.Iter,
            )

        return_results: "Statement.ParseResultItemsType" = []
        max_iter: Optional[NormalizedIterator] = None

        for statement, result in zip(statements, results):
            return_results.append(Statement.StatementParseResultItem(statement, result.Results))

            if max_iter is None or result.Iter.Offset > max_iter.Offset:
                max_iter = result.Iter

        return Statement.ParseResult(False, return_results, cast(NormalizedIterator, max_iter))
