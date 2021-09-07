# ----------------------------------------------------------------------
# |
# |  StandardType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 11:31:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardType object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common.TypeModifier import TypeModifier
    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTypeError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid type name; names must start with an uppercase letter and be at least 2 characters.")  # type: ignore


# ----------------------------------------------------------------------
class StandardType(GrammarPhrase):
    """\
    Type declaration.

    <type_name> <modifier>?

    Examples:
        Int
        Int var
    """

    PHRASE_NAME                             = "Standard Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <type_name>
                    CommonTokens.TypeName,

                    # <modifier>?
                    PhraseItem(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
                        arity="?",
                    ),
                ],
            ),
        )
