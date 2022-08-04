# ----------------------------------------------------------------------
# |
# |  Namespaces.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-20 16:51:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains various objects that help when working with namespaces"""

import os

from typing import Dict, Generator, List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ..ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo
    from ..ParserInfos.Statements.StatementParserInfo import ParserInfo, ScopeFlag

    from ..ParserInfos.Traits.NamedTrait import NamedTrait


# ----------------------------------------------------------------------
class Namespace(Interface.Interface, ObjectReprImplBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: Optional[str],
    ):
        super(Namespace, self).__init__()

        # Make this a private attribute with a corresponding property so that derived classes
        # can override it if necessary.
        self._name                          = name

        self.parent: Optional[Namespace]    = None

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
        assert self._name is not None
        self._name = new_name_value

    # ----------------------------------------------------------------------
    def HasChildren(self) -> bool:
        return bool(self._children)

    # ----------------------------------------------------------------------
    def AddChild(
        self,
        namespace: "Namespace",
    ) -> None:
        assert namespace.name is not None

        existing_value = self._children.get(namespace.name, None)

        if isinstance(existing_value, list):
            existing_value.append(namespace)
        else:
            if existing_value is None:
                value = namespace
            else:
                value = [existing_value, namespace]

            self._children[namespace.name] = value

        assert namespace.parent is None, namespace.parent
        object.__setattr__(namespace, "parent", self)

    # ----------------------------------------------------------------------
    def MoveChild(
        self,
        namespace: "Namespace",
    ) -> None:
        assert namespace.parent is not None
        object.__setattr__(namespace, "parent", None)

        self.AddChild(namespace)

    # ----------------------------------------------------------------------
    def ReplaceChild(
        self,
        namespace: "Namespace",
        *,
        is_move: bool=False,
    ) -> None:
        assert namespace.name is not None
        self._children.pop(namespace.name, None)

        if is_move:
            self.MoveChild(namespace)
        else:
            self.AddChild(namespace)

    # ----------------------------------------------------------------------
    def RemoveChild(
        self,
        namespace,
    ) -> None:
        del self._children[namespace.name]

    # ----------------------------------------------------------------------
    def GetChild(
        self,
        name: str,
    ) -> Union[None, "Namespace", List["Namespace"]]:
        return self._children.get(name, None)

    # ----------------------------------------------------------------------
    def EnumChildren(self) -> Generator[
        Union["Namespace", List["Namespace"]],
        None,
        None,
    ]:
        yield from self._children.values()

    # ----------------------------------------------------------------------
    def GetOrAddChild(
        self,
        name: str,
    ) -> Union["Namespace", List["Namespace"]]:
        result = self.GetChild(name)
        if result is not None:
            return result

        new_namespace = Namespace(name)
        self.AddChild(new_namespace)

        return new_namespace

    # ----------------------------------------------------------------------
    def Flatten(self) -> "Namespace":
        result = Namespace("{} (Flattened)".format(self.name))

        for value in self._FlattenImpl():
            assert value.name is not None

            existing_value = result.GetChild(value.name)
            if existing_value is not None:
                assert isinstance(existing_value, ParsedNamespace), existing_value
                assert isinstance(value, ParsedNamespace), value

                if existing_value.parser_info != value.parser_info:
                    if isinstance(existing_value, ImportNamespace):
                        if not isinstance(value, ImportNamespace):
                            result.ReplaceChild(
                                value,
                                is_move=True,
                            )
                        elif isinstance(value, ImportNamespace):
                            # Nothing to do here
                            pass
                        else:
                            assert False, (existing_value, value)  # pragma: no cover

                continue

            result.MoveChild(value)

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
    # TODO: Create a wrapper, where the actual namespace can only be used within a generator, where
    #       any exceptions are decorated with all of the imports. Should be impossible to use the
    #       underlying namespace outside of that generator.

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ParserInfo,
        scope_flag: ScopeFlag,
    ):
        assert isinstance(parser_info, NamedTrait), parser_info

        super(ParsedNamespace, self).__init__(parser_info.name)

        self.parser_info                    = parser_info
        self.scope_flag                     = scope_flag

    # ----------------------------------------------------------------------
    @property
    def name(self) -> str:
        name = super(ParsedNamespace, self).name

        assert name is not None
        return name

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
class ImportNamespace(ParsedNamespace):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ImportStatementParserInfo,
        scope_flag: ScopeFlag,
        imported_namespace: ParsedNamespace,
    ):
        super(ImportNamespace, self).__init__(parser_info, scope_flag)

        self.imported_namespace             = imported_namespace

    # ----------------------------------------------------------------------
    @Interface.override
    def EnumImports(self) -> Generator[ParsedNamespace, None, None]:
        yield self
        yield from self.imported_namespace.EnumImports()
