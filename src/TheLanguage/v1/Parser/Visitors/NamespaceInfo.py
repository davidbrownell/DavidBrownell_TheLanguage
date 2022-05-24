# ----------------------------------------------------------------------
# |
# |  NamespaceInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-06 09:28:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NamespaceInfo object"""

import os

from collections import OrderedDict
from typing import Any, Callable, cast, Dict, List, Optional, Union

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ..ParserInfos.ParserInfo import ParserInfo

    from ..ParserInfos.Statements.StatementParserInfo import (
        NamedStatementTrait,
        ScopeFlag,
        StatementParserInfo,
    )

    from ..ParserInfos.Statements.FuncDefinitionStatementParserInfo import OperatorType as FuncOperatorType
    from ..ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodType as SpecialMethodType


# ----------------------------------------------------------------------
class NamespaceInfo(ObjectReprImplBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parent: Optional["NamespaceInfo"],
        children: Optional[Dict[str, "NamespaceInfo"]]=None,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        self.parent                         = parent
        self.children                       = children or OrderedDict()

        super(NamespaceInfo, self).__init__(
            parent=None,
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    def GetOrAddChild(
        self,
        name: str,
    ) -> "NamespaceInfo":
        namespace = self.children.get(name, None)
        if namespace is None:
            namespace = NamespaceInfo(self)
            self.children[name] = namespace

        return namespace

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        key: str,
        namespace: "NamespaceInfo",
    ) -> None:
        assert key not in self.children, key

        object.__setattr__(namespace, "parent", self)
        self.children[key] = namespace

    # ----------------------------------------------------------------------
    def Accept(self, visitor, *args, **kwargs):
        for child in self.children.values():
            child.Accept(visitor, *args, **kwargs)


# ----------------------------------------------------------------------
class ParsedNamespaceInfo(NamespaceInfo):
    # ----------------------------------------------------------------------
    ChildrenType                            = Dict[
        Union[
            str,
            FuncOperatorType,
            SpecialMethodType,
        ],
        Union[
            "ParsedNamespaceInfo",
            List["ParsedNamespaceInfo"],
        ]
    ]

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parent: Optional[NamespaceInfo],
        scope_flag: ScopeFlag,
        parser_info: ParserInfo,
        children: Optional[ChildrenType]=None,
        visibility: Optional[VisibilityModifier]=None,
    ):
        assert isinstance(parser_info, NamedStatementTrait)

        super(ParsedNamespaceInfo, self).__init__(
            parent,
            children=None,
        )

        self.scope_flag                     = scope_flag
        self.parser_info                    = parser_info
        self.visibility                     = visibility or parser_info.visibility

        self.children                       = children or OrderedDict()

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        child: "ParsedNamespaceInfo",
    ) -> None:
        assert isinstance(child.parser_info, NamedStatementTrait)

        existing_value = self.children.get(child.parser_info.name, None)

        if isinstance(existing_value, list):
            existing_value.append(child)

            value = existing_value
        else:
            if existing_value is None:
                value = child
            else:
                value = [existing_value, child]

            self.children[child.parser_info.name] = value

        object.__setattr__(child, "parent", self)

        assert (
            not isinstance(value, list)
            or all(
                isinstance(v.parser_info, NamedStatementTrait) and v.parser_info.allow_name_to_be_duplicated__
                for v in value
            )
        )

    # ----------------------------------------------------------------------
    def Accept(self, visitor):
        for child in self.children.values():
            if isinstance(child, list):
                for child_item in child:
                    cast(StatementParserInfo, child_item.parser_info).Accept(visitor)
            else:
                cast(StatementParserInfo, child.parser_info).Accept(visitor)
