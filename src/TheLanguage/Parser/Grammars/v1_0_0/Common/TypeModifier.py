# ----------------------------------------------------------------------
# |
# |  TypeModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 12:50:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with type modifiers"""

import os
import re
import textwrap

from enum import auto, IntFlag
from typing import Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import ValidationError
    from ....Components.Token import RegexToken
    from ....Phrases.DSL import ExtractToken, Leaf, Node


# ----------------------------------------------------------------------
class TypeModifier(IntFlag):
    """\
    Modifies the behavior of a type.

    |-----------|----------|--------|
    |           | isolated | shared |
    |-----------|----------|--------|
    | mutable   |    var   |   ref  |
    | immutable |    val   |  view  |
    |-----------|----------|--------|
    """

    mutable                                 = auto()
    immutable                               = auto()
    isolated                                = auto()
    shared                                  = auto()

    var                                     = (mutable << 4) | isolated
    ref                                     = (mutable << 4) | shared
    val                                     = (immutable << 4) | isolated
    view                                    = (immutable << 4) | shared

    # ----------------------------------------------------------------------
    @classmethod
    def CreatePhraseItem(cls):
        # This code is attempting to walk a fine line - errors indicating that a modifier isn't
        # valid are much better than generic syntax errors. If we look for the exact modifier
        # tokens, we will produce syntax errors when it isn't found. However, if we just look for a
        # general string, we will greedily consume other tokens are produce syntax errors. So here,
        # we are producing a regular expression that is "close" to what a user might likely type
        # without requiring an exact match.
        return RegexToken(
            "Type Modifier",
            re.compile(
                textwrap.dedent(
                    r"""(?#
                        3 letter word: v..  )(?:v[a-z]{2}\b)(?#
                        3 letter word: ..f  )|(?:[a-z]{2}f\b)(?#
                        4 letter word: v..w )|(?:v[a-z]{2}w\b)(?#
                        Ends with 'able'    )|(?:[a-z]+able\b)(?#
                        Ends with 'ed'      )|(?:[a-z]+ed\b)(?#
                    )""",
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def Extract(
        node: Union[Node, Tuple[str, Leaf]],
    ) -> "TypeModifier":
        return _ExtractImpl(node)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTypeModifierError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty(
        "The type modifier '{{Name}}' is not valid; values may be {}.".format(
            ", ".join(["'{}'".format(e.name) for e in TypeModifier]),
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractImpl(
    node: Union[Node, Tuple[str, Leaf]],
) -> TypeModifier:
    if isinstance(node, tuple):
        name, leaf = node
    else:
        name = ExtractToken(
            node,  # type: ignore
            use_match=True,
        )

        leaf = node

    try:
        return TypeModifier[name]  # type: ignore
    except KeyError:
        raise InvalidTypeModifierError.FromNode(leaf, name)
