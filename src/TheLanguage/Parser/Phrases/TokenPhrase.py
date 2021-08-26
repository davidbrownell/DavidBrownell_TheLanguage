# ----------------------------------------------------------------------
# |
# |  TokenPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-08 19:00:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TokenPhrase object"""

import os

from typing import List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Phrase import Phrase

    from ..Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,                       # This is here as a convenience to other modules importing this one; please do not remove
        RegexToken,                         # This is here as a convenience to other modules importing this one; please do not remove
        Token as TokenClass,
    )


# ----------------------------------------------------------------------
class TokenPhrase(Phrase):
    """Phrase that matches against a Token"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        token: TokenClass,
        name: str=None,
    ):
        assert token

        name = name or token.Name

        super(TokenPhrase, self).__init__(
            name,
            Token=lambda token: token.Name,
        )

        self.Token                          = token

    # ----------------------------------------------------------------------
    @staticmethod
    def ExtractWhitespace(
        normalized_iter: Phrase.NormalizedIterator,
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
        unique_id: List[str],
        normalized_iter: Phrase.NormalizedIterator,
        observer: Phrase.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Phrase.ParseResult,
        None,
    ]:
        data: Optional[Phrase.StandardParseResultData] = None

        observer.StartPhrase(unique_id, [self])
        with CallOnExit(lambda: observer.EndPhrase(unique_id, [(self, data is not None)])):
            # We only want to consume whitespace if there is a match that follows; collect
            # it for now, but do not commit that collection to the input iterator.
            potential_iter = normalized_iter.Clone()
            potential_whitespace = self.ExtractWhitespace(potential_iter)
            potential_iter_begin = potential_iter.Clone()

            result = self.Token.Match(potential_iter)
            if result is None:
                # <Too many arguments> pylint: disable=E1121
                return Phrase.ParseResult(
                    False,
                    normalized_iter,
                    normalized_iter,
                    # <Too many arguments> pylint: disable=E1121
                    Phrase.StandardParseResultData(self, None, None),
                )

            # <Too many arguments> pylint: disable=E1121
            data = Phrase.StandardParseResultData(
                self,
                # <Too many arguments> pylint: disable=E1121
                Phrase.TokenParseResultData(
                    self.Token,
                    potential_whitespace,
                    result,
                    potential_iter_begin,
                    potential_iter,
                    IsIgnored=self.Token.IsAlwaysIgnored,
                ),
                unique_id,
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
            elif not await observer.OnInternalPhraseAsync(
                [data],
                potential_iter_begin,
                potential_iter,
            ):
                return None

            # <Too many arguments> pylint: disable=E1121
            return Phrase.ParseResult(True, normalized_iter.Clone(), potential_iter, data)
