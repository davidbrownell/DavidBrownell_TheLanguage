# ----------------------------------------------------------------------
# |
# |  AST.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-12 16:14:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types and methods that are used when building an Abstract Syntax Tree (AST)"""

import os
import textwrap

from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .Token import Token

    from .Statements.Statement import Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ASTBase(Interface.Interface):
    """Common base class for nodes and leaves"""

    Type: Union[None, Statement, Token]
    Parent: Optional[Statement]             = field(default_factory=lambda: None, init=False)

    # ----------------------------------------------------------------------
    def __str__(self):
        return self.ToString()

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def ToString(
        self,
        verbose=False,
    ) -> str:
        if self.Type is None:
            return "<Root>" if isinstance(self, RootNode) else "<None>"

        return self.Type.Name


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _Node(_ASTBase):
    """Common base class for `RootNode` and `Node`"""

    Children: List[Union["Node", "Leaf"]]   = field(default_factory=list)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        verbose=False,
    ) -> str:
        children = [
            child.ToString(
                verbose=verbose,
            ).rstrip()
            for child in self.Children  # pylint: disable=not-an-iterable
        ]

        if not children:
            children.append("<No Children>")

        return textwrap.dedent(
            """\
            {heading}
                {children}
            """,
        ).format(
            heading=super(_Node, self).ToString(
                verbose=verbose,
            ),
            children=StringHelpers.LeftJustify(
                "\n".join(children),
                4,
            ),
        )

    # ----------------------------------------------------------------------
    @property
    def IterBefore(self):
        node = self

        while isinstance(node, _Node):
            node = node.Children[0]  # pylint: disable=unsubscriptable-object
        return cast(Leaf, node).IterBefore

    @property
    def IterAfter(self):
        node = self

        while isinstance(node, _Node):
            node = node.Children[-1]  # pylint: disable=unsubscriptable-object

        return cast(Leaf, node).IterAfter


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RootNode(_Node):
    """Root of the tree"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Node(_Node):
    """Result of a `Statement`"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Leaf(_ASTBase):
    """AST results of a Token"""

    Whitespace: Optional[Tuple[int, int]]   # Whitespace immediately before the token
    Value: Token.MatchType                  # Result of the call to Token.Match
    IterBefore: NormalizedIterator          # NormalizedIterator before the token
    IterAfter: NormalizedIterator           # NormalizedIterator after the token has been consumed
    IsIgnored: bool                         # True if the result is whitespace while whitespace is being ignored

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        verbose=False,
    ) -> str:
        return "{super_string} <<{value}>> ws:{ws}{ignored} [{line_before}, {column_before} -> {line_after}, {column_after}]".format(
            super_string=super(Leaf, self).ToString(
                verbose=verbose,
            ),
            value=str(self.Value),
            ws="None" if self.Whitespace is None else "({}, {})".format(*self.Whitespace),
            ignored=" !Ignored!" if self.IsIgnored else "",
            line_before=self.IterBefore.Line,
            column_before=self.IterBefore.Column,
            line_after=self.IterAfter.Line,
            column_after=self.IterAfter.Column,
        )
