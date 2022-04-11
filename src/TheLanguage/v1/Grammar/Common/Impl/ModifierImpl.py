# ----------------------------------------------------------------------
# |
# |  ModifierImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 10:12:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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
    from ...GrammarPhrase import AST

    from ....Lexer.Phrases.DSL import (
        ExtractOr,
        ExtractToken,
    )


# ----------------------------------------------------------------------
EnumType                                    = TypeVar("EnumType", bound=Enum)


# ----------------------------------------------------------------------
def StandardCreatePhraseItemFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[], Tuple[str, ...]]:
    # ----------------------------------------------------------------------
    def CreatePhraseItem() -> Tuple[str, ...]:
        return tuple(e.name for e in the_enum)

    # ----------------------------------------------------------------------

    return CreatePhraseItem


# ----------------------------------------------------------------------
def StandardExtractFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[AST.Node], EnumType]:
    # ----------------------------------------------------------------------
    def Extract(
        node: AST.Node,
    ) -> EnumType:
        value = ExtractToken(
            cast(AST.Leaf, ExtractOr(node)),
            return_match_contents=True,
        )

        return the_enum[value]

    # ----------------------------------------------------------------------

    return Extract


# ----------------------------------------------------------------------
def ByValueCreatePhraseItemFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[], Tuple[str, ...]]:
    # ----------------------------------------------------------------------
    def CreatePhraseItem() -> Tuple[str, ...]:
        return tuple(e.value for e in the_enum)

    # ----------------------------------------------------------------------

    return CreatePhraseItem


# ----------------------------------------------------------------------
def ByValueExtractFuncFactory(
    the_enum: Type[EnumType],
) -> Callable[[AST.Node], EnumType]:
    # ----------------------------------------------------------------------
    def Extract(
        node: AST.Node,
    ) -> EnumType:
        value = ExtractToken(
            cast(AST.Leaf, ExtractOr(node)),
            return_match_contents=True,
        )

        for e in the_enum:
            if e.value == value:
                return e

        assert False, value  # pragma: no cover

    # ----------------------------------------------------------------------

    return Extract
