# ----------------------------------------------------------------------
# |
# |  GrammarStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 15:47:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tools and utilities that help creating statements within a grammar"""

import os

from enum import auto, Enum
from typing import List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserImpl.MultifileParser import (
        Observer as MultifileParserObserver,
        Node,
    )

    from ..ParserImpl.Statement import Statement


# ----------------------------------------------------------------------
class GrammarStatement(Interface.Interface):
    """An individual statement within a grammar"""

    # ----------------------------------------------------------------------
    class Type(Enum):
        """A Statement will be one of these types"""

        Statement                           = auto()
        Expression                          = auto()

    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_value: "GrammarStatement.Type",
        statement: Statement,
    ):
        self.TypeValue                      = type_value
        self.Statement                      = statement

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def Lower(
        node: Node,
    ):
        """Opportunity to lower the node associated with the statement (if necessary)"""
        return


# ----------------------------------------------------------------------
class ImportGrammarStatement(GrammarStatement):
    """Grammar statement that imports content; this functionality requires special handling"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Statement,
    ):
        super(ImportGrammarStatement, self).__init__(
            GrammarStatement.Type.Statement,
            statement,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ProcessImportStatement(
        source_roots: List[str],
        fully_qualified_name: str,
        node: Node,
    ) -> MultifileParserObserver.ImportInfo:
        """Returns ImportInfo for the statement"""
        raise Exception("Abstract method")  # pragma: no cover
