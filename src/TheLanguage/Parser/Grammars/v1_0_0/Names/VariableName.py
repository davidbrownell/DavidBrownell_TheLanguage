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
    from ....Phrases.DSL import CreatePhrase, ExtractSequence


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidNameError(ValidationError):
    Name: str

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid variable or parameter name; names must start with a lowercase letter.")


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
    VALIDATION_EXPRESSION                   = re.compile(r"^_?[a-z][a-zA-Z0-9_\.]*(?!<__)$")

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableName, self).__init__(
            GrammarPhrase.Type.Name,
            CreatePhrase(
                name=self.PHRASE_NAME,

                # TODO: Does this need to be in a sequence?
                item=[CommonTokens.GenericName],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateNodeSyntax(
        cls,
        node: Node,
    ):
        nodes = ExtractSequence(node)
        assert len(nodes) == 1
        name, leaf = nodes[0]  # type: ignore

        if not cls.VALIDATION_EXPRESSION.match(name):  # type: ignore
            raise InvalidNameError.FromNode(leaf, name)
