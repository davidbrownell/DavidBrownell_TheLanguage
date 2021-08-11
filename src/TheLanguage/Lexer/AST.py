# ----------------------------------------------------------------------
# |
# |  ASK.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 09:10:31
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
Contains Abstract Syntax Tree (AST) definitions; these are the building blocks
produced during the Lexing process.
"""

import os
import textwrap

from enum import Enum, Flag
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SourceLocation(object):
    """\
    Human-consumable location within a source file.

    This is generally used to display errors.
    """

    Filename: str
    Line: int
    Column: int
    Offset: int

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Filename
        assert self.Line >= 1, self.Line
        assert self.Column >= 1, self.Column
        assert self.Offset >= 0, self.Offset

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
            include_class=False,
        )

    # ----------------------------------------------------------------------
    def ToString(self) -> str:
        return "{} [{}, {}]".format(self.Filename, self.Line, self.Column)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class SourceRange(object):
    """\
    Human-consumable range of locations within a source file.

    This is generally used to display errors.
    """

    Start: SourceLocation
    End: SourceLocation

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Start.Filename == self.End.Filename
        assert (
            (
                self.End.Line == self.Start.Line
                and self.End.Column > self.Start.Column
            )
            or self.End.Line > self.Start.Line
        )

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
            include_class=False,
        )

    # ----------------------------------------------------------------------
    def ToString(self) -> str:
        return "{} [{}, {} -> {}, {}]".format(
            self.Start.Filename,
            self.Start.Line,
            self.Start.Column,
            self.End.Line,
            self.End.Column,
        )

    # ----------------------------------------------------------------------
    def Contains(
        self,
        other: "SourceRange",
    ) -> bool:
        if self.Start.Filename != other.Start.Filename:
            return False

        # ----------------------------------------------------------------------
        def Compare(
            a: SourceLocation,
            b: SourceLocation,
        ) -> int:
            result = a.Line - b.Line
            if result != 0:
                return result

            return a.Column - b.Column

        # ----------------------------------------------------------------------

        return Compare(self.Start, other.Start) <= 0 and Compare(self.End, other.End) >= 0


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Node(Interface.Interface):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    SourceRangesItemType                    = Union[
        None,                                                               # The corresponding value is a flag or optional (note that this value does not need to appear with the dict)
        SourceRange,                                                        # The corresponding value is an enum or string
        Tuple[SourceRange, List["SourceRangesItemType"]],                   # The corresponding value is a list
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    SourceRange: Optional[SourceRange]
    SourceRanges: Optional[Dict[str, SourceRangesItemType]]
    Parent: Optional["Node"]                = field(init=False, default=None)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __post_init__(self):
        # Ensure that every data item has a corresponding location
        source_locations = self.SourceRanges or {}

        d = {}

        for k, v in self.__dict__.items():
            if k in [
                "Type",
                "SourceRange",
                "SourceRanges",
                "Parent",
            ]:
                continue

            if k.startswith("_"):
                continue

            d[k] = v

        # If we only have a single value and that value is a string or Enum we don't need to have
        # additional SourceRanges values as SourceRange is sufficient.
        if len(d) == 1 and isinstance(next(iter(d.values())), (str, Enum)):
            return

        for k, v in d.items():
            self._EnsureValidMembers(
                [k],
                self.SourceRange,
                v,
                source_locations.get(k, None),
            )

        # Set the parent to self for all Nodes
        for k, v in self.__dataclass_fields__.items():  # type: ignore  # pylint: disable=no-member
            if k == "Parent":
                continue

            if (
                isinstance(v, Node)
                or (isinstance(v, list) and all(isinstance(item, Node) for item in v))
            ):
                if isinstance(v, Node):
                    v = [v]

                for item in v:
                    assert item.Parent is None, item
                    object.__setattr__(item, "Parent", self)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
            include_class=False,
        )

    # TODO: Enumerate

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    _EnsureValidMembersValueType          = Union[
        None,                                           # No location value expected
        Flag,                                           # No location value expected
        "Node",                                         # No location value expected (will use the information in the Node)
        Enum,                                           # SourceRange expected
        str,                                            # SourceRange expected
        List["_EnsureValidMembersValueType"],         # Tuple[SourceRange, List[...]] expected
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _EnsureValidMembers(
        cls,
        name_stack: List[Any],
        containing_range: Optional[SourceRange],
        value: _EnsureValidMembersValueType,
        range_value: SourceRangesItemType,
    ):
        if value is None or isinstance(value, Flag):
            return

        # ----------------------------------------------------------------------
        def CreateException(
            message: str,
        ) -> Exception:
            return Exception(
                textwrap.dedent(
                    """\
                    {}

                    [{}]
                    """,
                ).format(
                    message.rstrip(),
                    " / ".join([str(name) for name in name_stack]),
                ),
            )

        # ----------------------------------------------------------------------
        def EnsureContains(
            outer_range: Optional[SourceRange],
            inner_range: SourceRange,
            item_desc: str,
        ):
            if outer_range is None:
                return

            if outer_range.Start.Filename != inner_range.Start.Filename:
                # TODO: This should only happen for certain node types; not sure what those are right now
                return

            if not outer_range.Contains(inner_range):
                raise CreateException(
                    textwrap.dedent(
                        """\
                        The {item_desc_lower} is not contained within the parent node:

                            Parent: {outer}
                            {item_desc:<7} {inner}
                        """,
                    ).format(
                        item_desc_lower=item_desc.lower(),
                        item_desc="{}:".format(item_desc),
                        outer=outer_range.ToString(),
                        inner=inner_range.ToString(),
                    ),
                )

        # ----------------------------------------------------------------------

        if isinstance(value, Node):
            if value.SourceRange is not None:
                EnsureContains(containing_range, value.SourceRange, "Node")

        elif isinstance(value, (Enum, str)):
            if not isinstance(range_value, SourceRange):
                raise CreateException("Invalid type ('{}')".format(type(range_value)))

            EnsureContains(containing_range, range_value, "Value")

        elif isinstance(value, list):
            if not value:
                raise CreateException("'list' values may not be empty; consider declaring them as 'Optional[List[...]]'")

            if (
                not isinstance(range_value, tuple)
                or len(range_value) != 2
                or not isinstance(range_value[0], SourceRange)
                or not isinstance(range_value[1], List)
            ):
                raise CreateException("Invalid type ('{}')".format(type(range_value)))

            range_value, range_values = range_value

            EnsureContains(containing_range, range_value, "List")

            if len(value) != len(range_values):
                raise CreateException(
                    "The list lengths do not match ('{}' vs. '{}')".format(
                        len(value),
                        len(range_values),
                    ),
                )

            for item_index, (item, range_item) in enumerate(zip(value, range_values)):
                cls._EnsureValidMembers(
                    name_stack + [item_index],
                    range_value,
                    item,
                    range_item,
                )

        else:
            assert False, value  # pragma: no cover


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeNode(Node):
    """\
    TODO: Comment
    """
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ExpressionNode(Node):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def ExpressionResultType(self) -> TypeNode:
        """Result of the expression"""


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementNode(Node):
    """\
    TODO: Comment
    """


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariableNode(Node):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def VarNames() -> List[str]:
        """Returns a list of variable names made available by node"""
        raise Exception("Abstract method")  # pragma: no cover
