# ----------------------------------------------------------------------
# |
# |  NamespaceVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 12:52:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NamespaceVisitor object"""

import os

from typing import Callable, Dict, List, Optional

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Phrase import Phrase


# ----------------------------------------------------------------------
class NamespaceVisitor(object):
    """Object that organizes types according to namespaces"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Node(ObjectReprImplBase):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            phrase: Optional[Phrase],
        ):
            self.phrase                                                     = phrase
            self.namespaces: Dict[str, List["NamespaceVisitor.Node"]]       = {}
            self.unnamed: List["NamespaceVisitor.Node"]                     = []

            super(NamespaceVisitor.Node, self).__init__()

    # ----------------------------------------------------------------------
    def __init__(self):
        self._node_stack = [NamespaceVisitor.Node(None)]

    # ----------------------------------------------------------------------
    @property
    def root(self) -> Dict[str, List["NamespaceVisitor.Node"]]:
        assert len(self._node_stack) == 1, self._node_stack
        assert self._node_stack[0].phrase is None

        return self._node_stack[0].namespaces

    # ----------------------------------------------------------------------
    def __getattr__(self, attr) -> Callable[[], None]:
        return lambda *args, **kwargs: None

    # ----------------------------------------------------------------------
    def OnEnterScope(self, phrase):
        if not phrase.has_children__:
            return

        new_node = NamespaceVisitor.Node(phrase)

        name = getattr(phrase, "name", None)
        if name is not None:
            self._node_stack[-1].namespaces.setdefault(name, []).append(new_node)
        else:
            self._node_stack[-1].unnamed.append(new_node)

        self._node_stack.append(new_node)

    # ----------------------------------------------------------------------
    def OnExitScope(self, phrase):
        assert self._node_stack, phrase
        self._node_stack.pop()
        assert self._node_stack, phrase

    # TODO: Aliases
    # TODO: Compile-time if statements should populate parent namespace
