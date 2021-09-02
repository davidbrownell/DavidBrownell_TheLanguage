# ----------------------------------------------------------------------
# |
# |  ModifierBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-02 12:15:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ModifierBase object"""

import os

from enum import Enum
from typing import cast

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....Phrases.DSL import ExtractOr, ExtractToken, Leaf, Node


# ----------------------------------------------------------------------
def CreateModifierBaseClass(
    by_value=False,
    base_class=Enum,
):
    if by_value:
        # ----------------------------------------------------------------------
        class ModifierImpl(base_class):
            # ----------------------------------------------------------------------
            @classmethod
            def CreatePhraseItem(cls):
                return tuple(e.value for e in cls)  # type: ignore

            # ----------------------------------------------------------------------
            @classmethod
            def Extract(
                cls,
                node: Node,
            ):
                value = cast(
                    str,
                    ExtractToken(
                        cast(Leaf, ExtractOr(node)),
                        use_match=True,
                    ),
                )

                for e in cls:  # type: ignore
                    if e.value == value:
                        return e

                assert False, value

        # ----------------------------------------------------------------------

    else:
        # ----------------------------------------------------------------------
        class ModifierImpl(base_class):
            # ----------------------------------------------------------------------
            @classmethod
            def CreatePhraseItem(cls):
                return tuple(e.name for e in cls)  # type: ignore

            # ----------------------------------------------------------------------
            @classmethod
            def Extract(
                cls,
                node: Node,
                match_by_value=False,
            ):
                value = cast(
                    str,
                    ExtractToken(
                        cast(Leaf, ExtractOr(node)),
                        use_match=True,
                    ),
                )

                return cls[value]  # type: ignore

        # ----------------------------------------------------------------------

    return ModifierImpl


# ----------------------------------------------------------------------
ModifierBase                                = CreateModifierBaseClass(base_class=Enum)
