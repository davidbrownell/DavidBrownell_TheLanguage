# ----------------------------------------------------------------------
# |
# |  Namespaces.py
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
"""Contains various namespaces types, each of which have information used to lookup type names"""

import os

from typing import Dict, Generator, List, Optional, Tuple, TYPE_CHECKING, Union

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

    from ..ParserInfos.ParserInfo import ParserInfo

    from ..ParserInfos.Traits.NamedTrait import NamedTrait

    if TYPE_CHECKING:
        from ..ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo  # pylint: disable=unused-import
        from ..ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
        from ..ParserInfos.Statements.StatementParserInfo import ScopeFlag


# ----------------------------------------------------------------------
class Namespace(ObjectReprImplBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: Optional[str],
        parent: Optional["Namespace"],
    ):
        super(Namespace, self).__init__()

        assert (
            (name is not None and parent is not None)
            or (name is None and parent is None)
        ), (name, parent)

        self._name                          = name
        self.parent                         = parent

        self._children: Dict[
            str,
            Union[Namespace, List[Namespace]],
        ]                                   = {}

    # ----------------------------------------------------------------------
    @property
    def name(self) -> Optional[str]:
        return self._name

    # ----------------------------------------------------------------------
    def OverrideName(
        self,
        new_name_value: str,
    ) -> None:
        self._name = new_name_value

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def AddChild(
        self,
        namespace: "Namespace",
    ) -> None:
        assert namespace.name is not None

        existing_value = self._children.get(namespace.name, None)

        if isinstance(existing_value, list):
            existing_value.append(namespace)

            value = existing_value
        else:
            if existing_value is None:
                value = namespace
            else:
                value = [existing_value, namespace]

            self._children[namespace.name] = value

        object.__setattr__(namespace, "parent", self)

        assert (
            not isinstance(value, list)
            or all(
                (
                    isinstance(v, ParsedNamespace)
                    and isinstance(v.parser_info, NamedTrait)
                    and v.parser_info.allow_name_to_be_duplicated__
                )
                for v in value
            )
        ), value

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def ReplaceChild(
        self,
        namespace: "Namespace",
    ) -> None:
        assert namespace.name is not None
        self._children.pop(namespace.name, None)

        self.AddChild(namespace)

    # ----------------------------------------------------------------------
    def HasChildren(self) -> bool:
        return bool(self._children)

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def GetChild(
        self,
        name: str,
    ) -> Union[None, "Namespace", List["Namespace"]]:
        return self._children.get(name, None)

    # ----------------------------------------------------------------------
    def GetOrAddChild(
        self,
        name: str,
    ) -> Union["Namespace", List["Namespace"]]:
        result = self.GetChild(name)
        if result is not None:
            return result

        new_namespace = Namespace(name, self)
        self.AddChild(new_namespace)

        return new_namespace

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumChildren(self) -> Generator[
        Union["Namespace", List["Namespace"]],
        None,
        None,
    ]:
        yield from self._children.values()

    # ----------------------------------------------------------------------
    def Flatten(self) -> "Namespace":
        result = Namespace("{} (Flattened)".format(self.name), self.parent)

        for value in self._FlattenImpl():
            assert value.name is not None

            existing_value = result.GetChild(value.name)
            if existing_value is not None:
                assert isinstance(existing_value, ParsedNamespace), existing_value
                assert isinstance(value, ParsedNamespace), value

                if existing_value.parser_info != value.parser_info:
                    if isinstance(existing_value, ImportNamespace):
                        # Replace the existing value with the actual value
                        if not isinstance(value, ImportNamespace):
                            result.ReplaceChild(value)
                    elif isinstance(value, ImportNamespace):
                        # Nothing to do here
                        pass
                    else:
                        assert False, (existing_value, value)  # pragma: no cover

                continue

            result.AddChild(value)

        return result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _FlattenImpl(self) -> Generator["ParsedNamespace", None, None]:
        for value in self._children.values():
            if isinstance(value, Namespace):
                yield from value._FlattenImpl()  # pylint: disable=protected-access


# ----------------------------------------------------------------------
class ParsedNamespace(Namespace):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ParserInfo,
        parent: Namespace,
        scope_flag: "ScopeFlag",
        ordered_id: int,
    ):
        assert isinstance(parser_info, NamedTrait), parser_info

        super(ParsedNamespace, self).__init__(parser_info.name, parent)

        self.parser_info                    = parser_info
        self.scope_flag                     = scope_flag
        self.ordered_id                     = ordered_id

    # ----------------------------------------------------------------------
    @property
    def name(self) -> str:
        name = super(ParsedNamespace, self).name

        assert name is not None
        return name

    # ----------------------------------------------------------------------
    @property
    @Interface.extensionmethod
    def visibility(self) -> VisibilityModifier:
        assert isinstance(self.parser_info, NamedTrait), self.parser_info
        return self.parser_info.visibility

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def EnumImports(self) -> Generator["ParsedNamespace", None, None]:
        yield self

    # ----------------------------------------------------------------------
    def ResolveImports(self) -> "ParsedNamespace":
        *_, last = self.EnumImports()
        return last

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _ShouldFlatten(
        value: "ParsedNamespace",
    ) -> bool:
        # Don't flatten things without a first-class name
        if not isinstance(value.parser_info, NamedTrait):
            return False

        if value.parser_info.visibility != VisibilityModifier.public:
            return False

        return True

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.override
    def _FlattenImpl(self) -> Generator["ParsedNamespace", None, None]:
        for value in self.EnumChildren():
            # Don't process lists of values, as they should never be part of a flattened namespace
            if not isinstance(value, Namespace):
                continue

            if isinstance(value, ParsedNamespace):
                if self.__class__._ShouldFlatten(value):  # pylint: disable=protected-access
                    yield value
            else:
                yield from value._FlattenImpl()  # pylint: disable=protected-access


# ----------------------------------------------------------------------
class ImportNamespace(ParsedNamespace):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: "ImportStatementParserInfo",
        parent: Namespace,
        scope_flag: "ScopeFlag",
        ordered_id: int,
        imported_namespace: ParsedNamespace,
    ):
        super(ImportNamespace, self).__init__(
            parser_info,
            parent,
            scope_flag,
            ordered_id,
        )

        self.imported_namespace             = imported_namespace

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumImports(self) -> Generator["ParsedNamespace", None, None]:
        yield self
        yield from self.imported_namespace.EnumImports()
