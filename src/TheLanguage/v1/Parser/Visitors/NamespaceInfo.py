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
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ..ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ..ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo
    from ..ParserInfos.Statements.Traits.NamedStatementTrait import NamedStatementTrait

    from ..ParserInfos.Statements.FuncDefinitionStatementParserInfo import OperatorType as FuncOperatorType
    from ..ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodType as SpecialMethodType


# ----------------------------------------------------------------------
class NamespaceInfo(ObjectReprImplBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: Optional[str],
        parent: Optional["NamespaceInfo"],
        children: Optional[Dict[str, "NamespaceInfo"]]=None,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        assert (
            (name is not None and parent is not None)
            or (name is None and parent is None)
        ), (name, parent)

        self.name                                       = name
        self.parent                                     = parent
        self.children: Dict[str, NamespaceInfo]         = children or OrderedDict()

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
            namespace = NamespaceInfo(name, self)
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
    def Flatten(self) -> "NamespaceInfo":
        result = NamespaceInfo(None, None)

        for key, value in self._FlattenImpl():
            assert isinstance(value, ParsedNamespaceInfo), value

            existing_value = result.children.get(key, None)
            if existing_value is not None:
                assert isinstance(existing_value, ParsedNamespaceInfo), existing_value
                assert value.parser_info == existing_value.parser_info, (value.parser_info, existing_value.parser_info)
            else:
                result.children[key] = value

        return result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _FlattenImpl(self) -> Generator[Tuple[str, "ParsedNamespaceInfo"], None, None]:
        for value in self.children.values():
            yield from value._FlattenImpl()  # pylint: disable=protected-access


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
        parser_info: Union[
            StatementParserInfo,
            TemplateTypeParameterParserInfo,
        ],
        *,
        name: Optional[str]=None,
        visibility: Optional[VisibilityModifier]=None,
        children: Optional[ChildrenType]=None,
    ):
        if name is None:
            assert isinstance(parser_info, NamedStatementTrait)
            name = parser_info.name

        if visibility is None:
            assert isinstance(parser_info, NamedStatementTrait)
            visibility = parser_info.visibility

        if children is None:
            children = OrderedDict()

        super(ParsedNamespaceInfo, self).__init__(
            name,
            parent,
            children=None,
        )

        self.scope_flag                     = scope_flag
        self.parser_info                    = parser_info
        self.visibility                     = visibility

        self.children: ParsedNamespaceInfo.ChildrenType                     = children

        # Ordered children are those items that are only valid when they are introduced within the code.
        # For example, a type alias can only be used after it is defined. Compare this with a class
        # definition, which can be used as a base class before it is officially defined.
        self.ordered_children: ParsedNamespaceInfo.ChildrenType             = {}

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        child: "ParsedNamespaceInfo",
    ) -> None:
        assert child.name is not None
        assert isinstance(child.parser_info, (NamedStatementTrait, TemplateTypeParameterParserInfo))

        existing_value = self.children.get(child.name, None)

        if isinstance(existing_value, list):
            existing_value.append(child)

            value = existing_value
        else:
            if existing_value is None:
                value = child
            else:
                value = [existing_value, child]

            self.children[child.name] = value

        object.__setattr__(child, "parent", self)

        assert (
            not isinstance(value, list)
            or all(
                isinstance(v.parser_info, NamedStatementTrait) and v.parser_info.allow_name_to_be_duplicated__
                for v in value
            )
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _ShouldFlatten(
        key: str,
        value: "ParsedNamespaceInfo",
    ) -> bool:
        if not isinstance(key, str):
            return False

        # Don't return things without a first-class name, as they should never be a part of
        # a flattened namespace.
        if not isinstance(value.parser_info, NamedStatementTrait):
            return False

        if value.parser_info.visibility != VisibilityModifier.public:
            return False

        return True

    # ----------------------------------------------------------------------
    @Interface.override
    def _FlattenImpl(self) -> Generator[Tuple[str, "ParsedNamespaceInfo"], None, None]:
        for container in [self.children, self.ordered_children]:
            for key, value in container.items():
                # Don't process lists of values, as they should never be a part of a flattened namespace
                if not isinstance(value, NamespaceInfo):
                    continue

                if isinstance(value, ParsedNamespaceInfo):
                    if self.__class__._ShouldFlatten(key, value):  # pylint: disable=protected-access
                        yield key, value
                else:
                    yield from value._FlattenImpl()  # pylint: disable=protected-access
