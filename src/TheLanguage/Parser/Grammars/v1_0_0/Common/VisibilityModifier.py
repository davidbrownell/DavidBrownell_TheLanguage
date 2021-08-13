# ----------------------------------------------------------------------
# |
# |  VisibilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 15:25:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with visibility modifiers"""

import os

from enum import auto, Enum
from typing import Callable, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from ...GrammarPhrase import ValidationError
    from ....Phrases.DSL import ExtractToken, Leaf, Node, PhraseItem


# ----------------------------------------------------------------------
class VisibilityModifier(Enum):
    """\
    Modifies the external visibility of a function, method, class attribute, etc.
    """

    private                                 = auto()
    protected                               = auto()
    public                                  = auto()

    # ----------------------------------------------------------------------
    @staticmethod
    def CreatePhraseItem():
        return CommonTokens.GenericLowerName

    # ----------------------------------------------------------------------
    @staticmethod
    def Extract(
        node: Union[Node, Tuple[str, Leaf]],
    ) -> "VisibilityModifier":
        return _ExtractImpl(node)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidVisibilityModifierError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty(
        "The visibility modifier '{{Name}}' is not valid; values may be {}.".format(
            ", ".join(["'{}'".format(e.name) for e in VisibilityModifier]),
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractImpl(
    node: Union[Node, Tuple[str, Leaf]],
) -> VisibilityModifier:

    if isinstance(node, tuple):
        name, leaf = node
    else:
        name = ExtractToken(
            node,  # type: ignore
            use_match=True,
        )

        leaf = node

    try:
        return VisibilityModifier[name]  # type: ignore
    except KeyError:
        raise InvalidVisibilityModifierError.FromNode(leaf, name)
