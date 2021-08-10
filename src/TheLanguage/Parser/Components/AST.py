# ----------------------------------------------------------------------
# |
# |  AST.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-07 23:49:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""\
Contains types and methods that are used when building an Abstract Syntax Tree (AST)
for the parser.
"""

import os

from typing import Any, Callable, cast, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .Phrase import Phrase
    from .Token import Token


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _ASTBase(CommonEnvironment.ObjectReprImplBase):
    """Common base class for nodes and leaves"""

    Type: Union[None, Phrase, Token]
    Parent: Optional[Phrase]                = field(default=None, init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Callable[[Any], str],
    ):
        CommonEnvironment.ObjectReprImplBase.__init__(
            self,
            include_class_info=False,
            Type=lambda value: "<None>" if value is None else "{} {}".format(value.Name, type(value)),
            Parent=None,
            **custom_display_funcs,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _Node(_ASTBase):
    """Common base class for `RootNode` and `Node`"""

    Children: List[Union["Node", "Leaf"]]   = field(default_factory=list)

    # ----------------------------------------------------------------------
    @property
    def IterBefore(self) -> Optional[NormalizedIterator]:
        node = self

        while isinstance(node, _Node):
            if not node.Children:
                return None

            node = node.Children[0]  # <unscriptable> pylint: disable=E1136

        return cast(Leaf, node).IterBefore

    @property
    def IterAfter(self) -> Optional[NormalizedIterator]:
        node = self

        while isinstance(node, _Node):
            if not node.Children:
                return None

            node = node.Children[-1]  # <unscriptable> pylint: disable=E1136

        return cast(Leaf, node).IterAfter


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootNode(_Node):
    """Root of the tree"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Node(_Node):
    """Result of a `Statement`"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Leaf(_ASTBase):
    """AST results of a Token"""

    Whitespace: Optional[Tuple[int, int]]   # Whitespace immediately before the token
    Value: Token.MatchResult                # Result of the call to Token.Match
    IterBefore: NormalizedIterator          # NormalizedIterator before the token
    IterAfter: NormalizedIterator           # NormalizedIterator after the token has been consumed
    IsIgnored: bool                         # True if the result is whitespace while whitespace is being ignored
