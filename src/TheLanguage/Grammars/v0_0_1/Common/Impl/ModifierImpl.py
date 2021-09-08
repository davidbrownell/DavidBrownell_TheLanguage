# ----------------------------------------------------------------------
# |
# |  ModifierImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 15:08:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Mixin objects that help when creating modifiers used during the parsing process"""

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
    from .....Parser.Phrases.DSL import ExtractOr, ExtractToken, Leaf, Node


# ----------------------------------------------------------------------
EnumType                                    = TypeVar("EnumType")


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class StandardMixin(object):
    # ----------------------------------------------------------------------
    @classmethod
    def CreatePhraseItem(
        cls,
    ) -> Tuple[str, ...]:
        return _StandardCreatePhraseItem(cls)  # type: ignore

    # ----------------------------------------------------------------------
    @classmethod
    def Extract(
        cls: EnumType,
        node: Node,
    ) -> EnumType:
        return _StandardExtract(cls, node)


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def CreateStandardCreatePhraseItemFunc(
    the_enum: Type[Enum],
) -> Callable[[], Tuple[str, ...]]:
    return lambda: _StandardCreatePhraseItem(the_enum)


# ----------------------------------------------------------------------
def CreateStandardExtractFunc(
    the_enum: EnumType,
) -> Callable[[Node], EnumType]:
    return lambda node: _StandardExtract(the_enum, node)


# ----------------------------------------------------------------------
def CreateByValueCreatePhraseItemFunc(
    the_enum: Type[Enum],
) -> Callable[[], Tuple[str, ...]]:
    return lambda: _ByValueCreatePhraseItem(the_enum)


# ----------------------------------------------------------------------
def CreateByValueExtractFunc(
    the_enum: EnumType,
) -> Callable[[Node], EnumType]:
    return lambda node: _ByValueExtract(the_enum, node)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _StandardCreatePhraseItem(
    the_enum: Type[Enum],
) -> Tuple[str, ...]:
    return tuple(e.name for e in the_enum)


# ----------------------------------------------------------------------
def _StandardExtract(
    the_enum: EnumType,
    node: Node,
) -> EnumType:
    value = cast(
        str,
        ExtractToken(
            cast(Leaf, ExtractOr(node)),
            use_match=True,
        ),
    )

    return the_enum[value]  # type: ignore


# ----------------------------------------------------------------------
def _ByValueCreatePhraseItem(
    the_enum: Type[Enum],
) -> Tuple[str, ...]:
    return tuple(e.value for e in the_enum)


# ----------------------------------------------------------------------
def _ByValueExtract(
    the_enum: EnumType,
    node: Node,
) -> EnumType:
    value = cast(
        str,
        ExtractToken(
            cast(Leaf, ExtractOr(node)),
            use_match=True,
        ),
    )

    for e in the_enum:  # type: ignore
        if e.value == value:
            return e

    assert False, value
