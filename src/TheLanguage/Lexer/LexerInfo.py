# ----------------------------------------------------------------------
# |
# |  LexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 14:48:33
# |
# ----------------------------------------------------------------------
# | = """/*
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LexerInfo object"""

import os

from typing import Any, Callable, Dict, Optional, Tuple, Union

from dataclasses import (
    dataclass,
    fields,
    _PARAMS as DATACLASS_PARAMS,  # type: ignore
)

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Parser.Components.AST import Leaf, Node


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LexerInfo(YamlRepr.ObjectReprImplBase):
    TokenLookup: Dict[str, Union[Leaf, Node]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        # Ensure that the derived class has been created correctly
        assert (  # type: ignore
            hasattr(self, DATACLASS_PARAMS)
            and not getattr(self, DATACLASS_PARAMS).repr,
        ), "Derived classes should be based on `dataclass` with `repr` set to `False`"

        assert "self" in self.TokenLookup

        # Ensure that everything that needs to have an entry in TokenLookup has one
        for field in fields(self):
            if field.name == "TokenLookup":
                continue

            if field.type == Any:
                continue

            value = getattr(self, field.name)
            if value is None:
                continue

            if isinstance(value, list):
                if value:
                    assert isinstance(value[0], (Node, LexerInfo)), (field.name, field.type, value)

                continue

            if isinstance(value, (Node, LexerInfo)):
                continue

            if field.name in custom_display_funcs and custom_display_funcs[field.name] is None:
                continue

            assert field.name in self.TokenLookup, ("Missing item in TokenLookup", field.name)

        # Ensure that all the lookup values are not None
        for k, v in self.TokenLookup.items():
            assert v is not None, k

        YamlRepr.ObjectReprImplBase.__init__(
            self,
            TokenLookup=None,
            **custom_display_funcs,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Error(Exception, Interface.Interface):
    """Base error for all Lexer-related errors"""

    Line: int
    Column: int
    LineEnd: int
    ColumnEnd: int

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Union[Leaf, Node],
        *args,
    ):
        # ----------------------------------------------------------------------
        def GetLineColumn(iterator) -> Tuple[int, int]:
            if iterator is None:
                return -1, -1

            return iterator.Line, iterator.Column

        # ----------------------------------------------------------------------

        line_before, column_before = GetLineColumn(node.IterBegin)
        line_after, column_after = GetLineColumn(node.IterEnd)

        if isinstance(node, Leaf) and node.Whitespace is not None:
            column_before += node.Whitespace[1] - node.Whitespace[0] - 1

        return cls(
            line_before,
            column_before,
            line_after,
            column_after,
            *args,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Line >= 1
        assert self.Column >= 1
        assert self.Line <= self.LineEnd
        assert self.Line != self.LineEnd or self.Column <= self.ColumnEnd

    # ----------------------------------------------------------------------
    def __str__(self):
        # pylint: disable=no-member
        return self.MessageTemplate.format(**self.__dict__)

    # ----------------------------------------------------------------------
    @Interface.abstractmethod
    def MessageTemplate(self) -> str:
        """Template used when generating the exception string"""
        raise Exception("Abstract method")  # pragma: no cover
