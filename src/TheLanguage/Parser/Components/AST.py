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

from typing import Any, Callable, cast, List, Optional, TextIO, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator
    from .Phrase import Phrase
    from .Token import Token, RegexToken


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _ASTBase(Interface.Interface, CommonEnvironment.ObjectReprImplBase):
    """Common base class for nodes and leaves"""

    Type: Union[None, Phrase, Token]
    Parent: Optional[Phrase]                = field(default=None, init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Callable[[Any], Optional[str]],
    ):
        CommonEnvironment.ObjectReprImplBase.__init__(
            self,
            include_class_info=False,
            Type=lambda value: "<None>" if value is None else "{} {}".format(value.Name, type(value)),
            Parent=None,
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def DebugOutput(
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ) -> None:
        """Writes debugging output to the provided stream"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _Node(_ASTBase):
    """Common base class for `RootNode` and `Node`"""

    Children: List[Union["Node", "Leaf"]]   = field(default_factory=list)

    # ----------------------------------------------------------------------
    @property
    def IterBegin_(self) -> Optional[NormalizedIterator]: # TODO: Change this to IterBegin once there is better tooling support to do so
        node = self

        while isinstance(node, _Node):
            if not node.Children:
                return None

            node = node.Children[0]  # <unscriptable> pylint: disable=E1136

        return cast(Leaf, node).IterBegin_

    @property
    def IterEnd(self) -> Optional[NormalizedIterator]:
        node = self

        while isinstance(node, _Node):
            if not node.Children:
                return None

            node = node.Children[-1]  # <unscriptable> pylint: disable=E1136

        return cast(Leaf, node).IterEnd


    # ----------------------------------------------------------------------
    @Interface.override
    def DebugOutput(
        self,
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ):
        if indentation_prefix is None:
            indentation_prefix = ""

        for child in self.Children:  # type: ignore
            child.DebugOutput(output_stream, indentation_prefix)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootNode(_Node):
    """Root of the tree"""

    # ----------------------------------------------------------------------
    @Interface.override
    def DebugOutput(
        self,
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ):
        if indentation_prefix is None:
            indentation_prefix = ""

        output_stream.write("{}<root>\n".format(indentation_prefix))

        super(RootNode, self).DebugOutput(output_stream, indentation_prefix + "    ")


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Node(_Node):
    """Result of a `Statement`"""

    # ----------------------------------------------------------------------
    @Interface.override
    def DebugOutput(
        self,
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ):
        if indentation_prefix is None:
            indentation_prefix = ""

        assert self.Type
        output_stream.write("{}{}\n".format(indentation_prefix, self.Type.Name))

        super(Node, self).DebugOutput(output_stream, indentation_prefix + "    ")


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Leaf(_ASTBase):
    """AST results of a Token"""

    Whitespace: Optional[Tuple[int, int]]   # Whitespace immediately before the token
    Value: Token.MatchResult                # Result of the call to Token.Match
    IterBegin_: NormalizedIterator          # NormalizedIterator before the token
    IterEnd: NormalizedIterator           # NormalizedIterator after the token has been consumed
    IsIgnored: bool                         # True if the result is whitespace while whitespace is being ignored

    # ----------------------------------------------------------------------
    @Interface.override
    def DebugOutput(
        self,
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ):
        if indentation_prefix is None:
            indentation_prefix = ""

        assert self.Type is not None
        output_stream.write(
            "{}{}{}\n".format(
                indentation_prefix,
                self.Type.Name,
                " [{}]".format(self.Value.Match) if isinstance(self.Value, RegexToken.MatchResult) else "",
            ),
        )
