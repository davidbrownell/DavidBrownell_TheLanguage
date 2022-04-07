# ----------------------------------------------------------------------
# |
# |  AST.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 09:57:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that is used when building Abstract Syntax Trees (ASTs) during the lexing process"""

import os

from typing import Any, Callable, Generator, List, Optional, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator, OffsetRange
    from .Phrase import Phrase
    from .Tokens import Token


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _ASTBase(Interface.Interface, ObjectReprImplBase):
    """Common base class for all nodes and leaves"""

    type: Union[None, Phrase, Token]
    parent: Optional["_ASTBase"]            = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        ObjectReprImplBase.__init__(
            self,
            type=lambda value: "<None>" if value is None else "{} {}".format(value.name, type(value)),
            parent=None,
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enum(
        *,
        leaves_only=-False,
        nodes_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node"], None, None]:
        """Enumerate this item and all of its children"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Node(_ASTBase):
    """Result of a Phrase"""

    children: List[Union["Node", "Leaf"]]                                   = field(default_factory=list)
    iter_range: Optional[Phrase.NormalizedIteratorRange]                    = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def FinalInit(self) -> None:
        if self.iter_range is not None:
            return

        # Calculate the extent of the range based on all of its children.
        min_iter: Optional[NormalizedIterator] = None
        max_iter: Optional[NormalizedIterator] = None

        for child in self.children:  # type: ignore  # pylint: disable=not-an-iterable
            if isinstance(child, Leaf):
                child_iter_range = child.iter_range

            elif isinstance(child, Node):
                child.FinalInit()
                child_iter_range = child.iter_range

            else:
                assert False, child  # pragma: no cover

            if child_iter_range is not None:
                if min_iter is None or child_iter_range.begin < min_iter:  # type: ignore
                    min_iter = child_iter_range.begin
                if max_iter is None or child_iter_range.end > max_iter:  # type: ignore
                    max_iter = child_iter_range.end

        if min_iter is not None:
            assert max_iter is not None

            object.__setattr__(
                self,
                "iter_range",
                Phrase.NormalizedIteratorRange.Create(min_iter, max_iter),
            )

    # ----------------------------------------------------------------------
    @Interface.override
    def Enum(
        self,
        *,
        leaves_only=False,
        nodes_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node"], None, None]:
        if not leaves_only and not children_first:
            yield self

        for child in self.children:  # type: ignore  # pylint: disable=not-an-iterable
            yield from child.Enum(
                leaves_only=leaves_only,
                nodes_only=nodes_only,
                children_first=children_first,
            )

        if not leaves_only and children_first:
            yield self


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Leaf(_ASTBase):
    """AST results of a Token"""

    value: Token.MatchResult
    iter_range: Phrase.NormalizedIteratorRange
    is_ignored: bool

    # ----------------------------------------------------------------------
    @Interface.override
    def Enum(
        self,
        *,
        leaves_only=False,                  # type: ignore  # pylint: disable=unused-argument
        nodes_only=False,
        children_first=False,               # type: ignore  # pylint: disable=unused-argument
    ) -> Generator[Union["Leaf", "Node"], None, None]:
        if not nodes_only:
            yield self
