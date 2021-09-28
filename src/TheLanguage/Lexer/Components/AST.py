# ----------------------------------------------------------------------
# |
# |  AST.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 22:03:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that are used when building an Abstract Syntax Tree (AST)
during the lexing process.
"""

import os

from typing import Any, Callable, Generator, List, Optional, Tuple, Union

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
    from .Token import Token


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class _ASTBase(Interface.Interface, YamlRepr.ObjectReprImplBase):
    """Common base class for nodes and leaves"""

    Type: Union[None, Phrase, Token]
    Parent: Optional["_ASTBase"]            = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
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
    def Enum(
        *,
        leaves_only=False,
        nodes_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node"], None, None]:
        """Enumerate this item and all of its children"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Node(_ASTBase):
    """Result of a Phrase"""

    Children: List[Union["Node", "Leaf"]]   = field(default_factory=list)

    IterBegin: Optional[NormalizedIterator] = field(init=False, default=None)
    IterEnd: Optional[NormalizedIterator]   = field(init=False, default=None)

    # ----------------------------------------------------------------------
    def FinalInit(self):
        # Calculate the extent of the iterators. Note that this cannot be done during __post_init__,
        # as all of the children and not yet known.
        min_iter = None
        max_iter = None

        for child in self.Children:  # pylint: disable=not-an-iterable
            if isinstance(child, Leaf) and child.IsIgnored:
                continue

            # Min
            child_min_iter = child.IterBegin
            if (
                child_min_iter is not None
                and (
                    min_iter is None
                    or child_min_iter.Offset < min_iter.Offset
                )
            ):
                min_iter = child_min_iter

            # Max
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
    def Enum(
        self,
        *,
        leaves_only=False,
        nodes_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", "Node"], None, None]:
        if not leaves_only and not children_first:
            yield self

        for child in self.Children:  # pylint: disable=not-an-iterable
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

    Whitespace: Optional[Tuple[int, int]]
    Value: Token.MatchResult
    IterBegin: NormalizedIterator
    IterEnd: NormalizedIterator
    IsIgnored: bool

    # ----------------------------------------------------------------------
    @Interface.override
    def Enum(
        self,
        *,
        leaves_only=False,
        nodes_only=False,
        children_first=False,
    ) -> Generator[Union["Leaf", Node], None, None]:
        if not nodes_only:
            yield self
