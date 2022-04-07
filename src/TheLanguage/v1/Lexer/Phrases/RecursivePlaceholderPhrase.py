# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-03 13:25:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RecursivePlaceholderPhrase object"""

import os

from typing import TextIO, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Phrase import NormalizedIterator, Phrase


# ----------------------------------------------------------------------
class RecursivePlaceholderPhrase(Phrase):
    """\
    Temporary Phrase that should be replaced before participating in Lexing activities.

    Instances of this object are used as sentinels within a Phrase hierarchy to implement
    recursive grammars.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(RecursivePlaceholderPhrase, self).__init__("Recursive")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Lex(
        unique_id: Tuple[str, ...],
        normalized_iter: NormalizedIterator,
        observer: Phrase.Observer,
        *,
        ignore_whitespace=False,  # type: ignore  # pylint: disable=unused-argument
    ):
        raise Exception("This method should never be called on an instance of this object")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def PrettyPrint(
        indentation: str,
        data: Phrase.LexResultData.DataItemType,
        output_stream: TextIO,
    ) -> None:
        raise Exception("This method should never be called on an instance of this object")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _PopulateRecursiveImpl(
        new_phrase: "Phrase",
    ) -> bool:
        raise Exception("This method should never be called on an instance of this object")
