# ----------------------------------------------------------------------
# |
# |  VariableName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:12:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableName object"""

import os
import re

from typing import cast, Optional

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
    from ...GrammarPhrase import GrammarPhrase, Node, ValidationError
    from ....Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
# TODO: Is is probably safe to remove this, as CommonTokens.GenericName is now pretty much an exact match for the validation expression
@dataclass(frozen=True)
class InvalidVariableNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Name}' is not a valid variable or parameter name; names must start with a lowercase letter.",
    )


# ----------------------------------------------------------------------
class VariableName(GrammarPhrase):
    """\
    A variable name

    <name>

    Examples:
        foo
        bar
    """

    PHRASE_NAME                             = "Variable Name"
    VALIDATION_EXPRESSION                   = re.compile(r"^_?[a-z][a-zA-Z0-9_]*(?!<__)$")

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableName, self).__init__(
            GrammarPhrase.Type.Name,
            CreatePhrase(
                name=self.PHRASE_NAME,

                # Note that this needs to be a sequence rather than just the name as this is the only
                # way to ensure that the validation below is invoked. If just the name, there would
                # be nothing to tie the token to this phrase.
                item=[CommonTokens.GenericName],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # TODO: Revisit this

        nodes = ExtractSequence(node)
        assert len(nodes) == 1

        leaf = cast(Leaf, nodes[0])
        name = cast(str, ExtractToken(leaf))

        if not cls.VALIDATION_EXPRESSION.match(name):
            raise InvalidVariableNameError.FromNode(leaf, name)
