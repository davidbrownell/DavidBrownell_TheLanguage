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

from typing import Any, Callable, Dict, Optional, Union

from dataclasses import (
    dataclass,
    fields,
    _PARAMS as DATACLASS_PARAMS,  # type: ignore
)

import CommonEnvironment
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

            assert field.name in self.TokenLookup, ("Missing item in TokenLookup", field.name)

        # Ensure that all the lookup values are not None
        for k, v in self.TokenLookup.items():
            assert v is not None, k

        YamlRepr.ObjectReprImplBase.__init__(
            self,
            TokenLookup=None,
            **custom_display_funcs,
        )
