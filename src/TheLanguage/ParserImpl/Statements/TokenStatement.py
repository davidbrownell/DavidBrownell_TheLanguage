# ----------------------------------------------------------------------
# |
# |  TokenStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-25 15:48:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TokenStatement object"""

import os

from typing import Any, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement

    from ..Token import (
        DedentToken,
        IndentToken,
        NewlineToken,                       # Added here as a convenience, do not remove
        RegexToken,                         # Added here as a convenience, do not remove
        Token as TokenClass,
    )


# ----------------------------------------------------------------------
class TokenStatement(Statement):
    """Statement that wraps a Token"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        token: TokenClass,
        name: str=None,
        unique_id: Optional[List[Any]]=None,
        type_id: Optional[int]=None,
    ):
        assert token

        name = name or token.Name

        super(TokenStatement, self).__init__(
            name,
            unique_id=unique_id,
            type_id=type_id,
        )

        self.Token                          = token

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[Any],
    ) -> Statement:
        return self.__class__(
            self.Token,
            unique_id=unique_id,
            type_id=self.TypeId,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def PopulateRecursive(
        self,
        new_statement: Statement,
        type_to_replace: Any,
    ):
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        data: Optional[Statement.StandardParseResultData] = None

        observer.StartStatement([self])
        with CallOnExit(lambda: observer.EndStatement([(self, data != None)])):
            # We only want to consume whitespace if there is a match that follows
            potential_iter = normalized_iter.Clone()
            potential_whitespace = self.ExtractWhitespace(potential_iter)
            potential_iter_begin = potential_iter.Clone()

            result = self.Token.Match(potential_iter)
            if result is None:
                return Statement.ParseResult(False, normalized_iter, None)

            data = Statement.StandardParseResultData(
                self,
                Statement.TokenParseResultData(
                    self.Token,
                    potential_whitespace,
                    result,
                    potential_iter_begin,
                    potential_iter,
                    IsIgnored=self.Token.IsAlwaysIgnored,
                )
            )

            if isinstance(self.Token, IndentToken):
                await observer.OnIndentAsync(
                    [data],
                    potential_iter_begin,
                    potential_iter,
                )
            elif isinstance(self.Token, DedentToken):
                await observer.OnDedentAsync(
                    [data],
                    potential_iter_begin,
                    potential_iter,
                )
            elif not await observer.OnInternalStatementAsync(
                    [data],
                    potential_iter_begin,
                    potential_iter,
                ):
                    return None

            return Statement.ParseResult(True, potential_iter, data)

    # ----------------------------------------------------------------------
    @staticmethod
    def ExtractWhitespace(
        normalized_iter: Statement.NormalizedIterator,
    ) -> Optional[Tuple[int, int]]:
        """Consumes any whitespace located at the current offset"""

        if not normalized_iter.AtEnd():
            if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart:
                if (
                    not normalized_iter.LineInfo.HasNewIndent()
                    and not normalized_iter.LineInfo.HasNewDedents()
                ):
                    normalized_iter.SkipPrefix()

            else:
                start = normalized_iter.Offset

                while (
                    normalized_iter.Offset < normalized_iter.LineInfo.OffsetEnd
                    and normalized_iter.Content[normalized_iter.Offset].isspace()
                    and normalized_iter.Content[normalized_iter.Offset] != "\n"
                ):
                    normalized_iter.Advance(1)

                if normalized_iter.Offset != start:
                    return start, normalized_iter.Offset

        return None
