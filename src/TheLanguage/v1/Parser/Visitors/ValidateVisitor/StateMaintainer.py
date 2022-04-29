# ----------------------------------------------------------------------
# |
# |  StateMaintainer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-28 06:45:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StateMaintainer object"""

import os

from typing import cast, Dict, Generator, Generic, List, Optional, TypeVar, Union

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
T = TypeVar("T")

class StateMaintainer(Generic[T]):
    """Maintains state for named objects across scopes"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class DoesNotExist(object):
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        init_values: Optional[Dict[str, Union[T, List[T]]]]=None,
    ):
        initial_scope = {}

        for name, value_or_values in (init_values or {}).items():
            initial_scope[name] = value_or_values if isinstance(value_or_values, list) else [value_or_values, ]

        self._scopes: List[Dict[str, List[T]]]          = [initial_scope, ]

    # ----------------------------------------------------------------------
    def PushScope(self):
        self._scopes.append({})

    # ----------------------------------------------------------------------
    def PopScope(self):
        assert len(self._scopes) > 1
        self._scopes.pop()

    # ----------------------------------------------------------------------
    def EnumScopes(self) -> Generator[Dict[str, List[T]], None, None]:
        yield from reversed(self._scopes)

    # ----------------------------------------------------------------------
    def EnumItems(
        self,
        name: str,
    ) -> Generator[List[T], None, None]:
        for scope in self.EnumScopes():
            values = scope.get(name, None)
            if values is not None:
                yield values

    # ----------------------------------------------------------------------
    def EnumItem(
        self,
        name: str,
    ) -> Generator[T, None, None]:
        for items in self.EnumItems(name):
            assert len(items) == 1, items
            yield items[0]

    # ----------------------------------------------------------------------
    def HasItems(
        self,
        name: str,
    ) -> bool:
        for _ in self.EnumItems(name):
            return True

        return False

    # ----------------------------------------------------------------------
    def HasItem(
        self,
        name: str,
    ) -> bool:
        for _ in self.EnumItem(name):
            return True

        return False

    # ----------------------------------------------------------------------
    def GetItemsNoThrow(
        self,
        name: str,
    ) -> Union[
        List[T],
        "StateMaintainer.DoesNotExist",
    ]:
        for items in self.EnumItems(name):
            return items

        return self._does_not_exist

    # ----------------------------------------------------------------------
    def GetItems(
        self,
        name: str,
    ) -> List[T]:
        result = self.GetItemsNoThrow(name)
        assert result != self._does_not_exist

        return cast(List[T], result)

    # ----------------------------------------------------------------------
    def GetItemNoThrow(
        self,
        name: str,
    ) -> Union[
        T,
        "StateMaintainer.DoesNotExist",
    ]:
        for item in self.EnumItem(name):
            return item

        return self._does_not_exist

    # ----------------------------------------------------------------------
    def GetItem(
        self,
        name: str,
    ) -> T:
        result = self.GetItemNoThrow(name)
        assert result != self._does_not_exist

        return cast(T, result)

    # ----------------------------------------------------------------------
    def AddItem(
        self,
        name: str,
        value: T,
        ensure_unique: bool=True,
    ) -> "StateMaintainer[T]":
        scope = self._scopes[-1]

        if ensure_unique and name in scope:
            raise Exception("'{name}' is not unique".format(name))

        scope.setdefault(name, []).append(value)
        return self

    # ----------------------------------------------------------------------
    def CreateSnapshot(self) -> Dict[str, List[T]]:
        result = {}

        for scope in self.EnumScopes():
            for key, values in scope.items():
                if key in result:
                    continue

                result[key] = values

        return result

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _does_not_exist                         = DoesNotExist()
