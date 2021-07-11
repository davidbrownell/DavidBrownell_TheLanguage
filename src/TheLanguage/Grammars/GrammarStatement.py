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
from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserImpl.Error import Error

    from ..ParserImpl.TranslationUnitsParser import (
        DynamicStatements,
        Leaf,                               # This is here as a convenience for files that import this one; please do not remove
        Node,
        Observer as TranslationUnitsParserObserver,
        Statement,
        StatementEx,                        # This is here as a convenience for files that import this one; please do not remove
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ValidationError(Error):
    """Extend the `Error` base class to Include starting line and column attributes"""

    LineEnd: int
    ColumnEnd: int

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Node,
        *args,
    ):
        return cls(
            node.IterBefore.Line,
            node.IterBefore.Column,
            node.IterAfter.Line,
            node.IterAfter.Column,
            *args,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Line <= self.LineEnd
        assert self.Line != self.LineEnd or self.Column <= self.ColumnEnd


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
    def ValidateNodeSyntax(
        node: Node,
    ) -> Optional[bool]:                    # False to prevent child traversal
        """Opportunity to validate the syntax of a node; this method is invoked during calls to Parser.py:Validate"""
        return

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def Lower(
        node: Node,
    ) -> Optional[bool]:                    # False to prevent child traversal
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
    ) -> TranslationUnitsParserObserver.ImportInfo:
        """Returns ImportInfo for the statement"""
        raise Exception("Abstract method")  # pragma: no cover
