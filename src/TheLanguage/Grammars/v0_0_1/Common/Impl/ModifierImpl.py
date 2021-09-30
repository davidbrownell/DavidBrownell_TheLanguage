# ----------------------------------------------------------------------
# |
# |  ModifierImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 12:25:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that helps lex and extract modifier enumerations"""

import os

from enum import Enum
from typing import Callable, cast, Type, TypeVar, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....Lexer.Phrases.DSL import ExtractOr, ExtractToken, Leaf, Node


# ----------------------------------------------------------------------
EnumType                                    = TypeVar("EnumType", bound=Enum)


# ----------------------------------------------------------------------
def StandardCreatePhraseItemFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[], Tuple[str, ...]]:
    # ----------------------------------------------------------------------
    def CreatePhraseItem():
        return tuple(e.name for e in the_enum)

    # ----------------------------------------------------------------------

    return CreatePhraseItem


# ----------------------------------------------------------------------
def StandardExtractFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[Node], EnumType]:
    # ----------------------------------------------------------------------
    def Extract(
        node: Node,
    ) -> EnumType:
        value = cast(
            str,
            ExtractToken(
                cast(Leaf, ExtractOr(node)),
                use_match=True,
            ),
        )

        return the_enum[value]

    # ----------------------------------------------------------------------

    return Extract
