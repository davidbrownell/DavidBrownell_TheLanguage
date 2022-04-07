# ----------------------------------------------------------------------
# |
# |  TokenPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-02 18:44:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TokenPhrase object"""

import os

from typing import Optional, TextIO, Tuple

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Phrase import NormalizedIterator, Phrase

    from ..Components.Tokens import (       # pylint: disable=unused-import
        DedentToken,
        IndentToken,
        NewlineToken,                       # Convenience for other files
        Token,
        RegexToken,                         # Convenience for other files
    )


# ----------------------------------------------------------------------
class TokenPhrase(Phrase):
    """Phrase that matches against a token"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        token: Token,
        name: Optional[str]=None,
    ):
        assert token

        if name is None:
            name = token.name

        super(TokenPhrase, self).__init__(name)

        self.token                          = token

    # ----------------------------------------------------------------------
    @Interface.override
    def Lex(
        self,
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        single_threaded=False,              # type: ignore  # pylint: disable=unused-argument
        ignore_whitespace=False,            # type: ignore  # pylint: disable=unused-argument
    ) -> Optional[Phrase.LexResult]:
        result: Optional[Token.MatchResult] = None

        observer.StartPhrase(unique_id, self)
        with CallOnExit(lambda: observer.EndPhrase(unique_id, self, result is not None)):
            working_iter = normalized_iter.Clone()

            result = self.token.Match(working_iter)
            if result is None:
                return Phrase.LexResult.Create(
                    False,
                    Phrase.NormalizedIteratorRange.Create(working_iter, working_iter),
                    Phrase.LexResultData.Create(self, unique_id, None, None),
                )

            iter_range = Phrase.NormalizedIteratorRange.Create(normalized_iter.Clone(), working_iter)

            data = Phrase.LexResultData.Create(
                self,
                unique_id,
                Phrase.TokenLexResultData.Create(
                    self.token,
                    result,
                    is_ignored=self.token.is_always_ignored,
                ),
                None,
            )

            if isinstance(self.token, IndentToken):
                observer.OnPushScope(iter_range, data)
            elif isinstance(self.token, DedentToken):
                observer.OnPopScope(iter_range, data)
            elif not observer.OnInternalPhrase(iter_range, data):
                return None

            return Phrase.LexResult.Create(True, iter_range, data)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PrettyPrint(
        indentation: str,
        data: Phrase.LexResultData.DataItemType,
        output_stream: TextIO,
    ) -> None:
        assert isinstance(data, Phrase.TokenLexResultData), data

        if data.is_ignored or not isinstance(data.token, RegexToken):
            return

        assert isinstance(data.value, RegexToken.MatchResult), data.value
        output_stream.write("{}{}\n".format(indentation, data.value.match.group()))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,                 # type: ignore  # pylint: disable=unused-argument
    ) -> bool:
        # Nothing downstream has changed (because there isn't anything downstream)
        return False
