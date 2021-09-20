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

from typing import Any, Callable, Generator, List, Optional, TextIO, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

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
class _ASTBase(Interface.Interface, YamlRepr.ObjectReprImplBase):
    """Common base class for nodes and leaves"""

    Type: Union[None, Phrase, Token]
    Parent: Optional["_ASTBase"]            = field(default=None, init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Callable[[Any], Optional[str]],
    ):
        YamlRepr.ObjectReprImplBase.__init__(
            self,
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
    @staticmethod
    @Interface.abstractmethod
    def Enum(
        leaves_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node", "RootNode"], None, None]:
        """Enumerates this item and all of its children"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _Node(_ASTBase):
    """Common base class for `RootNode` and `Node`"""

    Children: List[Union["Node", "Leaf"]]   = field(default_factory=list)

    IterBegin: Optional[NormalizedIterator] = field(init=False, default=None)
    IterEnd: Optional[NormalizedIterator]   = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def FinalInit(self):
        # Calculate the extent of the iterators. Note that this cannot be done during __post_init__,
        # as all of the children are not yet known.
        min_iter = None
        max_iter = None

        # pylint: disable=not-an-iterable
        for child in self.Children:
            if isinstance(child, Leaf) and child.IsIgnored:
                continue

            child_min_iter = child.IterBegin
            if (
                child_min_iter is not None
                and (
                    min_iter is None
                    or child_min_iter.Offset < min_iter.Offset
                )
            ):
                min_iter = child_min_iter

            child_max_iter = child.IterEnd
            if (
                child_max_iter is not None
                and (
                    max_iter is None
                    or child_max_iter.Offset > max_iter.Offset
                )
            ):
                max_iter = child_max_iter

        object.__setattr__(self, "IterBegin", min_iter)
        object.__setattr__(self, "IterEnd", max_iter)

    # ----------------------------------------------------------------------
    @Interface.override
    def DebugOutput(
        self,
        output_stream: TextIO,
        indentation_prefix: Optional[str]=None,
    ):
        if indentation_prefix is None:
            indentation_prefix = ""

        # pylint: disable=not-an-iterable
        for child in self.Children:
            child.DebugOutput(output_stream, indentation_prefix)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enum(
        self,
        leaves_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node", "RootNode"], None, None]:
        if not leaves_only and not children_first:
            yield self  # type: ignore

        # pylint: disable=not-an-iterable
        for child in self.Children:
            yield from child.Enum(
                leaves_only=leaves_only,
                children_first=children_first,
            )

        if not leaves_only and children_first:
            yield self  # type: ignore


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
    IterBegin: NormalizedIterator          # NormalizedIterator before the token
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

    # ----------------------------------------------------------------------
    @Interface.override
    def Enum(
        self,
        leaves_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", Node, RootNode], None, None]:
        yield self
