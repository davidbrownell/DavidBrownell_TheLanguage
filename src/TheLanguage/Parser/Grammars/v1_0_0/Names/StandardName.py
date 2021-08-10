# ----------------------------------------------------------------------
# |
# |  StandardName.py
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
"""Contains the StandardName object"""

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

    MessageTemplate                         = Interface.DerivedProperty("'{Name}' is not a valid variable name; variables must start with a lowercase character.")


# ----------------------------------------------------------------------
class StandardName(GrammarPhrase):
    """<name>"""

    NODE_NAME                               = "Standard Name"
    VALIDATION_EXPRESSION                   = re.compile(r"^_?[a-z][a-zA-Z0-9_\.]*$")

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardName, self).__init__(
            GrammarPhrase.Type.Name,
            CreatePhrase(
                name=self.NODE_NAME,
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

        if not cls.VALIDATION_EXPRESSION.match(name):
            raise InvalidNameError.FromNode(leaf, name)
