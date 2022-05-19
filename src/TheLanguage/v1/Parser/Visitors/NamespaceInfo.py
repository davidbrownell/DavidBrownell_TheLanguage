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
from typing import Any, Callable, Dict, List, Optional, Union

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfos.Statements.StatementParserInfo import ParserInfo, ScopeFlag
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
    def Accept(self, visitor, *args, **kwargs):
        for child in self.children.values():
            child.Accept(visitor, *args, **kwargs)


# ----------------------------------------------------------------------
class ParsedNamespaceInfo(NamespaceInfo):
    # ----------------------------------------------------------------------
    ChildrenType                            = Dict[
        Union[
            None,
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
    ):
        super(ParsedNamespaceInfo, self).__init__(
            parent,
            children=None,
            parser_info=type,
            introduces_new_namespace_scope=None,
        )

        self.scope_flag                     = scope_flag
        self.parser_info                    = parser_info
        self.children                       = children or OrderedDict()
        self.introduces_new_namespace_scope = scope_flag == ScopeFlag.Class or scope_flag == ScopeFlag.Function

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        name: Optional[str],
        child: "ParsedNamespaceInfo",
    ) -> None:
        existing_value = self.children.get(name, None)

        if isinstance(existing_value, list):
            existing_value.append(child)
        else:
            if existing_value is None:
                value = child
            else:
                value = [existing_value, child]

            self.children[name] = value

    # ----------------------------------------------------------------------
    def AugmentChildren(
        self,
        source_children: ChildrenType,
    ) -> None:
        for source_key, source_value in source_children.items():
            existing_value = self.children.get(source_key, None)

            if isinstance(existing_value, list):
                if isinstance(source_value, list):
                    existing_value.extend(source_value)
                else:
                    existing_value.append(source_value)

            else:
                if existing_value is None:
                    value = source_value
                elif isinstance(source_value, list):
                    value = [existing_value] + source_value
                else:
                    value = [existing_value, source_value]

                self.children[source_key] = value

    # ----------------------------------------------------------------------
    def Accept(self, visitor):
        for child in self.children.values():
            if isinstance(child, list):
                for child_item in child:
                    child_item.parser_info.Accept(visitor)
            else:
                child.parser_info.Accept(visitor)

    # ----------------------------------------------------------------------
    def GetScopedNamespaceInfo(
        self,
        name: str,
    ) -> Union[
        None,
        "ParsedNamespaceInfo",
        List["ParsedNamespaceInfo"],
    ]:
        namespace = self

        while isinstance(namespace, ParsedNamespaceInfo):
            potential_child = namespace.children.get(name, None)
            if potential_child is not None:
                return potential_child

            if namespace.introduces_new_namespace_scope:
                break

            namespace = namespace.parent

        return None
